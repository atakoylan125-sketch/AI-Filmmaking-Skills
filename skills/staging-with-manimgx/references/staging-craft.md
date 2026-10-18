# Staging craft

Read this when you choose cameras (Coverage, or a thin Shots slot), write the plan, or check the result. It explains *why* a camera goes where it goes. It is placement knowledge only, and it is not tied to any camera system, video generator or production tool. Like the rest of the skill, the examples below are generic: never carry them into a real scene.

## Two kinds of person

- **They named the shot or the geometry** ("85 mm close-up on her, from the window side", "over his left shoulder"). Take it as given. Fill only missing numbers with defaults and list them as assumptions. Do not run a question round on someone who already knows their shot.
- **They brought a scene, a beat or a feeling** ("how do I cover this?"). Choose the cameras yourself with the tables below, and in the plan explain each choice in one line so they learn why.

Both mistakes are bad: interrogating a professional, and handing a beginner a list of cameras without the reasons.

## Shot size: distance decides what the shot is about

| Size | What it shows | Use it when |
| --- | --- | --- |
| Wide / establishing | the whole place, everyone, scale | opening the scene; after someone enters or leaves; showing a figure small in a space |
| Full | whole bodies, their relation to the floor and props | movement, arrivals, choreography |
| Medium / medium wide | waist or knees up, gestures, the prop in hand | someone starts doing something |
| Medium close-up (MCU) | chest up, attention and intent | someone listens, decides, focuses |
| Close-up (CU) | the face | the inner turn of the scene |
| Extreme close-up (ECU) / insert | an eye, a hand, an object | a detail the action depends on |

**Coverage escalation:** go wide → medium → close as attention narrows or tension rises, and pull back to a wide to release it or to re-establish the geography after a move. A cut that repeats the previous shot's size and angle on the same subject adds nothing; change size or angle by a clear step.

**A new size is a new camera position.** On the map, a closer shot of the same person is a different camera standing closer (or with a longer lens), not the same camera zooming. Draw it as its own shot.

## Camera height: height is power

The map draws height as legend text only, so state the reason for any height other than eye level.

| Height | Reads as |
| --- | --- |
| Eye level (default) | neutral, with the character |
| Low (below the eyes, looking up) | power, threat, monumentality |
| High (above, looking down) | vulnerability, being watched, a pattern from above |
| Overhead / top-down | the layout itself; objects on a table |

A seated character's eye level is about 1.2 m, a standing one's about 1.6 m. When one person sits and one stands, choose whose eye level each single uses; that choice is part of the shot.

## Lens: what each focal length does to space

| Lens (full frame) | Horizontal FOV | Effect |
| --- | --- | --- |
| 24 mm | ≈ 74° | lots of space; a figure inside its world; stretches depth |
| 35 mm | ≈ 54° | natural width; "you are there" default for wides and walking shots |
| 50 mm | ≈ 40° | close to the eye; honest mediums and over-the-shoulders |
| 85 mm | ≈ 24° | compresses depth, isolates a face; singles and inserts |
| 135 mm | ≈ 15° | strong compression; watching from far away |

A longer lens must stand farther back for the same size, which pushes the camera across the room on the map. If it would land outside a wall, either choose a shorter lens or say the camera is outside the room (e.g. through a window).

## Placement laws

1. **Shoot through something when the space offers it.** A shoulder, a door frame, glass, a shelf, another person in soft foreground. It gives depth and makes the frame feel found rather than set up. On the map this means the camera sits behind that object; an over-the-shoulder is the everyday case.
2. **Use the space's own lines.** A corridor, a counter, a row of windows, a road. Put cameras where those lines lead the eye towards the subject rather than across it.
3. **Keep the subject off the dead centre** unless the shot is symmetrical on purpose. When you write the shot descriptions, say which side of the frame each person is on.
4. **Every camera move needs a motive** — push in because attention sharpens, pull back because the space is revealed, track because someone walks. One move per camera. Keep the camera's move separate from the character's move, and say which one carries the shot.
5. **Cut on an event** (someone stands, a door opens, an object is picked up), not on a timer. When a shot exists for a beat, name the beat in its label or in the notes.

## Spatial continuity

- **World side is not screen side.** The map is world space: a window on the north wall stays on the north wall in every shot. Screen side depends on the camera. When a camera turns around (a reverse), what was frame-left becomes frame-right, and the key light that lit one cheek from frame-left may now come from frame-right. That is correct: the light did not move. Never move a window, door or lamp to make a frame prettier.
- **The 180° line keeps looks and moves readable.** Cameras on one side of the line keep A looking frame-right and B looking frame-left in every shot. A deliberate cross is allowed when it is marked and the reason is stated; the engine reports any shot that crosses.
- **Entry and exit directions.** Someone who leaves frame-right in one shot should enter frame-left in the next shot of their journey. Doors and paths on the map fix where people come from; check that every move actually reaches its door or mark.
- **Objects that matter keep their place and orientation** between shots unless someone moves them on screen. Give each one a named prop so cameras and lights can refer to it.
- **After a move the geometry changes.** Cover the new position, and give the shots after the move their own axis if the pair or their side changed.

## Offering alternatives

In the plan, after the cameras you chose, offer **two or three alternatives the person did not mention**, each in one line with its trade-off. For example: an over-the-shoulder instead of a clean single (more relationship, less isolation); a high wide instead of an eye-level wide (shows the pattern of the room, distances the viewer); one continuous shot with a move instead of three cuts (keeps real time, gives up the edit). They are suggestions; apply one only if the person picks it.

## Plain-language shot descriptions

After approval, each camera gets a short neutral description that anyone can read: a director of photography, an editor, a storyboard artist, or someone using any image or video tool. It describes the planned frame. It is not a prompt for any particular model and it contains no style or mood words. Build each one from the approved spec and the `frame` data in the report (who is in view and on which side of the frame, and where each light comes from relative to the frame):

```
Shot <n> — <label>
<size>, <lens> mm, <height>, <move or "static">.
Camera: <where it stands, in metres and relative words> looking towards <subject>.
In frame: <who and what is visible, which side of the frame each is on, what is in soft foreground>.
Behind them: <what the background of this shot is, from the Surroundings slot>.
Light: <each source and the frame side it comes from: frame-left, frame-right, into the lens, from behind the camera>.
Continuity: <axis side, eyeline direction (A looks frame-right), entry/exit direction, any mirrored or crossing warning>.
```

Use the report's `frame` data for left/right instead of working it out in your head; mirror mistakes are the most common error here.

## Final spatial check

Before you deliver, confirm:
- left and right are consistent across all shots, and every eyeline direction is clear;
- every entry and exit is possible through a door, an edge of the map or a path that exists;
- each move reaches its mark and every later shot covers the new position;
- the key light comes from the same physical source in every shot, even where its screen side changes;
- no camera stands inside a wall or a prop unless it is deliberately shooting through a window or doorway.
