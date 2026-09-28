# The motion prompt formula, layer by layer

The deep-dive behind `vg-video-prompt/SKILL.md`. Use it when writing a `video_prompt` from scratch
or when a clip feels wrong. Rules here apply to all three video models in the registry (Veo 3.1
Lite, Seedance 1.5 Pro, Gemini Omni Flash) unless a line names one. Source and evidence levels:
`4_Docs/Research/2026-09-28_Higgsfield_Learnings_v1.0.md`.

Order inside the prompt: **camera → action → performance → audio → locks**. Keep the body to 50–100
words; the tool appends `style_lock.video` (the style prefix) after it. Earlier words weigh more,
so the thing the shot depends on most goes first.

---

## Layer 1 — Camera (one move, with an end)

Say the shot type, the one move, its speed or duration, where it ends, and the hold:

```
Handheld phone video at chest height, friend walking half a step behind her; the camera keeps
pace, then settles and holds for the last 2 seconds.
Slow lateral glide left along the kitchen counter over 6 seconds, ending with the island centred;
hold 1.5 seconds.
Locked-off tripod shot, no camera movement.
```

- Every move needs an **end frame**. Without one it drifts, overshoots or reverses.
- One primary move plus at most one texture ("slight handheld drift"). Never two primary moves.
- Speed as time or distance ("over 6 seconds", "about one metre forward"), never "fast".
- Field of view in degrees when it matters: 107° architectural ultra-wide (verticals straight, no
  fisheye), 84° wide, 63° normal-wide, 47° normal, 29° short tele.
- Named moves and their wording: `camera-moves.md`.

## Layer 2 — Action (one beat, ending in a state)

**One physical action per 4–6 s, present tense, ending in a completed, visible state.**

| Abstract (avoid) | Physical (use) |
|---|---|
| she demonstrates the product | she lifts it into frame, turns it so the front faces the lens, and holds it still |
| she talks about the house | she speaks to the lens, glances toward the window on the last words, and looks back |
| the drone shows the area | the camera glides forward 40 m above the rooftops and stops with the cluster gate centred |
| she opens the door | her hand presses the handle down, the door swings in to about 90°, and stays open |

- Chain actions **in one direction**. A clip with time left over plays the action back in reverse.
- For manipulation (opening, pouring, pressing), write the chain: what the object is → what holds
  it → where the force goes → how the material reacts → the end state. A verb alone gives a mime.
- Walking: heel strikes, feet alternate, one foot always down; the same pace in every clip of the walk.
- Marketing verbs (demonstrates, showcases, presents, elegantly) pull toward a staged ad. Avoid them.
- Two actions need two shots (or timed phases in an 8 s clip: "0–3 s …, 3–8 s …").

## Layer 3 — Performance (people only)

- **Micro-life:** a visible micro-event every 1–2 s: a blink every 2–4 s, a breath before she speaks,
  a weight shift before she moves, a loose strand of hair and the shirt moving a fraction behind her.
- **Eyes with a task:** "her eyes check the viewer's reaction after the price", "she glances at the
  window as if checking the light". Eyes reach a target before the head turns.
- **Physics, not labels:** "the corners of her mouth lift, eyes crinkle, a short exhale through the
  nose" instead of "she looks delighted". Emotion keeps inertia: breathing stays uneven after a big moment.
- **Business:** give her a physical task (a hand runs along the counter, she opens a blind) and let
  her talk over it; the moment she stops the task is the accent.
- UGC: slight off-lens glances, loose imperfect framing; avoid the fixed "endorsement smile" into the lens.

## Layer 4 — Audio

Talking shot:

```
AUDIO: <voice descriptor, verbatim from the character>, in casual Jakarta Indonesian, warm and
curious: "<exact dialogue line>" — only this line, nothing else. She keeps walking while she speaks,
then smiles on the last word. Anyone else in frame: lips at rest, jaw closed. Open-air street
ambience with distant traffic under her voice. No music, no subtitles.
```

- The quoted line equals the shot's `dialogue` field word for word (`vg validate` checks it).
- Name the language and register before the line; spell numbers and abbreviations as spoken.
- Non-speakers get a positive mouth state. "Listens without speaking" names speaking; don't use it.
- One speaker per clip. Lip-sync conditions: 3–8 s line, medium close-up or tighter, locked camera or
  slow push-in, no nodding or head-turn words.
- The fit rule caps the line; a line much shorter than the clip invites filler. Fill the time with a
  silent action or a scripted pause, or shorten the clip.

Non-talking shot:

```
AUDIO: footsteps on polished tile as the camera moves in; faint street sound through the window.
Nobody speaks. No music, no subtitles.
```

One dominant sound per action, tied to what is visible. Reuse the same ambience sentence in every
clip of the same space so the cuts don't jump.

## Layer 5 — Locks (positive constraints)

```
LOCKS: her face, hair and shirt stay identical to the first frame; verticals stay straight; the
light stays constant; the room keeps its layout.
```

Only a few short bans where the model's default is the failure: `No music, no subtitles, no
on-screen text.` Full guidance: `avoid-list.md`.

---

## Worked examples by category

### UGC talking head, Veo 3.1 Lite, 8 s, first frame only

```
Handheld selfie video, arm's length, parked car with the engine off; slight sway from her arm, the
framing never changes. She speaks to the lens with genuine curiosity, one eyebrow lifting on the
question; on the last words she glances at the side window and back to the lens, then holds a small
smile for the final 1.5 seconds. Blink every few seconds, a breath before she starts.
AUDIO: warm, clear young woman's voice in her late twenties, casual Jakarta Indonesian, curious:
"Rumah Kota Harapan masih ada yang satu koma tiga M-an? Aku cek langsung." — only this line, nothing
else. Quiet car cabin, no engine. No music, no subtitles.
LOCKS: her face and shirt stay identical to the first frame; the car does not move.
```

### Property room from a real photo, Veo 3.1 Lite, 6–8 s

```
Slow push-in of about one metre over 6 seconds from the doorway toward the living room window,
eye height 1.5 m, 107° rectilinear view, verticals stay straight; the move eases in and out and
holds for the last 2 seconds with the window centred. Late-afternoon sun from the window, about
5000 K, soft shadows across the floor.
AUDIO: quiet room tone, a faint bird outside. Nobody speaks. No music, no subtitles.
LOCKS: every wall, door, furniture piece and material stays exactly as in the first frame; nothing
is added or removed.
```

(Do not describe the room. The photo is the room.)

### Threshold reveal between two spaces, first + last frame, 8 s

```
Steady forward walk through the doorway at walking pace, the camera crossing the threshold at 3
seconds and continuing into the bright kitchen, easing to a stop with the island centred as in the
last frame; hold 1.5 seconds. Warm hallway light gives way to cool daylight in the kitchen.
AUDIO: two soft footsteps on wood, then tile. No music, no subtitles.
LOCKS: both rooms keep their layout and materials from the two frames.
```

### Detail insert (material or fixture), Seedance 1.5 Pro silent, 4 s

```
Locked-off macro shot, 29° view, on the brushed-steel smart lock; a finger presses the keypad once,
the green light blinks, the handle turns down and stops. Raking light from the left shows the
brushed texture.
LOCKS: one hand, one finger; the lock and door stay identical to the first frame.
```

### Aerial establishing, Veo 3.1 Lite, 8 s (`"style_lock": false` if the prefix is handheld)

```
Aerial drone shot, 120 m, camera tilted 40° down; constant slow forward glide over the store roof
and across the toll road over 7 seconds, stopping with the green neighbourhood centred; level
horizon, no rotation. Bright mid-afternoon sun from the left.
AUDIO: wind and a distant traffic hum. No music, no voice, no subtitles.
LOCKS: buildings and roads keep their shapes; cars stay in their lanes.
```

### Lifestyle b-roll with the presenter, no speech

```
Friend-held phone at chest height walking backwards in front of her; she walks toward the lens at
an easy pace, heels landing first, one foot always on the ground; she glances left at the palm
trees, then back to the lens with a small smile. Mouth closed, not speaking. Hair and shirt move a
fraction behind her steps.
AUDIO: footsteps on paving, birds, distant traffic. No music, no subtitles.
```

---

## Diagnosing bad output

Full table and the stop rule: `diagnosing.md`. The five most common:

| Symptom | Fix |
|---|---|
| Looks staged / "AI ad" | shot label as a real camera situation (phone, friend holding it); delete slop words; micro-life |
| Camera drifts or reverses | add the end frame and a hold |
| Motion stiff or floaty | physics verbs, completed state, micro-events, one beat |
| Extra mumbled words | line too short for the clip; shorten the clip or add a silent action; "only this line" |
| Room warps | shorter, slower move; lateral glide instead of push-in; stop re-describing the room |
