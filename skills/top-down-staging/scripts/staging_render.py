#!/usr/bin/env python3
# /// script
# requires-python = ">=3.13"
# dependencies = ["manimgx==0.1.1", "numpy", "imageio-ffmpeg"]
# ///
"""
Top-down staging renderer: scene spec (JSON) -> animated top-down staging video (ManimGX).

Usage:
    uv run staging_render.py scene.json -o out.mp4 [--quality h|m|l] [--poster 1.0]

World coordinates are METRES on a top-down map: +x = right (east), +y = up (north, "into the scene").
Angles are map degrees, counter-clockwise from +x (E=0, N=90, W=180, S=270), or compass strings
("N","NE","E","SE","S","SW","W","NW"), or "towards:<name>" (a character, prop or "light").
"""
import argparse, json, math, os, shutil, subprocess, sys, tempfile, time
import imageio_ffmpeg
import numpy as np
from manimgx import *

COMPASS = {"E": 0, "NE": 45, "N": 90, "NW": 135, "W": 180, "SW": 225, "S": 270, "SE": 315}
SIZE_DIST_50MM = {  # camera-to-subject distance (m) for a given shot size on a 50mm lens
    "extreme wide": 16, "ews": 16, "wide": 9, "ws": 9, "establishing": 11, "full": 5, "fs": 5,
    "medium wide": 4, "mws": 4, "medium": 3, "ms": 3, "medium close-up": 2.0, "mcu": 2.0,
    "close-up": 1.4, "cu": 1.4, "extreme close-up": 0.8, "ecu": 0.8, "insert": 0.8, "ots": 1.6,
}
REL_OFFSETS = {  # camera placement relative to a character's facing (degrees added to facing)
    "front": 0, "front-left": 35, "front-right": -35, "left": 90, "right": -90,
    "behind": 180, "behind-left": 145, "behind-right": -145,
}
PALETTE = ["#F2A541", "#9CC5A1", "#B07CC6", "#6FB3E0", "#E07A6F", "#D9C36A", "#7FD1C1", "#C98BB9"]
CAM_C, AXIS_C, WARN_C, HL_C = "#E8EEF5", "#FFD84D", "#FF6B6B", "#FFB35C"

# frame regions (Manim units): map on the left, legend panel on the right
MAP_X, MAP_Y = (-6.95, 2.9), (-3.85, 3.0)
PANEL_LEFT, PANEL_RIGHT = 3.25, 6.95


# ---------------------------------------------------------------- geometry helpers
def v2(p):
    return np.array([float(p[0]), float(p[1])])


def unit(deg):
    return np.array([math.cos(math.radians(deg)), math.sin(math.radians(deg))])


def deg_of(vec):
    return math.degrees(math.atan2(vec[1], vec[0]))


def side_of(a, b, p):
    d, q = b - a, p - a
    c = d[0] * q[1] - d[1] * q[0]
    return 0 if abs(c) < 1e-9 else (1 if c > 0 else -1)


def reflect(p, a, b):
    d = (b - a) / np.linalg.norm(b - a)
    q = p - a
    proj = a + d * np.dot(q, d)
    return 2 * proj - p


def hfov(lens_mm):
    return 2 * math.degrees(math.atan(18.0 / float(lens_mm)))  # full-frame 36 mm width


# ---------------------------------------------------------------- spec resolution
class Spec:
    def __init__(self, raw):
        if not isinstance(raw, dict):
            raise ValueError("the scene spec must be a JSON object")
        self.raw = raw
        self.title = raw.get("title", "Top-down staging")
        self.ground = raw.get("ground", "#3A3D44")
        self.warnings = []
        self.chars = {}
        for i, c in enumerate(self._list(raw.get("characters", []), "characters")):
            if not isinstance(c, dict):
                raise ValueError(f"characters[{i}] must be an object")
            c = dict(c)
            if not isinstance(c.get("name"), str) or not c["name"]:
                raise ValueError(f"characters[{i}].name is required")
            if c["name"] in self.chars:
                raise ValueError(f"duplicate character name: {c['name']}")
            if "pos" not in c:
                raise ValueError(f"missing field: characters[{i}].pos")
            c["pos"] = v2(c["pos"])
            c.setdefault("color", PALETTE[i % len(PALETTE)])
            c["moves"] = self._list(c.get("moves", []), f"characters[{i}].moves")
            self.chars[c["name"]] = c
        self.props = self._list(raw.get("props", []), "props")
        for i, prop in enumerate(self.props):
            if not isinstance(prop, dict):
                raise ValueError(f"props[{i}] must be an object")
        if "lights" in raw:
            self.lights = self._list(raw["lights"], "lights")
        elif raw.get("light") is not None:
            self.lights = [raw["light"]]
        else:
            self.lights = []
        for i, light in enumerate(self.lights):
            if not isinstance(light, dict):
                raise ValueError(f"lights[{i}] must be an object")
            if "direction" not in light:
                raise ValueError(f"missing field: lights[{i}].direction")
            if "pos" in light:
                light["pos"] = self._coord(light["pos"], f"lights[{i}].pos")
        self.light = self.lights[0] if self.lights else None
        self.axis = raw.get("axis")
        self.eyelines = self._list(raw.get("eyelines", []), "eyelines")
        self.notes = self._list(raw.get("notes", []), "notes")
        raw_shots = self._list(raw.get("shots", []), "shots")
        self._move_states = {}
        for name, c in self.chars.items():
            for i, move in enumerate(c["moves"]):
                if not isinstance(move, dict):
                    raise ValueError(f"characters.{name}.moves[{i}] must be an object")
                if "to" not in move:
                    raise ValueError(f"missing field: characters.{name}.moves[{i}].to")
        for name, c in self.chars.items():
            for i in range(1, len(c["moves"]) + 1):
                self._resolve_move_position(name, i)
        for c in self.chars.values():
            c["facing_deg"] = self.angle(c.get("facing", "S"), c["pos"])
        for name, c in self.chars.items():
            facing = c["facing_deg"]
            for move in c["moves"]:
                end = move["pos"]
                previous = move["_path_points"][-2]
                direction = end - previous
                if "facing" in move:
                    facing = self.angle(move["facing"], end)
                elif np.linalg.norm(direction) > 1e-9:
                    facing = deg_of(direction)
                move["facing_deg"] = facing
            if c.get("turn"):
                if not isinstance(c["turn"], dict) or "to" not in c["turn"]:
                    raise ValueError(f"{c['name']}.turn must include a 'to' angle")
                c["turn_deg"] = self.angle(c["turn"]["to"], c["pos"])
        for i, light in enumerate(self.lights):
            self.angle(light["direction"], self.scene_center())
            if light.get("target") is not None:
                self.point(light["target"])
        for i, eyeline in enumerate(self.eyelines):
            if not isinstance(eyeline, dict):
                raise ValueError(f"eyelines[{i}] must be an object")
            for key in ("from", "to"):
                if key not in eyeline:
                    raise ValueError(f"missing field: eyelines[{i}].{key}")
                self.point(eyeline[key])
            self.character_name(eyeline["from"])
        if self.axis is not None:
            self._axis_points(self.axis, "axis")
        for i, shot in enumerate(raw_shots):
            if not isinstance(shot, dict):
                raise ValueError(f"shots[{i}] must be an object")
            if shot.get("axis") is not None:
                self._axis_points(shot["axis"], f"shots[{i}].axis")
        self.shots = self.resolve_shots(raw_shots)
        if self.axis:
            moving = [name for name in self.axis if name in self.chars and self.chars[name]["moves"]]
            if moving and not any(shot.get("axis") is not None for shot in raw_shots):
                for name in moving:
                    self.warnings.append(
                        f"axis is checked at starting positions; {name} moves — set a per-shot axis for shots after the move"
                    )

    @staticmethod
    def _list(value, field):
        if not isinstance(value, list):
            raise ValueError(f"{field} must be a list")
        return value

    @staticmethod
    def _coord(value, field="point"):
        try:
            point = v2(value)
        except (IndexError, TypeError, ValueError) as exc:
            raise ValueError(f"{field} must be a 2D point") from exc
        if point.shape != (2,) or not np.isfinite(point).all():
            raise ValueError(f"{field} must be a finite 2D point")
        return point

    def _move_reference(self, ref):
        if not isinstance(ref, str) or "@" not in ref:
            return None
        name, index = ref.rsplit("@", 1)
        if name not in self.chars:
            return None
        if not index.isdigit() or int(index) < 1:
            raise ValueError(f"unknown reference: {ref}")
        return name, int(index)

    def _resolve_move_position(self, name, index):
        if name not in self.chars or index < 1 or index > len(self.chars[name]["moves"]):
            raise ValueError(f"unknown reference: {name}@{index}")
        key = (name, index)
        state = self._move_states.get(key, 0)
        if state == 1:
            raise ValueError(f"cyclic move reference: {name}@{index}")
        move = self.chars[name]["moves"][index - 1]
        if state == 2:
            return move["pos"]
        self._move_states[key] = 1
        previous = self.chars[name]["pos"] if index == 1 else self._resolve_move_position(name, index - 1)
        via = self._list(move.get("via", []), f"characters.{name}.moves[{index - 1}].via")
        via = [self._coord(point, f"characters.{name}.moves[{index - 1}].via") for point in via]
        destination = self.point(move["to"])
        move["_path_points"] = [previous, *via, destination]
        move["pos"] = self._coord(destination, f"characters.{name}.moves[{index - 1}].to")
        self._move_states[key] = 2
        return move["pos"]

    def point(self, ref):
        if isinstance(ref, (list, tuple, np.ndarray)) and len(ref) == 2 and all(
            isinstance(value, (int, float, np.number)) for value in ref
        ):
            return self._coord(ref)
        if isinstance(ref, (list, tuple)):
            return np.mean([self.point(r) for r in ref], axis=0)
        move_ref = self._move_reference(ref)
        if move_ref:
            return self._resolve_move_position(*move_ref)
        if ref in self.chars:
            return self.chars[ref]["pos"]
        for p in self.props:
            if p.get("name") == ref:
                return self._coord(p["pos"]) if "pos" in p else np.mean(
                    [self._coord(q) for q in p["points"]], axis=0
                )
        if ref == "light" and self.light:
            return self.scene_center() + unit(self.light_dir()) * 1000
        for light in self.lights:
            if light.get("name") == ref and "pos" in light:
                return light["pos"]
        raise ValueError(f"unknown reference: {ref}")

    def angle(self, a, origin):
        if isinstance(a, (int, float)):
            if math.isfinite(float(a)):
                return float(a)
            raise ValueError(f"bad angle: {a}")
        if isinstance(a, str) and a.upper() in COMPASS:
            return float(COMPASS[a.upper()])
        if isinstance(a, str) and a.startswith("towards:"):
            ref = a.split(":", 1)[1]
            if not ref:
                raise ValueError(f"bad angle: {a}")
            return deg_of(self.point(ref) - origin)
        raise ValueError(f"bad angle: {a}")

    def light_dir(self):
        return self.angle(self.light["direction"], self.scene_center())

    def character_name(self, ref):
        move_ref = self._move_reference(ref)
        if move_ref:
            return move_ref[0]
        if ref in self.chars:
            return ref
        raise ValueError(f"unknown character reference: {ref}")

    def facing_for(self, ref, turned=False):
        move_ref = self._move_reference(ref)
        if move_ref:
            name, index = move_ref
            if index > len(self.chars[name]["moves"]):
                raise ValueError(f"unknown reference: {ref}")
            return self.chars[name]["moves"][index - 1]["facing_deg"]
        if ref not in self.chars:
            raise ValueError(f"unknown character reference: {ref}")
        c = self.chars[ref]
        return c.get("turn_deg", c["facing_deg"]) if turned else c["facing_deg"]

    def scene_center(self):
        pts = [c["pos"] for c in self.chars.values()] or [np.zeros(2)]
        return np.mean(pts, axis=0)

    def _axis_points(self, refs, field="axis"):
        if not isinstance(refs, (list, tuple)) or len(refs) != 2:
            raise ValueError(f"{field} must contain exactly two references")
        a, b = self.point(refs[0]), self.point(refs[1])
        if np.linalg.norm(b - a) < 1e-9:
            raise ValueError(f"{field} references must not resolve to the same point")
        return a, b

    def group_spread(self, names):
        pts = [self.point(n) for n in names]
        if len(pts) < 2:
            return 0.0
        return max(np.linalg.norm(p - q) for p in pts for q in pts)

    # -- shots
    def resolve_shots(self, shots):
        out = []
        ref_sides = {}
        for i, s in enumerate(shots):
            s = dict(s)
            s["n"] = s.get("n", i + 1)
            lens = float(s.get("lens", 35))
            if not math.isfinite(lens) or lens <= 0:
                raise ValueError(f"shot {s['n']} has a bad lens: {lens}")
            s["lens"] = lens
            size = str(s.get("size", "medium")).lower()
            tgt_ref = s.get("target")
            if tgt_ref is None:
                if self.chars:
                    tgt_ref = list(self.chars.keys())
                elif self.props:
                    tgt_ref = self.props[0].get("name")
                elif self.lights:
                    tgt_ref = "light"
                else:
                    raise ValueError(f"missing field: shots[{i}].target")
            names = tgt_ref if isinstance(tgt_ref, (list, tuple)) and tgt_ref and all(
                isinstance(name, str) for name in tgt_ref
            ) else None
            target = self.point(tgt_ref)
            dist = SIZE_DIST_50MM.get(size, 3) * lens / 50.0
            if names and len(names) > 1:  # make sure a group fits in frame
                need = (self.group_spread(names) / 2) / math.tan(math.radians(hfov(lens) / 2)) * 1.35
                dist = max(dist, need)
            explicit = "pos" in s
            if explicit:
                pos = self._coord(s["pos"], f"shot {s['n']}.pos")
            elif "over_shoulder" in s:
                self.character_name(s["over_shoulder"])
                o = self.point(s["over_shoulder"])
                look = target - o
                if np.linalg.norm(look) < 1e-9:
                    raise ValueError(f"shot {s['n']} has a target at the over-shoulder position")
                look = look / np.linalg.norm(look)
                perp = np.array([-look[1], look[0]])  # the character's left, seen along the look
                if str(s.get("shoulder", "right")).lower() == "right":
                    perp = -perp
                pos = o - look * 1.0 + perp * 0.45
                s["_ots_perp"] = perp
            elif "from" in s:
                frm = s["from"]
                if isinstance(frm, str) and frm.lower() in REL_OFFSETS:
                    anchor = s.get("relative_to") or (names[0] if names else None) or tgt_ref
                    fac = self.facing_for(anchor, turned=s.get("relative_facing") == "turned")
                    pos = target + unit(fac + REL_OFFSETS[frm.lower()]) * dist
                else:  # compass / absolute direction from target
                    pos = target + unit(self.angle(frm, target)) * dist
            else:
                prev = out[0]["pos"] if out else None
                dirv = (prev - target) if prev is not None else unit(270)
                norm = np.linalg.norm(dirv)
                pos = target + (dirv / norm if norm > 1e-9 else unit(270)) * dist
            # 180-degree rule
            crossed = False
            axis_refs = s.get("axis", self.axis)
            axis_ab = self._axis_points(axis_refs, f"shot {s['n']} axis") if axis_refs else None
            axis_key = tuple(sorted(axis_refs)) if axis_refs else None
            axis_label = "–".join(str(ref) for ref in axis_refs) if axis_refs else None
            if axis_ab is not None and not s.get("ignore_axis"):
                axis_ab = self._axis_points(axis_key)
                sd = side_of(axis_ab[0], axis_ab[1], pos)
                ref_side = ref_sides.get(axis_key)
                if ref_side is None and sd != 0:
                    ref_sides[axis_key] = sd
                elif sd != 0 and sd != ref_side:
                    if explicit or s.get("allow_cross"):
                        crossed = True
                        if not s.get("allow_cross"):
                            self.warnings.append(f"shot {s['n']} crosses the 180° axis {axis_label}")
                    else:
                        pos = reflect(pos, *axis_ab)
                        self.warnings.append(
                            f"shot {s['n']} auto-mirrored to stay on one side of the 180° axis {axis_label}"
                        )
            if "dir" in s:
                d = self.angle(s["dir"], pos)
            else:
                d = deg_of(target - pos)
            s.update(pos=pos, dir=d, target_pt=target, dist=float(np.linalg.norm(target - pos)),
                     fov=hfov(lens), crossed=crossed, axis_refs=axis_refs)
            out.append(s)
        return out


# ---------------------------------------------------------------- the scene
SPEC = None
if os.environ.get("STAGING_SPEC"):
    with open(os.environ["STAGING_SPEC"]) as f:
        SPEC = Spec(json.load(f))


def T(text, size=18, color=WHITE, weight=MEDIUM):
    return Text(str(text), font="Noto Sans", font_size=size, color=color, weight=weight)


class StagingScene(Scene):
    def construct(self):
        S = SPEC
        self.camera.background_color = "#0E1319"

        # ---- fit the map on the scene core; far cameras get clamped to the map edge later
        pts = [c["pos"] for c in S.chars.values()]
        for c in S.chars.values():
            for move in c["moves"]:
                pts.extend(move["_path_points"])
        for p in S.props:
            if p.get("type") == "rect":
                w, h = p.get("size", [1, 1])
                c = v2(p["pos"])
                pts += [c + np.array([w / 2, h / 2]), c - np.array([w / 2, h / 2])]
            elif p.get("type") == "circle":
                c, r = v2(p["pos"]), float(p.get("radius", 1))
                pts += [c + r, c - r]
        for light in S.lights:
            if light.get("pos") is not None:
                pts.append(v2(light["pos"]))
        for s_ in S.shots:  # near cameras belong to the core
            if s_["dist"] <= 3.5:
                pts.append(s_["pos"])
        pts = np.array(pts)
        lo, hi = pts.min(axis=0) - 1.2, pts.max(axis=0) + 1.2
        span = np.maximum(hi - lo, 1e-3)
        scale = 0.95 * min((MAP_X[1] - MAP_X[0]) / span[0], (MAP_Y[1] - MAP_Y[0]) / span[1])
        mid_w, mid_m = (lo + hi) / 2, np.array([sum(MAP_X) / 2, sum(MAP_Y) / 2])

        def M(p):
            q = (v2(p) - mid_w) * scale + mid_m
            return np.array([q[0], q[1], 0.0])

        def clamp_to_map(p_map, origin_map):
            x0, x1 = MAP_X[0] + 0.35, PANEL_LEFT - 0.45
            y0, y1 = MAP_Y[0] + 0.8, MAP_Y[1] - 0.35
            if x0 <= p_map[0] <= x1 and y0 <= p_map[1] <= y1:
                return p_map, False
            d = p_map[:2] - origin_map[:2]
            ts = []
            for lo_, hi_, k in ((x0, x1, 0), (y0, y1, 1)):
                if abs(d[k]) > 1e-9:
                    ts.append(((hi_ if d[k] > 0 else lo_) - origin_map[k]) / d[k])
            t = max(0.0, min(ts)) if ts else 1.0
            q = origin_map[:2] + d * t
            return np.array([q[0], q[1], 0.0]), True

        # ---- ground + props
        ground = Rectangle(width=14.6, height=8.4, fill_color=S.ground, fill_opacity=1, stroke_width=0)
        title = T(S.title, 26).to_edge(UP, buff=0.22)
        title_bg = SurroundingRectangle(title, buff=0.12, fill_color="#0E1319", fill_opacity=0.75,
                                        stroke_width=0, corner_radius=0.1)
        title_bg.set_z_index(8); title.set_z_index(9)
        north = VGroup(Arrow([6.75, 2.85, 0], [6.75, 3.5, 0], buff=0, color=WHITE, stroke_width=3),
                       T(S.raw.get("north_label", "into the scene"), 13).move_to([5.95, 3.15, 0]))
        prop_mobs = []
        for p in S.props:
            col = p.get("color", "#555A5F")
            t = p.get("type", "rect")
            if t == "band":
                a, b = v2(p["points"][0]), v2(p["points"][1])
                d = (b - a) / np.linalg.norm(b - a)
                n = np.array([-d[1], d[0]]) * p.get("width", 1.0) / 2
                ext = d * 100
                poly = Polygon(M(a - ext + n), M(b + ext + n), M(b + ext - n), M(a - ext - n),
                               fill_color=col, fill_opacity=1, stroke_width=0)
                prop_mobs.append(poly)
                if p.get("label"):
                    # put the label where the band is inside the map, near its left side
                    best = None
                    for t in np.linspace(-3, 4, 141):
                        q = M(a + (b - a) * t)
                        if MAP_X[0] + 1.4 <= q[0] <= PANEL_LEFT - 1.4 and MAP_Y[0] + 0.3 <= q[1] <= MAP_Y[1] - 0.3:
                            best = q
                            break
                    if best is not None:
                        prop_mobs.append(T(p["label"], 15, "#20262C" if p.get("dark_label") else "#E5E5E0")
                                         .move_to(best).rotate(math.radians(deg_of(d))))
            elif t == "circle":
                r = float(p.get("radius", 1)) * scale
                m = Circle(radius=r, fill_color=col, fill_opacity=0.9, stroke_color=p.get("stroke", "#3F7A50"),
                           stroke_width=2).move_to(M(p["pos"]))
                prop_mobs.append(m)
                if p.get("label"):
                    prop_mobs.append(T(p["label"], 16, "#DDE8DF").move_to(M(p["pos"])))
            else:
                w, h = p.get("size", [1, 1])
                m = Rectangle(width=w * scale, height=h * scale, fill_color=col, fill_opacity=1,
                              stroke_color=p.get("stroke", col), stroke_width=1.5) \
                    .rotate(math.radians(p.get("rotation", 0))).move_to(M(p["pos"]))
                prop_mobs.append(m)
                if p.get("label"):
                    lbl = T(p["label"], 14, p.get("label_color", "#DDE8DF"))
                    lbl.move_to(M(p["pos"]) + np.array([0, -(h * scale) / 2 - 0.2, 0]))
                    prop_mobs.append(lbl)
        self.play(FadeIn(ground), FadeIn(title_bg), FadeIn(title), run_time=0.4)
        self.play(*[FadeIn(m) for m in prop_mobs], FadeIn(north), run_time=0.9)

        # ---- lights
        multiple_lights = len(S.lights) > 1
        light_label_centers = []
        light_icon_centers = []
        for light_index, light in enumerate(S.lights, start=1):
            ld = S.angle(light["direction"], S.scene_center())
            u = unit(ld)
            org = M(S.point(light["target"]))[:2] if light.get("target") else mid_m
            xmax, xmin = PANEL_LEFT - 0.55, MAP_X[0] + 0.5
            ymax, ymin = MAP_Y[1] - 0.45, MAP_Y[0] + 0.45
            cand = []
            if u[0] > 1e-6: cand.append((xmax - org[0]) / u[0])
            if u[0] < -1e-6: cand.append((xmin - org[0]) / u[0])
            if u[1] > 1e-6: cand.append((ymax - org[1]) / u[1])
            if u[1] < -1e-6: cand.append((ymin - org[1]) / u[1])
            tt = max(0.8, min(cand)) if cand else 3.0
            lp = np.array([org[0] + u[0] * tt, org[1] + u[1] * tt, 0])
            if light.get("pos") is not None:
                lp = M(light["pos"])
            kind = light.get("type", "sun")
            if kind == "sun":
                icon = VGroup(*[Line(ORIGIN, 0.42 * np.array([*unit(a), 0]), color="#FFC93C", stroke_width=3)
                                for a in range(0, 360, 30)],
                              Circle(radius=0.24, fill_color="#FFD84D", fill_opacity=1, stroke_width=0))
            elif multiple_lights and kind == "lamp":
                icon = VGroup(
                    Circle(radius=0.2, fill_color="#FFE9A8", fill_opacity=1, stroke_width=0),
                    Circle(radius=0.26, fill_opacity=0, stroke_color="#FFE9A8", stroke_width=1.5),
                )
            else:
                icon = VGroup(Square(0.45, fill_color="#FFE9A8", fill_opacity=1, stroke_width=0))
            icon.move_to(lp)
            light_icon_centers.append(lp)
            light_mobs = [icon]
            tgt = light.get("target")
            if tgt:
                light_mobs.append(DashedLine(lp, M(S.point(tgt)), color="#FFC93C", stroke_width=2.5,
                                             dash_length=0.12).set_opacity(0.6))
            if multiple_lights:
                tag = T(f"L{light_index}", 12, "#FFE9A8")
                tag_radius = math.hypot(tag.width, tag.height) / 2
                directions = [np.array([x, y, 0]) for x, y in (
                    (1, 0), (-1, 0), (0, 1), (0, -1),
                    (1, 1), (1, -1), (-1, 1), (-1, -1),
                )]
                directions = [direction / np.linalg.norm(direction) for direction in directions]
                tag_distance = 0.34 + tag_radius
                tag_candidates = [lp + direction * tag_distance for direction in directions]
                left = MAP_X[0] + tag.width / 2 + 0.12
                right = min(MAP_X[1] - 0.12, PANEL_LEFT - 0.15) - tag.width / 2
                bottom = MAP_Y[0] + tag.height / 2 + 0.12
                top = MAP_Y[1] - tag.height / 2 - 0.12

                def tag_penalty(center):
                    penalty = max(0, left - center[0]) ** 2
                    penalty += max(0, center[0] - right) ** 2
                    penalty += max(0, bottom - center[1]) ** 2
                    penalty += max(0, center[1] - top) ** 2
                    for other in light_icon_centers[:-1]:
                        penalty += max(0, 0.46 + tag_radius - np.linalg.norm(center[:2] - other[:2])) ** 2
                    for other in light_label_centers:
                        penalty += max(0, tag_radius + other[1] + 0.1
                                       - np.linalg.norm(center[:2] - other[0][:2])) ** 2
                    return penalty

                tag_center = min(tag_candidates, key=tag_penalty).copy()
                tag_center[0] = np.clip(tag_center[0], left, right)
                tag_center[1] = np.clip(tag_center[1], bottom, top)
                tag.move_to(tag_center)
                tag_bg = SurroundingRectangle(tag, buff=0.04, color="#20262C",
                                              fill_color="#20262C", fill_opacity=0.9,
                                              stroke_width=0)
                light_label_centers.append((tag_center, tag_radius))
                light_mobs.extend([tag_bg, tag])
            self.play(*[FadeIn(m) if not isinstance(m, DashedLine) else Create(m) for m in light_mobs], run_time=0.6)

        # ---- characters
        char_mobs, turn_mobs = [], []
        for c in S.chars.values():
            p = M(c["pos"])
            dot = Dot(p, radius=0.17, color=c["color"])
            ring = Circle(radius=0.17, color=BLACK, stroke_width=2).move_to(p)
            arr = Arrow(p, p + 0.62 * np.array([*unit(c["facing_deg"]), 0]), buff=0.12, color=c["color"],
                        stroke_width=4, max_tip_length_to_length_ratio=0.45)
            label = c["name"] + (f" · {c['posture']}" if c.get("posture") else "")
            lbl = T(label, 20, c["color"]).move_to(p + np.array([0, 0.48, 0]))
            g = VGroup(dot, ring, arr, lbl)
            g.set_z_index(3)
            char_mobs.append(g)
            if "turn_deg" in c:
                delta = ((c["turn_deg"] - c["facing_deg"] + 180) % 360) - 180
                arc = Arc(radius=0.62, start_angle=math.radians(c["facing_deg"]), angle=math.radians(delta),
                          color=c["color"], stroke_width=3).move_arc_center_to(p).add_tip(tip_length=0.14)
                turn_mobs.append(arc)
        self.play(LaggedStart(*[FadeIn(m, scale=1.3) for m in char_mobs], lag_ratio=0.25), run_time=1.0)
        if turn_mobs:
            self.play(*[Create(m) for m in turn_mobs], run_time=0.5)

        # ---- character movement
        move_label_obstacles = [M(c["pos"]) for c in S.chars.values()]
        move_label_obstacles.extend(M(move["pos"]) for c in S.chars.values() for move in c["moves"])
        move_label_obstacles.extend(M(light["pos"]) for light in S.lights if light.get("pos") is not None)
        move_label_obstacles.extend(M(shot["pos"]) for shot in S.shots)
        prop_obstacles = []
        for prop in S.props:
            if "pos" not in prop:
                continue
            if prop.get("type") == "rect":
                w, h = prop.get("size", [1, 1])
                radius = 0.5 * math.hypot(float(w), float(h)) * scale
            elif prop.get("type") == "circle":
                radius = float(prop.get("radius", 1)) * scale
            else:
                radius = 0.25 * scale
            prop_obstacles.append((M(prop["pos"]), radius))
        axis_obstacles = []
        axis_refs_to_draw = [S.axis] + [shot.get("axis_refs") for shot in S.shots]
        for refs in axis_refs_to_draw:
            if not refs:
                continue
            a, b = (M(point) for point in S._axis_points(refs))
            direction = (b - a) / np.linalg.norm(b - a)
            axis_obstacles.append((a - direction * 1.4, b + direction * 1.4))
        move_path_obstacles = [
            (M(a), M(b))
            for character in S.chars.values()
            for move in character["moves"]
            for a, b in zip(move["_path_points"], move["_path_points"][1:])
            if np.linalg.norm(b - a) > 1e-9
        ]
        move_label_centers = []

        def segment_distance(point, start, end):
            delta = end - start
            length_sq = float(np.dot(delta, delta))
            if length_sq < 1e-9:
                return float(np.linalg.norm(point - start))
            t = np.clip(np.dot(point - start, delta) / length_sq, 0, 1)
            return float(np.linalg.norm(point - (start + t * delta)))

        for c in S.chars.values():
            for i, move in enumerate(c["moves"], start=1):
                points = move["_path_points"]
                segments = [
                    Line(M(a), M(b), color=c["color"], stroke_width=3).set_opacity(0.85)
                    for a, b in zip(points, points[1:]) if np.linalg.norm(b - a) > 1e-9
                ]
                path = VGroup(*segments)
                if segments:
                    direction = points[-1] - next(p for p in reversed(points[:-1])
                                                   if np.linalg.norm(points[-1] - p) > 1e-9)
                    tip = Triangle().scale(0.12).rotate(math.radians(deg_of(direction) - 90))
                    tip.set_fill(c["color"], opacity=1).set_stroke(width=0).move_to(M(move["pos"]))
                    path.add(tip)
                    path.set_z_index(1)
                p = M(move["pos"])
                ring = Circle(radius=0.17, fill_opacity=0, stroke_color=c["color"], stroke_width=2.5).move_to(p)
                facing = Arrow(p, p + 0.36 * np.array([*unit(move["facing_deg"]), 0]), buff=0.03,
                               color=c["color"], stroke_width=2.5, max_tip_length_to_length_ratio=0.45)
                label = c["name"] + str(i) + (f" · {move['posture']}" if move.get("posture") else "")
                step_label = T(label, 13, c["color"])
                incoming = next((points[j] - points[j - 1] for j in range(len(points) - 1, 0, -1)
                                 if np.linalg.norm(points[j] - points[j - 1]) > 1e-9), np.array([1.0, 0.0]))
                incoming = incoming / np.linalg.norm(incoming)
                perpendicular = np.array([-incoming[1], incoming[0], 0])
                tangent = np.array([incoming[0], incoming[1], 0])
                directions = [perpendicular, -perpendicular, tangent, -tangent,
                              (perpendicular + tangent) / math.sqrt(2),
                              (perpendicular - tangent) / math.sqrt(2),
                              (-perpendicular + tangent) / math.sqrt(2),
                              (-perpendicular - tangent) / math.sqrt(2)]
                label_radius = math.hypot(step_label.width, step_label.height) / 2
                candidates = [p + direction * (label_radius + offset)
                              for offset in (0.18, 0.42, 0.68, 0.94) for direction in directions]

                def label_penalty(center):
                    half_w, half_h = step_label.width / 2, step_label.height / 2
                    penalty = max(0, MAP_X[0] + half_w - center[0]) ** 2
                    penalty += max(0, center[0] + half_w - (PANEL_LEFT - 0.45)) ** 2
                    penalty += max(0, MAP_Y[0] + half_h - center[1]) ** 2
                    penalty += max(0, center[1] + half_h - MAP_Y[1]) ** 2
                    for obstacle in move_label_obstacles:
                        distance = np.linalg.norm(center[:2] - obstacle[:2])
                        penalty += max(0, label_radius + 0.32 - distance) ** 2
                    for obstacle, radius in prop_obstacles:
                        distance = np.linalg.norm(center[:2] - obstacle[:2])
                        penalty += max(0, label_radius + radius + 0.08 - distance) ** 2
                    for start, end in axis_obstacles:
                        distance = segment_distance(center[:2], start[:2], end[:2])
                        penalty += 20 * max(0, label_radius + 0.12 - distance) ** 2
                    for old_center, old_radius in move_label_centers:
                        distance = np.linalg.norm(center[:2] - old_center[:2])
                        penalty += max(0, label_radius + old_radius + 0.12 - distance) ** 2
                    for start, end in move_path_obstacles:
                        distance = segment_distance(center[:2], start[:2], end[:2])
                        penalty += 20 * max(0, label_radius + 0.12 - distance) ** 2
                    return penalty

                label_center = min(candidates, key=label_penalty)
                step_label.move_to(label_center)
                move_label_centers.append((label_center, label_radius))
                label_bg = SurroundingRectangle(step_label, buff=0.04, color="#20262C",
                                                fill_color="#20262C", fill_opacity=0.82,
                                                stroke_width=0)
                ghost = VGroup(ring, facing, label_bg, step_label).set_z_index(2)
                animations = [Create(path), FadeIn(ghost)] if segments else [FadeIn(ghost)]
                self.play(*animations, run_time=0.6)

        # ---- legend panel
        rows = []
        for s in S.shots:
            parts = [f"{s['n']} · {s.get('label', s.get('size', 'shot'))}", f"{int(s['lens'])}mm"]
            if s.get("height") and s["height"] != "eye":
                parts.append(s["height"])
            mv = s.get("move", "static")
            if mv != "static":
                parts.append(mv)
            if s["dist"] > 3.5 and s.get("target") != "light":
                parts.append(f"{s['dist']:.0f} m")
            col = WARN_C if s["crossed"] and not s.get("allow_cross") else (HL_C if s.get("highlight") else CAM_C)
            rows.append(("  ·  ".join(parts), col))
        note_rows = [(c["turn"]["label"], c.get("color", WHITE))
                     for c in S.chars.values() if c.get("turn", {}).get("label")]
        note_rows.extend((move["label"], c.get("color", WHITE))
                         for c in S.chars.values() for move in c["moves"] if move.get("label"))
        for e in S.eyelines:
            if e.get("label"):
                note_rows.append((e["label"], S.chars[S.character_name(e["from"])]["color"]))
        for n in S.notes:
            note_rows.append((n, "#C9D1D9"))
        for light_index, light in enumerate(S.lights, start=1):
            if light.get("label"):
                label = f"L{light_index} · {light['label']}" if len(S.lights) > 1 else light["label"]
                note_rows.append((label, "#FFD84D"))
        static_all = all(s.get("move", "static") == "static" for s in S.shots)
        head = T("SHOTS" + (" — every camera static" if static_all else ""), 15, AXIS_C, BOLD)
        shot_txt = VGroup(*[T(r, 14, c) for r, c in rows])
        note_head = T("NOTES", 13, "#9AA5B1", BOLD) if note_rows else VGroup()
        note_txt = VGroup(*[T(r, 13, c) for r, c in note_rows])
        block = VGroup(head, shot_txt.arrange(DOWN, aligned_edge=LEFT, buff=0.14))
        if note_rows:
            block.add(note_head, note_txt.arrange(DOWN, aligned_edge=LEFT, buff=0.1))
        block.arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        maxw, maxh = PANEL_RIGHT - PANEL_LEFT - 0.3, 6.6
        k = min(1.0, maxw / block.width, maxh / block.height)
        block.scale(k)
        block.move_to([0, 0.2, 0]).align_to(np.array([PANEL_LEFT + 0.15, 0, 0]), LEFT)
        if block.get_top()[1] > 3.0:
            block.shift(DOWN * (block.get_top()[1] - 3.0))
        bg = SurroundingRectangle(block, buff=0.18, color="#0E1319", fill_color="#0E1319", fill_opacity=0.82,
                                  stroke_width=0, corner_radius=0.12)
        bg.set_z_index(5); block.set_z_index(6)
        self.play(FadeIn(bg), FadeIn(head), run_time=0.3)

        # ---- cameras, one by one
        taken = [M(c["pos"]) for c in S.chars.values()] + \
                [M(c["pos"]) + np.array([0, 0.48, 0]) for c in S.chars.values()] + \
                [M(move["pos"]) for c in S.chars.values() for move in c["moves"]]
        for i, s in enumerate(S.shots):
            tgt_map = M(s["target_pt"]) if s.get("target") != "light" else M(s["pos"])
            p0, far = clamp_to_map(M(s["pos"]), tgt_map)
            s["_far"] = far
            p = p0
            if any(np.linalg.norm(p - q) < 0.42 for q in taken):
                # nearest free spot on a small spiral around the true position
                for r in np.arange(0.12, 0.9, 0.06):
                    hit = None
                    for a in range(0, 360, 20):
                        c = p0 + r * np.array([*unit(a + s["dir"] + 180), 0])
                        if all(np.linalg.norm(c - q) >= 0.42 for q in taken):
                            hit = c
                            break
                    if hit is not None:
                        p = hit
                        break
            taken.append(p)
            col = WARN_C if s["crossed"] and not s.get("allow_cross") else (HL_C if s.get("highlight") else CAM_C)
            length = max(0.9, min(s["dist"] * scale + 0.6, 2.6 if s.get("target") == "light" else 4.2))
            half = s["fov"] / 2
            a1, a2 = unit(s["dir"] + half), unit(s["dir"] - half)
            cone = Polygon(p, p + length * np.array([*a1, 0]), p + length * np.array([*a2, 0]),
                           stroke_color=col, stroke_width=1.5, fill_color=col, fill_opacity=0.10)
            body = Square(0.32, stroke_color=col, stroke_width=2.5, fill_color="#10151C",
                          fill_opacity=1).rotate(math.radians(s["dir"])).move_to(p)
            num = T(s["n"], 17, col).move_to(p)
            body.set_z_index(4); num.set_z_index(4)
            anims = [FadeIn(cone), GrowFromCenter(body), FadeIn(num), FadeIn(shot_txt[i], shift=LEFT * 0.2)]
            mv = s.get("move", "static")
            if mv in ("push in", "dolly in", "push", "dolly out", "pull back"):
                sign = -1 if mv in ("dolly out", "pull back") else 1
                tip = p + sign * 0.7 * np.array([*unit(s["dir"]), 0])
                anims.append(GrowArrow(Arrow(p, tip, buff=0.18, color=col, stroke_width=3,
                                             max_tip_length_to_length_ratio=0.35)))
            elif mv in ("truck left", "truck right", "track left", "track right"):
                sg = 1 if mv.endswith("left") else -1
                sidev = np.array([*unit(s["dir"] + 90 * sg), 0])
                anims.append(GrowArrow(Arrow(p, p + 0.8 * sidev, buff=0.18, color=col, stroke_width=3,
                                             max_tip_length_to_length_ratio=0.35)))
            elif mv.startswith("pan"):
                sg = 1 if "left" in mv else -1
                anims.append(Create(Arc(radius=0.45, start_angle=math.radians(s["dir"]), angle=math.radians(40 * sg),
                                        color=col, stroke_width=3).move_arc_center_to(p).add_tip(tip_length=0.12)))
            self.play(*anims, run_time=0.55)
            self.wait(0.22)

        # ---- 180 axis
        if S.axis:
            a, b = M(S.point(S.axis[0])), M(S.point(S.axis[1]))
            d = (b - a) / np.linalg.norm(b - a)
            axis = DashedLine(a - d * 1.4, b + d * 1.4, color=AXIS_C, stroke_width=3, dash_length=0.15)
            lab = T("180° axis", 16, AXIS_C)
            if any(character["moves"] for character in S.chars.values()):
                label_radius = math.hypot(lab.width, lab.height) / 2 + 0.16
                normal = np.array([-d[1], d[0], 0])
                anchors = [a - d * 1.4, a, (a + b) / 2, b, b + d * 1.4]
                candidates = [
                    anchor + normal * sign * distance
                    for anchor in anchors
                    for sign in (-1, 1)
                    for distance in (label_radius, label_radius + 0.35)
                ]

                def axis_label_penalty(center):
                    half_w, half_h = lab.width / 2, lab.height / 2
                    penalty = max(0, MAP_X[0] + half_w - center[0]) ** 2
                    penalty += max(0, center[0] + half_w - (PANEL_LEFT - 0.45)) ** 2
                    penalty += max(0, MAP_Y[0] + half_h - center[1]) ** 2
                    penalty += max(0, center[1] + half_h - MAP_Y[1]) ** 2
                    for start, end in move_path_obstacles:
                        distance = segment_distance(center[:2], start[:2], end[:2])
                        penalty += 20 * max(0, label_radius + 0.1 - distance) ** 2
                    return penalty

                lab.move_to(min(candidates, key=axis_label_penalty))
            else:
                lab.move_to(a - d * 1.4 + np.array([0, 0.3, 0]))
            any_cross = any(s["crossed"] and not s.get("allow_cross") for s in S.shots)
            verdict = T("a camera crosses the axis" if any_cross else "every camera on one side of the axis",
                        14, WARN_C if any_cross else AXIS_C)
            verdict.move_to([sum(MAP_X) / 2, MAP_Y[0] + 0.05, 0]).set_z_index(7)
            self.play(Create(axis), FadeIn(lab), run_time=0.7)
            self.play(FadeIn(verdict), run_time=0.35)
        drawn_axes = {frozenset(S.axis)} if S.axis else set()
        for shot in S.shots:
            refs = shot.get("axis_refs")
            key = frozenset(refs) if refs else None
            if not refs or key in drawn_axes:
                continue
            drawn_axes.add(key)
            a, b = (M(point) for point in S._axis_points(refs))
            d = (b - a) / np.linalg.norm(b - a)
            axis = DashedLine(a - d * 1.4, b + d * 1.4, color="#9AA5B1",
                              stroke_width=1.6, dash_length=0.12).set_z_index(2)
            moved_refs = [ref for ref in refs if S._move_reference(ref)]
            label = "axis after " + ", ".join(moved_refs) if moved_refs else f"axis for shot {shot['n']}"
            perpendicular = np.array([-d[1], d[0], 0])
            lab = T(label, 11, "#B8C1CC").move_to((a + b) / 2 + perpendicular * 0.32)
            lab_bg = SurroundingRectangle(lab, buff=0.04, color="#252B31",
                                          fill_color="#252B31", fill_opacity=0.82,
                                          stroke_width=0).set_z_index(2)
            lab.set_z_index(3)
            self.play(Create(axis), FadeIn(lab_bg), FadeIn(lab), run_time=0.45)

        # ---- eyelines
        for i, e in enumerate(S.eyelines):
            fa, fb = M(S.point(e["from"])), M(S.point(e["to"]))
            ang_ = -0.35 if i % 2 == 0 else 0.35
            arr = CurvedArrow(fa + 0.22 * (fb - fa) / np.linalg.norm(fb - fa),
                              fb - 0.22 * (fb - fa) / np.linalg.norm(fb - fa),
                              angle=ang_, color=S.chars[S.character_name(e["from"])]["color"],
                              stroke_width=3, tip_length=0.18)
            self.play(Create(arr), run_time=0.55)
        if note_rows:
            self.play(FadeIn(note_head), *[FadeIn(t, shift=LEFT * 0.2) for t in note_txt], run_time=0.6)
        self.wait(2.5)


def ffmpeg_executable():
    return shutil.which("ffmpeg") or imageio_ffmpeg.get_ffmpeg_exe()


def run_ffmpeg(*args):
    subprocess.run([ffmpeg_executable(), *map(str, args)], check=True)


def extract_last_frame(src, still):
    run_ffmpeg("-y", "-loglevel", "error", "-sseof", "-3", "-i", src, "-update", "1", still)


def conform_video(src, out):
    run_ffmpeg("-y", "-loglevel", "error", "-i", src, "-vf", "fps=30,format=yuv420p",
               "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
               "-movflags", "+faststart", out)


def add_poster(src, out, seconds, still):
    """Prepend the finished map as a poster, then cross-fade into the build-up."""
    fade = min(0.35, seconds / 2)
    run_ffmpeg(
        "-y", "-loglevel", "error",
        "-loop", "1", "-t", f"{seconds + fade:.6f}", "-framerate", "30", "-i", still,
        "-i", src,
        "-filter_complex",
        f"[0:v]format=yuv420p,setsar=1,fps=30,settb=AVTB[p];[1:v]format=yuv420p,setsar=1,fps=30,settb=AVTB[m];"
        f"[p][m]xfade=transition=fade:duration={fade:.6f}:offset={seconds:.6f},fps=30,format=yuv420p,settb=AVTB[v]",
        "-map", "[v]", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        "-movflags", "+faststart", out,
    )


def make_report(video, elapsed, preview=False, check=False):
    report = {
        "video": None if preview or check else video,
        "warnings": SPEC.warnings,
        "shots": [{"n": s["n"], "label": s.get("label"), "pos_m": [round(x, 2) for x in s["pos"]],
                   "dir_deg": round(s["dir"], 1), "distance_m": round(s["dist"], 2), "lens": s["lens"],
                   "hfov_deg": round(s["fov"], 1), "crosses_axis": bool(s["crossed"])} for s in SPEC.shots],
        "characters": [{
            "name": c["name"],
            "pos_m": [round(float(x), 2) for x in c["pos"]],
            "facing_deg": round(c["facing_deg"], 1),
            "posture": c.get("posture"),
            "moves": [{
                "to_m": [round(float(x), 2) for x in move["pos"]],
                "facing_deg": round(move["facing_deg"], 1),
                "posture": move.get("posture"),
                "label": move.get("label"),
            } for move in c["moves"]],
        } for c in SPEC.chars.values()],
        "lights": [{
            "type": light.get("type", "sun"),
            "name": light.get("name"),
            "direction_deg": round(SPEC.angle(light["direction"], SPEC.scene_center()), 1),
            **({"pos_m": [round(float(x), 2) for x in light["pos"]]} if light.get("pos") is not None else {}),
            "target": light.get("target"),
        } for light in SPEC.lights],
        "axis": SPEC.axis,
        "elapsed_seconds": round(elapsed, 2),
    }
    if preview:
        report["preview"] = video
    if check:
        report["check"] = True
    return report


def manimgx_command():
    module = subprocess.run([sys.executable, "-m", "manimgx", "--help"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if module.returncode == 0:
        return [sys.executable, "-m", "manimgx"]
    entrypoint = os.path.join(os.path.dirname(sys.executable), "manimgx")
    if os.path.isfile(entrypoint) and os.access(entrypoint, os.X_OK):
        return [entrypoint]
    raise RuntimeError("cannot run ManimGX: neither python -m manimgx nor the adjacent manimgx entry point works")


def main():
    global SPEC
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("-o", "--out")
    ap.add_argument("--quality", default="h", choices=["l", "m", "h"])
    ap.add_argument("--poster", type=float, default=1.0,
                    help="seconds the finished map is shown at the very start (0 = off)")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true",
                      help="resolve the spec and print its report without rendering")
    mode.add_argument("--preview", action="store_true",
                      help="render an 854x480 preview PNG and report without creating the final MP4")
    ap.add_argument("--version", action="version", version="staging_render 1.0.0 (manimgx 0.1.1)")
    args = ap.parse_args()
    started = time.perf_counter()
    try:
        with open(args.spec) as f:
            SPEC = Spec(json.load(f))
    except (OSError, json.JSONDecodeError, ValueError, TypeError, KeyError, IndexError, OverflowError) as exc:
        message = " ".join(str(exc).splitlines())
        print(f"spec error: {message}", file=sys.stderr)
        return 2
    if args.check:
        report = make_report(None, time.perf_counter() - started, check=True)
        if args.out:
            report_path = os.path.splitext(os.path.abspath(args.out))[0] + ".report.json"
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)
        print(json.dumps(report, indent=2))
        return 0
    out = os.path.abspath(args.out or "staging.mp4")
    stem = os.path.splitext(out)[0]
    os.makedirs(os.path.dirname(out), exist_ok=True)
    image_path = stem + (".preview.png" if args.preview else ".last.png")
    quality = "854x480" if args.preview else {"l": "854x480", "m": "1280x720", "h": "1920x1080"}[args.quality]
    try:
        renderer = manimgx_command()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory(prefix="top-down-staging-") as tmp:
        src = os.path.join(tmp, "staging_render.mp4")
        command = [*renderer, "render", os.path.abspath(__file__), "StagingScene", "-r", quality,
                   "--fps", "30", "-o", src]
        try:
            subprocess.run(command, check=True, env={**os.environ, "STAGING_SPEC": os.path.abspath(args.spec)},
                           stdout=sys.stderr, stderr=sys.stderr)
        except (OSError, subprocess.CalledProcessError) as exc:
            status = f" (exit {exc.returncode})" if isinstance(exc, subprocess.CalledProcessError) else ""
            print(f"ManimGX render failed{status}: {exc}", file=sys.stderr)
            return 1
        extract_last_frame(src, image_path)
        if not args.preview:
            if args.poster > 0:
                add_poster(src, out, args.poster, image_path)
            else:
                conform_video(src, out)
    elapsed = time.perf_counter() - started
    report = make_report(image_path if args.preview else out, elapsed, preview=args.preview)
    rp = stem + ".report.json"
    with open(rp, "w") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
