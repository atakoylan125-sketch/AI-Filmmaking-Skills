# Walkthrough: night laundromat

An original scene, written for this repository, that shows the whole workflow end to end: a thin brief, the guided intake, the plan shown for approval, and the rendered map. The questions and answers below are an illustration of the procedure in `SKILL.md`, written by hand; they are not a recorded agent transcript. Like every file in `examples/`, the scene is a demo, not a template.

Files: [`night-laundromat.json`](night-laundromat.json) (the approved spec) · rendered map: [`docs/media/poster.png`](../docs/media/poster.png)

## 1. The brief

> Late at night in a laundromat. A woman is waiting for her wash. A man comes in, empties a dryer and finds a red shirt that isn't his. She walks over and they talk about it.

Scored against the seven slots: Location is named but not sized. Positions, Orientation, Light, Surroundings and Shots are missing. Beats are partly given (he comes in, she walks over). Location and Positions are not both missing, so the first message can carry three questions.

## 2. Intake, message 1 (structure)

1. **Where is the woman while she waits?** *Why: it sets where the 180° line will run once they meet.*
   a. Seated on a bench against a side wall **(recommended: gives her somewhere to rise from)**
   b. Standing at the folding table
   c. Sitting on top of a washer
   d. You decide
2. **What is the room like, and where is the street?** *Why: without it the map can come out mirrored.*
   a. Narrow shop: washers along the back wall, dryers on the right, glass storefront and door at the front **(recommended)**
   b. Square room, street door on the side wall
   c. You decide
3. **How do you want to cover it?** *Why: these are the cameras.*
   a. I'll give you a list
   b. Classic coverage: a wide, two over-the-shoulders, a close-up, plus his entrance and an insert of the shirt **(recommended)**
   c. One continuous shot
   d. You decide

Answers: **1a, 2a, 3b**.

## 3. Intake, message 2 (light and movement)

1. **Where does the main light come from?** *Why: it decides which side of each face is lit.*
   a. Overhead fluorescent tubes **(recommended: the hard, flat light the place really has)**
   b. The street through the glass
   c. You decide
2. **Where do they end up?** *Why: moves are drawn as paths and set the axis for the dialogue.*
   a. He brings the shirt to the folding table; she rises from the bench and meets him there **(recommended)**
   b. She stays seated; he comes to the bench
   c. You decide

Answers: **"You decide"** for the light, **2a** for the movement. Two messages, five questions; nothing about the story or the dialogue was asked.

## 4. Plan shown for approval

The agent runs `--check`, renders `--preview`, looks at the PNG, then shows it with this plan:

- **Environment**: 7 × 5.5 m. A row of washers on the back (north) wall, a stack of dryers on the right (east) wall, a bench on the left (west) wall, a 1.8 × 0.8 m folding table in the middle, glass storefront along the front (south) with the door at the front right.
- **Characters**: MIRA is seated on the bench, facing east. JONAS is standing just inside the door, facing north. Moves, in order:
  1. JONAS walks to the dryers.
  2. JONAS brings the shirt to the east end of the table.
  3. MIRA rises and stands at the west end of the table, facing him.
- **Light**:
  - L1 (key): overhead fluorescents above the table, hard. *(assumed)*
  - L2: a red neon sign outside the glass, lighting MIRA at the table from her right. *(assumed)*
  - L3: the open dryer drum, a soft glow on JONAS at the dryers. *(assumed)*
- **Cameras** (all static, eye height unless noted):

  | # | Shot | Lens | Where it stands | What it sees |
  | --- | --- | --- | --- | --- |
  | 1 | wide | 24 mm | 4.5 m south, outside the glass | the whole room, both of them |
  | 2 | medium wide | 35 mm | 1.8 m west of JONAS at the door | JONAS coming in |
  | 3 | over-the-shoulder | 50 mm | behind MIRA's right shoulder | JONAS at the table |
  | 4 | over-the-shoulder | 50 mm | behind JONAS's left shoulder | MIRA at the table |
  | 5 | close-up | 85 mm | 2.1 m front-right of MIRA | MIRA at the table |
  | 6 | insert | 85 mm | 1.4 m south of the shirt, high | the shirt on the table |

- **180° axis**: MIRA–JONAS at the table, after their moves. Every camera stays on the storefront side. No shot was mirrored.
- **Assumptions**: the room size, all three lights, the exact metre positions.

The person approved the plan without changes. The agent then rendered at `--quality h` and checked `night-laundromat.last.png` and the report (no warnings).

## 5. Reproduce

```bash
uv run skills/staging-with-manimgx/scripts/staging_render.py examples/night-laundromat.json --check
uv run skills/staging-with-manimgx/scripts/staging_render.py examples/night-laundromat.json -o night-laundromat.mp4 --preview
uv run skills/staging-with-manimgx/scripts/staging_render.py examples/night-laundromat.json -o night-laundromat.mp4 --quality h
```
