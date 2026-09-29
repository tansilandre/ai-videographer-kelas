---
name: vg-video-prompt
description: "Use when writing or reviewing a shot's `video_prompt` field in Shotlist.json — the motion prompt that drives image-to-video generation on Veo 3.1 Lite, Seedance 1.5 Pro or Gemini Omni Flash, or a Kling AI Avatar Pro lipsync shot that says the reel's own narration — including camera moves, performance and micro-motion, dialogue and lip-sync for talking shots, audio, b-roll/aerial/property/transition motion, and the dialogue fit check that sets `duration`. Trigger phrases: \"generate the video prompt\", \"write the video prompt\", \"make it move\", \"camera move\", \"dialogue fit\", \"the motion looks stiff\", \"lip-sync is off\"."
---

# vg-video-prompt

Pipeline: vg-setup → vg-scene → vg-reference-sheets → vg-storyboard → **vg-video-prompt** →
vg-video → vg-edit, orchestrated by vg-director. The frames are already approved by the human
(`vg approve visuals`). This stage writes each shot's `video_prompt` in `1_Script/Shotlist.json`:
the instruction that turns an approved still into 4–10 seconds of motion. `vg-video` spends the
credits. Run `python3 2_Tools/vg/vg.py validate -p <project>` after every edit.

Knowledge behind this skill: `4_Docs/Research/2026-09-28_Higgsfield_Learnings_v1.0.md`.

## The one rule

**The frame carries the look. The prompt describes only what changes: motion, camera, performance,
sound, timing.** Never re-describe the face, wardrobe, room or product in the frame; two competing
descriptions make the model drift. For a property shot animated from a real photo, the prompt names
the camera move and the light, nothing about the room.

## Which model, and what it wants

The shot's model is `shot.model` or `models.video` (`vg models`). Write for that model.

| Model | Inputs we send | Write it like this |
|---|---|---|
| **Veo 3.1 Lite** (`veo-3-1-lite`, our default) | first frame, optional last frame; speech and sound generated from the prompt | Order: subject action → camera → composition/lens → light/ambience → audio. Dialogue in quotes with a delivery tag. One speaker per clip. No voice lock: repeat the same voice descriptor verbatim in every clip. With first + last frame, use 8 s unless a 4/6 s pilot proved otherwise. |
| **Seedance 1.5 Pro** (`seedance-1-5-pro-audio`, silent variant `seedance-1-5-pro`) | first (+ last) frame; 4/8/12 s | Its vendor lists Indonesian lip-sync: the candidate for talking heads (pilot first). State the dialogue, the language, the sound effects and the music mood (or "No music"). 50–80 words. |
| **Kling AI Avatar Pro** (`kling-ai-avatar-pro`, lipsync mode) | first frame + a cut of the reel's approved narration; 1080p, 16 credits per second | Talking lines in an audio-first reel. The audio drives the lips, so the prompt only directs gaze, expression and small movement (see "Lipsync mode" below). Live-tested 2026-09-29: 4/4 first-try, ~2.5 min each. |
| **Gemini Omni Flash** (`gemini-omni-flash-1-1`) | `frames` mode (hard first frame, silent anchor) or `character` mode (character + voice ids) | Character mode failed 9/9 for us; prefer frames. No documented prompting dialect; use the general rules below. |

`style_lock.video` from `Shotlist.json` is appended by the tool to every prompt (unless the shot sets
`"style_lock": false`). Make it the reel's **style prefix** written as rules (see `vg-scene`), and
do not repeat it by hand.

## How a video prompt is built

Short and physical: **50–100 words of body** (the style prefix is added on top). For a busier shot,
use short labelled lines in this order; skip any that the shot does not need:

```
CAMERA: <one named move, its speed or duration, its end frame, then a hold>
ACTION: <the one physical beat, present tense, ending in a visible completed state>
PERFORMANCE: <micro-life and eyes; physics, not emotion words>
AUDIO: <dialogue block, one dominant sound tied to the action, ambience; "No music, no subtitles.">
LOCKS: <positive constraints: what must stay as it is>
```

Full layer guide and worked examples: `references/prompt-formula.md`. Camera moves with their
wording: `references/camera-moves.md`. Recipes per shot category (talking head, walkthrough,
threshold reveal, detail, aerial, transition…): `references/shot-categories.md`.

## Rules that make the difference

1. **Measurable words only.** Could a camera, light meter or stopwatch measure it? "hard key 45°
   from camera left, about 4000 K" not "cinematic lighting"; "over 6 seconds" not "slowly";
   "107° rectilinear ultra-wide, verticals straight" not "wide". Delete: cinematic, epic, stunning,
   breathtaking, masterpiece, 8K, ultra-realistic, premium, luxury, beautiful.
2. **One camera move per clip**, with an **end frame** ("…until the window fills the frame") and a
   **hold** of 1.5–2 s at the end. No end frame → the camera drifts or reverses. A compound move
   only as timed phases ("rises 0–3 s, holds, then pushes in 4–8 s").
3. **One action beat per 4–6 s** (1–2 in 8 s). End it in a **completed state** ("…and sets the cup
   down, hand resting beside it"); chain actions in one direction, or the model plays the action
   back to fill the clip.
4. **Micro-life on people:** a visible micro-event every 1–2 s (blink every 2–4 s, a breath before
   speaking, a weight shift before moving, hair and fabric lagging a fraction behind). **Eyes need a
   task** ("checks whether the viewer is following"); dead eyes are the first AI tell.
5. **Physics, not emotion labels:** "jaw relaxes, a small exhale through the nose, eyes crinkle"
   rather than "she looks happy". Give a presenter a physical task and let them talk over it.
6. **Walking is the hardest move:** write it as physics (heel strikes, feet strictly alternate, one
   foot always on the ground) and use the same absolute pace in every clip of one walk.
7. **Hands:** frame waist-up, or state the hand count and what each hand does. One simple hand action.
8. **Positive constraints, not negative lists.** "face stays identical, verticals stay straight,
   light stays constant" beats "no morphing, no warping". A ban only where the model's default is the
   failure (music, subtitles, text, slow motion in action). `references/avoid-list.md`.
9. **No text in the generation.** On-screen words are added in the edit.

## Dialogue and lip-sync (talking shots)

Build the audio line in this order:

```
AUDIO: <voice descriptor, verbatim from the character>, in <language and register, e.g. casual Jakarta
Indonesian>, <delivery>: "<exact line from the shot's dialogue field>" — only this line, nothing else.
<Her physical action while speaking>. <Facial reaction after the line>. Anyone else in frame: lips at
rest, jaw closed. <Room acoustic / ambience>. No music, no subtitles.
```

- **Fit rule (tool-enforced):** `characters ≤ (duration − 0.7) × 10.5`; `"duration": "auto"` picks
  the shortest fitting duration. **Also a floor:** a line far shorter than its clip makes the model
  invent filler words or repeat the line. If the line uses less than about half the budget, shorten
  the clip, add a scripted pause ("she pauses, then…"), or give the remaining time a silent action.
- **Spell numbers and abbreviations the way they are said** ("satu koma tiga M-an", "er-es"); the
  caption can keep "1,3M-an". Give unusual names a phonetic spelling.
- **Lip-sync works best at:** 3–8 s lines, medium close-up or tighter, one face, locked camera or a
  slow push-in, no nodding or head-turn words, speech slightly slower than natural.
- **Keep lips out of most shots.** One or two short on-camera lines per reel; everything else is
  voice-over over b-roll (people in b-roll: "mouth closed, not speaking"). Longer narration is a
  voice-over track in the edit, not speech generated inside clips.
- Never replace a clip's lip-synced voice with a different TTS voice afterwards: the mouth was
  animated for the original audio, and the result reads as a bad dub.

### Lipsync mode: the reel's own narration on camera

When the narration is recorded first (audio-first edit), a talking shot says that exact audio instead
of generating its own voice: `"mode": "lipsync"`, `"model": "kling-ai-avatar-pro"` and a `lipsync`
window on the narration file (`shotlist-schema.md`). One voice for the whole reel, no dubbing.

- **Window:** start 0.2–0.4 s before the first word (the mouth opens on the breath) and end in the
  pause after the line. The edit then trims the clip (`in`/`out`) to its segment.
- **Eye contact is made in the first frame, not the prompt.** A first frame where she looks away
  gives a clip where she talks to herself. Make an eye-contact selfie frame: phone at arm's length,
  eyes fully on the lens, lips slightly parted as if starting to talk.
- **The prompt directs gaze and manner only** (the audio drives the words): "She talks directly to the
  viewer through the phone camera: her eyes stay on the lens the whole time and never look down or
  away, like talking to a friend on a video call; an open friendly expression, small natural nods,
  quick natural blinks. Her face, hair, outfit, the background and the light stay exactly as in the
  picture." A walking selfie works too: she can walk while she talks.
- **Check the clip against its sound**: loudness every 0.1 s next to a mouth close-up at the same
  moments. Lips close on m/b/p, round on u/w, open on the breath before a line; eyes mostly on the lens.

## Audio

Four layers: dialogue · **one dominant sound per action**, tied to what is visible ("heels on
polished tile as she steps in") · ambience, at most 2–3 elements in one sentence reused verbatim in
every clip of the same space · music never in the video model ("No music, no subtitles."). Name
the room acoustic ("small tiled room, slight echo").

## Self-check before saving a `video_prompt`

- [ ] Written for the shot's model (table above); nothing re-describes the frame
- [ ] One camera move with speed/duration, end frame and a hold
- [ ] One action beat per 4–6 s, ending in a completed state
- [ ] People: micro-life, an eye task, physics instead of emotion words; hands handled
- [ ] Measurable words; no slop words; no on-screen text asked of the model
- [ ] Talking shot: audio block in order, "only this line", mouth states for others, fit rule and
      floor checked, numbers spelled as spoken
- [ ] Sound: one dominant sound per action, ambience sentence shared across the scene, "No music"
- [ ] Positive LOCKS instead of a long Avoid list
- [ ] `vg validate -p <project>` passes; for a shot whose look differs from `style_lock.video`
      (aerial, concept render), `"style_lock": false` is set and checked with `vg video --dry-run`

When a clip comes back wrong, use `references/diagnosing.md` (symptom → cause → fix, and the stop
rule: two identical failures mean rewrite the prompt or fix the still, never a third identical try).

## References

- `references/prompt-formula.md` — every layer, word banks, worked examples per category
- `references/camera-moves.md` — named camera moves with speed, easing, end frame, per-model notes; the room → move map for property tours
- `references/shot-categories.md` — recipes per shot category
- `references/diagnosing.md` — symptom → cause → fix, stop rule, salvaging takes
- `references/avoid-list.md` — positive locks, and the few bans worth writing
- `references/hook-library.md` — spoken and visual hook structures for the opening shot
