---
name: "top-down-staging"
description: "Turn any scene description (script, shot list or one casual sentence) into an animated top-down staging video (rendered with ManimGX): positions, light, every camera cone shot by shot, 180° axis auto-checked."
---

# Top-down staging

Placement only. This skill does not write story, dialogue or acting. It answers one question: **where is everyone and everything, and where does each camera stand and look?** The output is a short video in the style of a director's floor plan: the finished map shows for a second, then the map builds up, then cameras appear one by one with their field-of-view cones, then the 180° axis and the eyelines.

The person may be a professional with a shot list or a beginner with one sentence ("two friends arguing in a café"). Both must end with the same quality of map. Fill every gap with sensible defaults and say what you assumed — never block on missing detail.

## Workflow

1. **Read the scene.** Pull out:
   - the location and the props that matter for blocking (furniture, doors, windows, vehicles, paths, walls);
   - every character, where they are and what they face;
   - the light source that matters (sun, window, lamp) and who it hits;
   - the main relationship — the pair who talk to or look at each other most. That pair defines the 180° axis;
   - shots, if the person gave any. If none were given, build coverage yourself (see Coverage).
   Ask at most ONE short question, and only if the location itself is unknowable. Otherwise assume and move on.
2. **Lay it out in metres** with real-world sizes (table below). Map convention: +y is "into the scene" as seen from the main/opening camera, +x is right. Put the main camera south of the action looking north.
3. **Write the scene spec** (JSON, schema below) to the working directory.
4. **Render** with the bundled engine, `scripts/staging_render.py` (path relative to this skill's folder; do not rewrite or copy it):
   `uv run <skill-dir>/scripts/staging_render.py scene.json -o <name>.mp4 --quality h`.
   Use `--quality l` for a quick draft. The video opens on the finished map for 1 second (`--poster 1.0`, the default), then cross-fades into the step-by-step build. That first frame is also the thumbnail on social platforms, so it must show the whole result; use `--poster 0` only if the person asks for a plain build-up.
   It prints a JSON report with each camera's position, distance, horizontal field of view and `warnings` (also saved as `<name>.report.json`), and saves `<name>.last.png`, the finished map.
5. **Check the result before delivering.** Open `<name>.last.png` and look at it: every label readable, no camera icon sitting on a person, cones pointing at the right subject, legend not cut off. Read `warnings` — an auto-mirrored shot or a camera crossing the axis must be mentioned to the person. Fix the spec and re-render (two rounds at most).
6. **Deliver** the video plus the spec JSON (so the layout can be edited by changing numbers). In the person's language, say in two or three lines what you assumed, and any axis warning. Map labels are English unless the person asks otherwise.

## Coverage (when no shots are given)

Build the smallest set that covers the scene, in shooting-script order, max 8:
1. **Establishing wide** — everyone in frame (`target`: list of all names, `size: "wide"`, `lens: 35`, `from: "S"`).
2. **For the main pair A/B:** an over-the-shoulder on each (`over_shoulder: B, target: A` and the reverse). Pick the shoulders so both cameras sit on the same side of the axis; the engine mirrors any that do not and reports it.
3. **Singles** for the key beats: `size: "cu"` or `"mcu"`, `lens: 85`/`50`, `from: "front-left"`/`"front-right"` (relative to the character's facing), same side of the axis.
4. **Inserts** for any prop the action depends on (`size: "insert"`, `lens: 85`, `height: "high"` for things on a table).
5. **A closing or re-establishing shot** if someone enters, leaves or the geography changes.
Every camera is static unless the person asks for a move. Keep each `label` under ~28 characters.

## Default sizes and distances (metres)

| Thing | Size | | Situation | Distance |
| --- | --- | --- | --- | --- |
| Park bench | 1.8 × 0.5 | | Two people talking, seated across a table | 1.4–1.6 |
| Café table (round) | r 0.4 | | Two people talking, standing | 1.0–1.3 |
| Dining table | 1.8 × 0.9 | | Group standing | 1.2 between neighbours |
| Desk | 1.4 × 0.7 | | Strangers in a public place | 3–6 |
| Sofa | 2.0 × 0.9 | | Doorway width | 0.9 |
| Bed (double) | 2.0 × 1.6 | | Room (living) | 4 × 5 |
| Car | 4.5 × 1.8 | | Street lane width | 3.5 |
| Yoga mat | 1.8 × 0.65 | | Footpath width | 1.5 |

Lens → horizontal field of view on full frame: 24mm ≈ 74°, 35mm ≈ 54°, 50mm ≈ 40°, 85mm ≈ 24°. The engine computes camera distance from shot size and lens, and widens it until a listed group fits.

## Scene spec (JSON)

```json
{
  "title": "Top-down staging — <scene>",
  "north_label": "into the scene",
  "ground": "#2E5A3A",
  "props": [
    {"type": "band", "name": "path", "points": [[-14, -4], [14, 0]], "width": 1.4, "color": "#8C8C88", "label": "path"},
    {"type": "rect", "name": "bench", "pos": [4, -0.3], "size": [1.9, 0.55], "rotation": 9, "color": "#1F4A2E", "label": "bench"},
    {"type": "circle", "name": "tree", "pos": [-8, 3], "radius": 2.5, "color": "#1E3F27", "label": "tree"}
  ],
  "characters": [
    {"name": "A", "pos": [4, -0.3], "facing": "S", "turn": {"to": "SE", "label": "A stands, turns to the sun"}},
    {"name": "B", "pos": [-0.4, 3.7], "facing": "towards:A"}
  ],
  "light": {"type": "sun", "direction": "SE", "target": "A", "label": "sun: south-east, low"},
  "axis": ["B", "A"],
  "eyelines": [{"from": "B", "to": "A", "label": "B shouts at A"}],
  "notes": ["anything worth a line in the legend"],
  "shots": [
    {"label": "opening wide", "size": "wide", "lens": 35, "pos": [1, -6.5], "dir": "N"},
    {"label": "A close-up", "size": "cu", "lens": 50, "target": "A", "from": "front"},
    {"label": "behind A, sun in frame", "size": "ots", "lens": 24, "height": "low",
     "over_shoulder": "A", "shoulder": "right", "target": "light", "highlight": true}
  ]
}
```

Field reference:
- **Angles** (`facing`, `dir`, `light.direction`, `turn.to`, compass `from`): map degrees counter-clockwise from +x (E 0, N 90, W 180, S 270), a compass string (`"N"`, `"SE"` …) or `"towards:<name>"` (a character, a named prop, or `light`).
- **props**: `rect` (pos, size [w, h], rotation, color, label), `circle` (pos, radius), `band` (two points + width; drawn as an endless strip — roads, paths, walls, windows; `dark_label: true` for light-coloured bands).
- **characters**: `pos`, `facing`, optional `color`, optional `turn` {`to`, `label`} for a change of facing during the scene.
- **light**: `type` `sun` | `window` | `lamp`; `direction` it comes from; `target` it hits; optional `pos` to pin the icon (windows, lamps); `label`.
- **axis**: the two names that define the 180° line. The first shot sets the allowed side.
- **shots** — placement, in priority order:
  - `pos` (+ optional `dir`): exact position. If it crosses the axis it is drawn red and reported.
  - `over_shoulder`: name, plus `shoulder` `"right"`/`"left"` and `target`: camera ~1 m behind that shoulder looking at the target.
  - `from` relative to the target character's facing: `front`, `front-left`, `front-right`, `left`, `right`, `behind`, `behind-left`, `behind-right` (`relative_to` to use another character; `relative_facing: "turned"` to use the facing after `turn`). Or `from` as a compass direction from the target.
  - nothing: placed on the line from the target toward the first camera.
  Auto-placed shots that land on the wrong side of the axis are mirrored across it and reported. `allow_cross: true` keeps a deliberate cross; `ignore_axis: true` skips the check for that shot.
  - Other fields: `label`, `size` (`wide`, `full`, `medium wide`, `medium`, `mcu`, `cu`, `ecu`, `insert`, `ots`, `establishing`), `lens` (mm), `height` (`eye` default, `low`, `high`, `overhead` — legend only), `move` (`static` default; `push in`, `dolly out`, `truck left/right`, `pan left/right` draw an arrow), `highlight: true` for the one shot that matters most.

## Limits — say these when relevant

- The top-down map is for the director and the team, not for the video model. Video models think in frames; a staging reference fed to a model should be drawn from the camera's point of view.
- A map solves space, not time. It cannot tell whether the cut rhythm will feel rushed.
- Cameras farther away than the map can show are pinned to the map edge on their true line, and the legend gives the real distance.

## Setup (once per environment)

The engine runs on [ManimGX](https://github.com/academa-labs/manimgx). Its dependencies (Python ≥ 3.13, `manimgx`, `numpy`, a bundled ffmpeg) are declared inside the script, and `uv run` installs them on first use. Only `uv` is needed:

```bash
command -v uv >/dev/null || { curl -LsSf https://astral.sh/uv/install.sh | sh; export PATH="$HOME/.local/bin:$PATH"; }
```
Do not install the `manim` package, LaTeX or system ffmpeg for this skill. Without a GPU, ManimGX renders on the CPU (bundled lavapipe). `no GPU adapter` means a sandbox hides the GPU: run outside the sandbox.
