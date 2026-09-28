---
name: vg-storyboard
description: Use when building the storyboard panel and first/last frames for each AI shot — trigger phrases like "build the storyboard", "storyboard panel", "generate first frame", "generate last frame", "check shot continuity", "style frames", "look review", "approve the look", "animatic", "sequence review", "approve the visuals", or whenever a shot's `storyboard`/`first_frame`/`last_frame` fields are still null.
---

# vg-storyboard

`vg-reference-sheets` has already produced the character/location/product sheets. This skill
generates one storyboard panel per AI shot from those sheets, then decides — per shot — whether a
separate first frame and a last frame are worth generating. The next skill, `vg-video-prompt`,
writes the motion prompt that animates between them. Prompt formulas are in `vg-image-prompt`;
running generation safely is in `vg-image`. There is no `vg` on PATH — commands here run as
`python3 2_Tools/vg/vg.py <command>`.

## Look review first (style frames)

Storyboard and frame images are refused until the human approves the look. Order:

1. Write or refine the `look.style_frames[]` prompts with `vg-image-prompt` (use: "style frame, the
   look of the whole reel"; name the world, light and grade from the `look` block verbatim).
2. `vg image -p P --stage look` (also builds any character sheet a style frame refs). Look at every
   frame yourself.
3. `vg board -p P`; send the human the style frames and the look text. Ask one question: "Is this
   the look of the whole reel?" Fix what they flag, regenerate, show again.
4. On their explicit "approved": `vg approve look -p P`. Never before.

From then on the tool adds the approved style frames as refs to every storyboard, first and last
frame (and to location/product/other sheets); set `"look_refs": false` on a shot that must not
inherit them, such as a flat map graphic. Keep prompts consistent with the look text.

## Frames decide the video

- **Images first, and choose stills by their light.** A still with the wrong light, a plastic face
  or an invented detail becomes a bad clip; no video prompt rescues it. Regenerate the still instead.
- **Real places start from real photos.** A property room's first frame is the client's photo
  (category `room_reveal`), not a generated interior (`vg-scene/references/property-tour.md`).
- **One world:** every frame at the look's time of day, sun direction and grade. Compare frames side
  by side on the board before the sequence review; a frame that breaks the light is redone now.
- **Bake stubborn looks into the frame** (grade, lens character) instead of hoping the video prompt holds them.
- **Plan the cut into the frame:** end one shot and start the next on the same gesture or direction
  of travel when they cut together; a first + last frame pair can hide a transition in motion.

## Storyboard panel

One panel per AI shot, `9:16`, image-to-image from whichever sheets that shot actually needs —
usually the character portrait/turnaround plus the location plate, sometimes the product sheet.
Refs are picked per shot, not copied from the previous shot. Frame the panel at the **start** of
the shot's action, not its climax — the video model animates forward from this frame:

| Shot intent | Panel should show |
|---|---|
| she lifts the bottle | bottle still on the desk, hand entering frame |
| she turns to camera | head still turned away |
| she unscrews the cap | cap still on |

Leave headroom in the frame for whatever the shot will move into (a push-in needs room to push
into; a turn needs room on the side she'll turn toward).

```bash
python3 2_Tools/vg/vg.py image -p P --stage storyboard
```

## First frame

Write `first_frame` one of two ways:

- **`{"from": "storyboard"}`** — reuse the panel as the first frame. Free, no extra generation.
  This is the default: use it whenever the panel's framing is already exactly where the video
  should start.
- **A separate `{prompt, refs}`** — only when the panel proved the composition but needs a fix it
  didn't nail (a drifted hand, a product angle, a detail the video needs sharper than the panel
  delivered). Refs the panel plus whatever sheet corrects it; describe only the change.

Most `frames`-mode shots (b-roll, product, location) can reuse the panel directly. Most
`character`-mode shots can too, unless the panel's face drifted and needs one more correction
pass before it becomes the identity reference sent to the video model.

## Last frame

`last_frame` is `null` by default. Only generate one when the shot's motion has a genuinely
different end state worth pinning down:

| Generate a last frame for | Skip it for |
|---|---|
| a camera move (push-in, pull-out, pan) that ends on a different composition | a static talking-head / character-mode shot with no camera move |
| a reveal (product opened, result shown) | a shot that's mostly one continuous gesture with no distinct end state |
| a transition shot feeding the next shot's first frame | any shot where "the model will figure out the middle" is good enough |

When generated, `last_frame` is i2i **from the first frame**, refs `[first:<ShotId>]`, and the
prompt describes only what changed by the end — not the whole scene again. See the last-frame
template in `vg-image-prompt/references/templates.md`.

`last_frame` is only ever sent to the video model in `frames` mode. Generating one for a
`character`- or `text`-mode shot still costs an image but the tool never uses it (`vg validate`
warns "only frames mode sends a last frame; it will be unused") — don't build one there.

```bash
python3 2_Tools/vg/vg.py image -p P --stage frames
```

If every shot's first/last frame is already generated or reuses its storyboard panel, this prints
`Nothing to generate at stage frames` and exits `0` — that's the normal, done state, not an error.

## Continuity between consecutive shots

When a cut between two AI shots should feel continuous (the same motion carrying across the
edit), make the next shot's first frame echo the previous shot's last frame:

```json
"first_frame": { "prompt": "same position and framing as the reference, ...", "refs": ["last:S01"] }
```

This is a deliberate choice, not a default — only do it where the beat sheet actually wants a
continuous feel (e.g. one scene whipping straight into the next). Most cuts in short-form are hard
cuts between unrelated framings and don't need this.

## Continuity QC checklist

Run this across every shot in a scene before moving to `vg-video-prompt`:

| Check | Failure looks like |
|---|---|
| Identity string reused verbatim across shots with the same character | face/features subtly change shot to shot |
| Environment matches across shots in one scene | walls or surfaces change colour/layout |
| Light direction consistent | window light on the left in S01, right in S02 |
| Colour temperature consistent | warm morning light in one shot, cool fluorescent in the next |
| Wardrobe consistent (or the change is motivated) | outfit changes with no story reason |
| Product state moves forward only | opened in S02, sealed again in S04 |
| Time of day consistent | daylight in S02, night in S03 with no transition beat |
| Hands/props continuity | holding the product in S03, empty-handed in S04 with no action explaining it |
| At least one direct-to-camera shot in the scene | a scene made only of b-roll/product reads as an ad |

Fix conflicts here — don't defer them to the edit.

## After frames exist

```bash
vg board -p P
```

Open `Board_<Project>.html` and look at storyboard + frames side by side.

## Sequence review (the whole reel as images)

Before any video prompt, the human approves the whole reel as images:

1. Draft `6_Edit/Edit_Spec.json` now (see `vg-edit`): timing, on-screen text, map, photos, captions.
   Text and placement are part of what the human approves.
2. `vg edit animatic -p P` (free, local): the reel as stills at edit timing with captions and
   graphics, and the planned narration, music and sound effects. `vg board -p P` rebuilds the filmstrip.
3. Watch the animatic yourself first, as a viewer, not a checker: one world and light across every
   shot? Does the story pay off the hook? Does the product get screen time? One graphic style, off
   faces? Nothing that looks like a placeholder?
4. Send the human the animatic and the board. Fix only the beats they flag, regenerate, re-render
   the animatic (`approve visuals` refuses an animatic older than the current images), show again.
5. On their explicit "approved": `vg approve visuals -p P`. Then hand off to `vg-video-prompt`.

**Show both reviews on the review page.** Instead of sending images in chat, run `vg review -p P` in
the background and tell the human it is open: they switch takes, write a note per picture and click
Approve look / Approve reel themselves. When they click Done you get `GATE`, `NOTE` and `NEXT` lines;
treat each `NOTE` as a prompt instruction for that exact card, regenerate, re-render the animatic for
the sequence review, and open the page again. Never click its buttons yourself.

## Common mistakes

| Mistake | Fix |
|---|---|
| Reusing the previous shot's refs without checking they still apply | pick refs per shot |
| Panel framed at the action's climax | reframe to the start of the action |
| A last frame generated for a static talking-head shot | skip it — nothing to pin down |
| First frame written from a fresh text prompt instead of `{"from": "storyboard"}` or the panel's refs | reuse or i2i from the sheets, always |
| Continuity checklist skipped because "it'll probably be fine" | run it — it's the cheapest QC pass in the pipeline |
