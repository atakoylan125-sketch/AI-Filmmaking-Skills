---
name: "top-down-staging"
description: "Spatial previsualization: turn any scene description (script, shot list or one casual sentence) into an animated top-down staging map rendered with ManimGX — environment and key objects, character positions, postures, facings and movement, physical light sources, every camera with its lens and field of view, 180° axis auto-checked. When the brief is thin it asks a short round of scene-specific multiple-choice questions, and it always shows the proposed layout for approval before rendering."
---

# Top-down staging

Placement only. This skill does not write story, dialogue or acting, and it is not tied to any camera system, video generator or production tool. It answers one question: **where is everything and everyone, how do they move, where does the light come from, and where does each camera stand and look?** The output is a short video in the style of a director's floor plan: the finished map shows for a second, then the map builds up, then movement paths, then cameras appear one by one with their field-of-view cones, then the 180° axis and the eyelines.

The person may be a professional with a full shot list or a beginner with one sentence. Both must end with the same quality of map. What differs is the road there: a complete brief goes straight to a proposed layout; a thin brief goes through a short guided intake round first, so the person decides the placement instead of you guessing it. The questions also teach a beginner what a staging brief needs. Every road ends with a plan the person approves or corrects before anything is rendered.

Work only from the scene in front of you. The question templates, the size table and the spec example below show shapes and syntax, not content: never carry their locations, props, names, positions or colours into a real scene.

## The complete brief — seven slots

A brief is complete when it answers these seven. Check every incoming brief against them before doing anything else.

| # | Slot | What it pins down | Why the map needs it |
| --- | --- | --- | --- |
| 1 | **Location** | type, size and character of the place (small or large, cramped or open, style or era) and its fixed geometry: walls, doors, windows, the objects that matter for blocking | sets the scale of the whole map and which props exist |
| 2 | **Positions** | who is where, their posture (standing, seated, lying, kneeling…), who faces whom, how far apart | the dots, posture tags and facing arrows; the 180° axis is drawn from here |
| 3 | **Orientation** | which side of a character the key feature is on (window, door, wall, road), stated relative to a character: "window on her right" | without it the map can come out mirrored and every background is wrong |
| 4 | **Light** | each source that matters, where it physically is, the side it comes from, hard or soft | decides which side of each face is lit and which shots look into the light |
| 5 | **Surroundings** | what lies on the other sides of the action | it becomes the background of every reverse shot |
| 6 | **Shots** | how many, in what order, and the size, lens and angle of each (close-up on A, centred two-shot, over A's shoulder onto B…) | these are the cameras |
| 7 | **Movement** | who moves, from where to where and when (stands up, crosses, enters, leaves, turns), and what happens in each shot | movement changes positions, facings and sometimes the axis mid-scene; moves are drawn as paths |

A slot counts as filled when the brief states it or makes it unambiguous ("they sit across a booth" fills Positions). Slot 7 only matters when someone moves: if every beat is a line of dialogue and nobody moves, it needs no question.

## Intake round — when the brief is thin

1. **Score the brief** against the seven slots, silently. Never show the checklist itself to the person.
2. **Everything filled → skip intake** and go to Workflow. Also skip it when the person says they want no questions ("sorma", "direkt yap", "just do it"): fill the gaps with defaults; they are listed in the plan (Workflow step 4).
3. **Anything missing → ask**, in the person's language:
   - At most **3 questions per message and at most 2 messages**. Order: Location → Positions → Shots first, because they decide the structure of the map; then Orientation → Light → Surroundings; Movement last.
   - If Location and Positions are both missing, ask only those two in the first message: the options of every other question depend on their answers.
   - Every question is multiple choice: 2–4 options **written for this scene**, built from what the brief already says, plus a final **"You decide"** option (in the person's language, e.g. "Sen öner"). The person can always type their own answer instead.
   - Mark the option you would pick as **(recommended)** with a few words of reason, so a beginner can simply take it.
   - Every question carries **one short line on why it matters for the map**.
   - Use the `AskUserQuestion` tool when it is available; otherwise write numbered questions with lettered options in plain text.
   - Never ask what the brief already answers. Never ask about story, dialogue or acting: that is not this skill's job.
   - When the person writes like a professional (lenses, shot sizes, "over A's shoulder", axis), take every stated choice exactly as given. Ask only about slots that are genuinely missing, and never re-open a decision they made.
4. After the answers, anything still open or answered "You decide" gets a sensible default. Then go to Workflow; the plan in step 4 is where the person confirms or corrects these defaults.

### Question templates

These show the shape of each question. Rewrite the wording and the options for the scene in front of you; never paste them verbatim.

- **Location** — "Where does this happen, and what is the place like?" → options built from the brief, e.g. *small, cramped interior · large, open interior · outdoors · You decide*. Why: it sets the scale and which props exist.
- **Positions** — "How are they placed?" → options that fit the place and the people in the brief, combining position and posture (*both seated, facing each other · side by side · one seated, one standing · You decide*). Why: the 180° axis is drawn between the two main characters.
- **Orientation** — "Which side of <A> is the <window / door / wall>?" → *<A>'s left · <A>'s right · behind <A> · behind <B>*. Why: without it the map can come out mirrored and every background changes.
- **Light** — "Where does the main light come from?" → sources that exist in this place (*from the <window / door> side · from overhead fixtures · from a practical in the scene · from behind one of them (backlit) · You decide*). Ask soft or hard only if they named a source. Why: it decides which side of each face is lit.
- **Surroundings** — "What is on the other side of them?" → options that fit the location. Why: it is the background of every reverse shot.
- **Shots** — "How do you want to cover it?" → *I'll give you a list (count, order, size) · classic coverage: a wide, two over-the-shoulders, two close-ups · one continuous shot · You decide*. Why: these are the cameras.
- **Movement** (only when movement is plausible) — "Does anyone move during the scene?" → *no, everyone stays put · <a move this scene suggests, written for it> · yes (tell me who, from where to where, and when) · You decide*. Why: moves are drawn as paths and can shift the axis.

## Workflow

1. **Read the scene** — the brief plus any intake answers. Pull out:
   - the location, its fixed geometry and the props that matter for blocking (walls, doors, windows, furniture, vehicles, paths);
   - every character: where they are, posture, what they face;
   - every move: who, from where, through where, to where, the facing and posture at the end;
   - every light source that matters (sun, window, lamp, practical): where it physically is, the side it comes from, who it hits;
   - the main relationship — the pair who talk to or look at each other most. That pair defines the 180° axis. If a move changes the geometry, decide the axis for the shots after it;
   - the shots. If the person left them to you or chose classic coverage, build them yourself (see Coverage).
2. **Lay it out in metres** with real-world sizes (table below). Map convention: +y is "into the scene" as seen from the main/opening camera, +x is right. Put the main camera south of the action looking north.
3. **Write the scene spec** (JSON, schema below) to the working directory.
4. **Preview and get approval — before any render.** Run
   `uv run <skill-dir>/scripts/staging_render.py scene.json -o <name>.mp4 --preview`
   (a few seconds). It writes `<name>.preview.png`, the finished map, and `<name>.report.json`. Look at the preview yourself first and fix obvious problems. Then show the person the preview image and a compact plan in their language:
   - **Environment** — size of the space, the key objects and where they are (relative words plus metres);
   - **Characters** — position, posture, facing; then each move in order;
   - **Light** — each source, where it is, which side of whom it lights;
   - **Cameras** — a table: number, size, lens, where it stands (e.g. "2.9 m front-right of A, eye height"), what it sees;
   - **180° axis** — which pair, which side the cameras stay on, any shot that is mirrored or crosses;
   - **Assumptions** — every value you chose rather than the person, marked as such.
   Ask them to approve or correct anything ("put the door on the other wall", "make shot 3 a close-up", "she stays seated"). Apply corrections to the spec, preview again and show the changed plan; repeat until they approve. Render only after approval. Skip this step only if the person explicitly asked to render without review; then list the assumptions at delivery.
5. **Render** with the bundled engine, `scripts/staging_render.py` (path relative to this skill's folder; do not rewrite or copy it):
   `uv run <skill-dir>/scripts/staging_render.py scene.json -o <name>.mp4 --quality h`.
   Use `--quality l` for a quick draft. The video opens on the finished map for 1 second (`--poster 1.0`, the default), then cross-fades into the step-by-step build. That first frame is also the thumbnail on social platforms, so it must show the whole result; use `--poster 0` only if the person asks for a plain build-up.
   It prints a JSON report with each character, light and camera (position, distance, horizontal field of view) and `warnings` (also saved as `<name>.report.json`), and saves `<name>.last.png`, the finished map.
6. **Check the result before delivering.** Open `<name>.last.png` and look at it: every label readable, no camera icon sitting on a person, cones pointing at the right subject, movement paths readable, legend not cut off. Read `warnings` — an auto-mirrored shot or a camera crossing the axis must be mentioned to the person. Fix the spec and re-render (two rounds at most).
7. **Deliver** the video plus the spec JSON (so the layout can be edited by changing numbers). In the person's language, say in two or three lines which defaults remain (only what intake left open or the person handed back), and any axis warning. Map labels are English unless the person asks otherwise.

## Coverage (when the shots are left to you)

Build the smallest set that covers the scene, in shooting-script order, max 8:
1. **Establishing wide** — everyone in frame (`target`: list of all names, `size: "wide"`, `lens: 35`, `from: "S"`).
2. **For the main pair A/B:** an over-the-shoulder on each (`over_shoulder: B, target: A` and the reverse). Pick the shoulders so both cameras sit on the same side of the axis; the engine mirrors any that do not and reports it.
3. **Singles** for the key beats: `size: "cu"` or `"mcu"`, `lens: 85`/`50`, `from: "front-left"`/`"front-right"` (relative to the character's facing), same side of the axis.
4. **Inserts** for any prop the action depends on (`size: "insert"`, `lens: 85`, `height: "high"` for things on a table).
5. **After a move:** cover the end position (`target: "A@1"`), and give the shots after the move their own axis (`"axis": ["A@1", "B"]`) when the move changes the geometry. Add a closing or re-establishing shot if someone enters, leaves or the geography changes.
Every camera is static unless the person asks for a move. Keep each `label` under ~28 characters.

## Default sizes and distances (metres)

Real-world reference sizes for laying out any place, not a scene template.

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
  "ground": "#3A3D44",
  "props": [
    {"type": "band", "name": "wall", "points": [[-6, 2.6], [6, 2.6]], "width": 0.3, "color": "#8A8F98", "label": "wall", "dark_label": true},
    {"type": "rect", "name": "prop_1", "pos": [0, 0], "size": [1.2, 0.7], "color": "#6B6F78", "label": "prop_1"},
    {"type": "circle", "name": "prop_2", "pos": [3.2, 1.2], "radius": 0.45, "color": "#55595F", "stroke": "#9AA0A8", "label": "prop_2"}
  ],
  "characters": [
    {"name": "A", "pos": [0, -0.8], "posture": "seated", "facing": "towards:B", "turn": {"to": "towards:prop_2", "label": "A turns to prop_2"}},
    {"name": "B", "pos": [0, 0.8], "posture": "standing", "facing": "towards:A",
     "moves": [{"to": [2.6, 0.9], "via": [[1.4, 1.4]], "facing": "towards:A", "posture": "standing", "label": "B crosses to prop_2"}]}
  ],
  "lights": [
    {"type": "window", "name": "light_1", "direction": "N", "target": "A", "pos": [0, 2.6], "label": "<source>, <side>, <hard/soft>"},
    {"type": "lamp", "name": "light_2", "direction": "W", "target": "B", "pos": [-2.6, 0.8], "label": "<source>, <side>, <hard/soft>"}
  ],
  "axis": ["A", "B"],
  "eyelines": [{"from": "A", "to": "B", "label": "<line or action>"}],
  "notes": ["one line per beat or anything worth a line in the legend"],
  "shots": [
    {"label": "wide", "size": "wide", "lens": 35, "pos": [2.4, -4.2], "dir": "towards:prop_1"},
    {"label": "A close-up", "size": "cu", "lens": 85, "target": "A", "from": "front-right"},
    {"label": "over A onto B", "size": "ots", "lens": 50, "over_shoulder": "A", "shoulder": "right", "target": "B", "highlight": true},
    {"label": "B after the cross", "size": "mcu", "lens": 50, "target": "B@1", "from": "front-left", "axis": ["A", "B@1"]}
  ]
}
```

Every name and label above is a placeholder. The example only shows the syntax of each field; never carry its props, positions or colours into a real scene.

Field reference:
- **ground**: floor colour (hex). Pick one that fits the location (wood, tiles, asphalt, grass); the engine default is a neutral grey.
- **Angles** (`facing`, `dir`, `light.direction`, `turn.to`, move `facing`, compass `from`): map degrees counter-clockwise from +x (E 0, N 90, W 180, S 270), a compass string (`"N"`, `"SE"` …) or `"towards:<name>"` (a character, a named prop, a named light, `light` for the key light, or a move position `A@1`).
- **References**: a character name, a prop or light `name`, `light` (the key light), a list of names (their centre), or `NAME@k` — character NAME's position after move step k (1-based). They are valid in `target`, `over_shoulder`, `relative_to`, eyelines, light `target`, `towards:` and axes.
- **props**: `rect` (pos, size [w, h], rotation, color, label), `circle` (pos, radius), `band` (two points + width; drawn as an endless strip — roads, paths, walls, windows; `dark_label: true` for light-coloured bands).
- **characters**: `pos`, `facing`, optional `posture` (free text, shown next to the name), optional `color`, optional `turn` {`to`, `label`} for a change of facing in place, optional `moves` — steps in order, each {`to` (point or reference), optional `via` (waypoints), optional `facing` (default: direction of travel), optional `posture`, optional `label` (goes in the legend)}. Each step is drawn as a path to a ghost position labelled `A1`, `A2` ….
- **lights**: a list; the first is the key light. Each: `type` `sun` | `window` | `lamp`; `direction` it comes from; `target` it hits; optional `pos` to pin the icon at the physical source (windows, lamps, practicals); optional `name`; `label`. A single `"light": {...}` object is also accepted.
- **axis**: the two references that define the 180° line. The first shot sets the allowed side. A shot can carry its own `axis` (e.g. after a move); the first shot using that axis sets its side.
- **shots** — placement, in priority order:
  - `pos` (+ optional `dir`): exact position. If it crosses the axis it is drawn red and reported.
  - `over_shoulder`: name, plus `shoulder` `"right"`/`"left"` and `target`: camera ~1 m behind that shoulder looking at the target.
  - `from` relative to the target character's facing: `front`, `front-left`, `front-right`, `left`, `right`, `behind`, `behind-left`, `behind-right` (`relative_to` to use another character; `relative_facing: "turned"` to use the facing after `turn`; a `NAME@k` target uses the facing after that move). Or `from` as a compass direction from the target.
  - nothing: placed on the line from the target toward the first camera.
  Auto-placed shots that land on the wrong side of the axis are mirrored across it and reported. `allow_cross: true` keeps a deliberate cross; `ignore_axis: true` skips the check for that shot.
  - Other fields: `label`, `size` (`wide`, `full`, `medium wide`, `medium`, `mcu`, `cu`, `ecu`, `insert`, `ots`, `establishing`), `lens` (mm), `height` (`eye` default, `low`, `high`, `overhead` — legend only), `move` (`static` default; `push in`, `dolly out`, `truck left/right`, `pan left/right` draw an arrow), `axis` (per-shot axis), `highlight: true` for the one shot that matters most.

A spec error (unknown reference, bad angle) stops the engine with one `spec error: …` line; fix the spec and run again.

## Limits — say these when relevant

- The map shows space from above. It does not show what each frame looks like; for framing and composition, draw frames from each camera's point of view.
- A map solves space, not time. It cannot tell whether the cut rhythm will feel rushed.
- One floor level. Camera height and tilt are legend text only; stairs, balconies and multi-storey blocking are not drawn.
- Moves are drawn as paths with end positions, not timed animation of the characters. The axis is checked at starting positions unless a shot sets its own.
- Cameras farther away than the map can show are pinned to the map edge on their true line, and the legend gives the real distance.
- At most about 8 cameras stay readable on one map; split longer scenes into several maps.

## Setup (once per environment)

The engine runs on [ManimGX](https://github.com/academa-labs/manimgx). Its dependencies (Python ≥ 3.13, `manimgx`, `numpy`, a bundled ffmpeg) are declared inside the script, and `uv run` installs them on first use. Only `uv` is needed:

```bash
command -v uv >/dev/null || { curl -LsSf https://astral.sh/uv/install.sh | sh; export PATH="$HOME/.local/bin:$PATH"; }
```
Do not install the `manim` package, LaTeX or system ffmpeg for this skill. Without a GPU, ManimGX renders on the CPU (bundled lavapipe). `no GPU adapter` means a sandbox hides the GPU: run outside the sandbox.
