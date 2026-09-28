---
name: vg-scene
description: Use when turning a client brief into a script, beat sheet, and shot list — trigger phrases like "generate scene", "write the script", "build the shot list", "plan the shots", or right after `vg new`, while Shotlist.json still has an empty shots[].
---

# vg-scene

This is the first creative skill in the pipeline: `vg-setup` confirms the environment and
`vg new` creates the empty project; `vg-scene` turns the client brief into
`1_Script/Shotlist.json`, the plan every later skill reads. The next skill,
`vg-reference-sheets`, generates the character/location/product sheets this skill lists in
`assets[]`. Field names below are exactly as defined in
`vg-director/references/shotlist-schema.md` — do not invent a field that isn't there.
`templates/Shotlist.template.json` in this skill's folder is a filled-in, valid worked example —
start from its shape (and its `rules[]`-vs-`shots[]` consistency) rather than from a blank object.

## What vg-scene owns

Fill these now: `project`, `title`, `client`, `format`, `models`/`image_defaults`/
`video_defaults` (only if they differ from `.env` defaults), `style_lock`, `rules[]`,
`characters[]`, `assets[]`, and every `shots[]` field **except** `storyboard`, `first_frame`,
`last_frame`, `video_prompt`. Those belong to `vg-reference-sheets`/`vg-storyboard` (the panel
and frames) and `vg-video-prompt` (the motion prompt) — leave them `null`. Running
`python3 2_Tools/vg/vg.py validate -p P` (`vg validate -p P` from here on) after this skill is
expected to still flag those as missing; that is fine. The goal here is zero errors in the
fields this skill owns: ids, `source`, `mode`, dialogue fit, and every ref inside `assets[]`.

## Step 1 — read the brief literally

Extract, per beat: what the viewer sees, the spoken/on-screen line, and — critically —
**source**: is this beat real footage the client will shoot, a motion graphic built in the edit,
or something we generate with AI? A brief usually states this explicitly (a table column, a
note like "real footage only" or "AI ok"). Never upgrade a `real` or `mg` beat to `ai` because AI
would be easier or cheaper — a real building, a real product unit, or a precise distance/map is
exactly the kind of thing a client brief marks `real`/`mg` on purpose, to avoid a fabricated
asset appearing in a paid ad. Only flip source if the brief explicitly allows it, or is silent
and the human confirms it in chat. One middle ground for an `ai` shot of a real place: its
`first_frame` can be image-to-image from an actual photo (`refs: ["file:0_Source/photo.jpg"]`)
instead of a generated plate — that keeps the real geometry. If no real photo is available, mark
the beat `source: real` or `mg` instead of guessing at a generated location.

## Step 2 — extract client rules into `rules[]`

Pull every constraint that isn't a shot: disclaimers, mandatory labels, legal claims, "never do
X" statements, brand voice notes. Put each as one string in `rules[]`. `vg board` shows this
list to the human; the agent must obey it while writing every shot. Do not carry a stray
commercial fact (a price, a phone number) into the plan unless a rule specifically requires
displaying it on screen.

## Step 3 — lay out the beats before shots

Do not jump straight to shots. Pick a structure from `references/beat-sheets.md` (hook-problem-
proof-CTA, listicle, guess-reveal, before-after, POV) that matches the brief's content type and
target length, and write the beat table: seconds, function, line, emotion. A beat is a change in
information or emotion; a beat that changes nothing is padding — cut it.

## Step 4 — short-form craft rules

| Rule | Why |
|---|---|
| Hook lands in the first 1–2s; first word before ~0.8s, first text within ~0.5s | most scroll-past decisions happen before 2s |
| One idea per shot; every shot has one job (introduce, show the place, prove, reveal, move the viewer, ask) | two actions in one shot means the model — and the viewer — reads the wrong one |
| **Cuts every 1.5–3s** for b-roll, property and product; longer only while someone speaks on camera | slow cuts were our first test reel's pacing problem; plan 2–3 cuts inside one 6–8s generated clip |
| No three cuts in a row with the same shot size and the same camera move | the most common giveaway of a generated shot list |
| The product holds real screen time (a property tour: the house ≥ 40%) | our first test reel showed the house for 9 of 42 s |
| Every hook's promise is paid off on screen by a named shot | a "let me check it myself" hook must show her checking, at the place |
| Captions-first | most viewers watch muted — `on_screen_text` and `vo` are not optional decoration |
| End on a clear CTA | a beat with a next action, not just a fade-out |

**Duration note:** `time` is the beat's position in the final edit and can be any length. But an
AI-generated shot's `duration` must be one of the video model's allowed values (`"4"`, `"6"`,
`"8"`, `"10"` on Gemini Omni Flash — see `shotlist-schema.md`). A 2–3s hook beat still generates a
full 4s clip, and `vg edit roughcut` does **not** trim it — the AI clip goes into the rough cut at
its full generated length; only `source: real`/`mg` placeholder gaps are sized from `time`.
Trimming an AI clip down to its `time` window, if still wanted, happens later in the edit stage
(`vg-edit`), not automatically. Do not plan an AI beat that needs less than 4s of usable generated
footage.

## Step 5 — one shot per beat, pick the mode

Normally one shot per beat. Give each shot a **`category`, `camera` and `size`** from
`1_Skills/vg-video-prompt/references/shot-categories.md` and `camera-moves.md`; the category decides
model, framing, move, length and sound. Put the hook's promise in `"promise"` and mark the shot that
delivers it with `"pays_off"`. For a product or property, set `format.product_share_min` (e.g. 0.4). For a property, the house is animated from
the client's real photos (`room_reveal`) or shown as a slow move on the photo in the edit
(`photo_move`), never invented — see `references/property-tour.md`. For `ai` shots, pick `mode`:

| Mode | Use for |
|---|---|
| `frames` | b-roll, locations, product, transitions — exact composition matters more than a face |
| `character` | a recurring person speaks or acts on camera — same face and voice every shot |
| `text` | cheap exploration only; no image/character control |

`real` and `mg` shots don't get a `mode`, `duration`, or any AI-only field — just `id`, `time`,
`beat`, `source`, `summary`, and `vo`/`on_screen_text` as needed.

**Speech discipline.** Plan at most one or two short on-camera lines per reel (the hook, the CTA).
Everything else the viewer hears is voice-over over b-roll, and people in b-roll keep their mouths
closed. Lip-sync is the most fragile part of AI video; fewer moving lips means fewer failures.

## Step 6 — write `vo` and `dialogue` correctly

`vo` is the spoken/caption line for the beat, whoever says it — on camera or not — and is what
the edit's subtitles are built from. `dialogue` is the exact line sent to the video model to
lip-sync, normally the same text as `vo`. Fill it on a `character`-mode shot for a consistent,
locked voice — that's the normal case. A `frames`-mode shot can technically carry `dialogue` too,
but the voice is unlocked and `vg validate` warns about it; use `character` mode instead whenever
the voice needs to stay consistent across shots. Never fill `dialogue` on a `real`/`mg` shot —
there is no AI speaker there at all.

`dialogue` must satisfy the fit rule the tool checks at `vg validate`:

```
characters_in_dialogue ≤ (duration_s − 0.7) × 10.5
```

With `"duration": "auto"` the tool picks the shortest allowed duration that fits; a line too long
for 10s must be split across two shots. Write it short and spoken, not written — contractions,
trailing off, one clause at a time.

## Step 7 — plan `assets[]`

For every character, location, and product the shots need, add one entry per sheet with a
placeholder `id` (`Char_<Name>_Portrait`, `Loc_<Place>`, `Prod_<Item>` — see the naming rule in
`shotlist-schema.md`), `kind`, a first-pass `prompt`, and `refs` (usually `[]` at this stage
unless the brief supplies a real photo to build from — a `file:0_Source/...` ref).
`vg-reference-sheets` and `vg-image-prompt` refine these prompts before generating; your job here
is to make sure nothing needed is missing and nothing unneeded is listed — every asset is a
generation cost.

## Step 7b — write the `look` block (the reel's one visual direction)

A reel reads as AI slop when every shot has its own time of day, weather, grade and graphic style.
Decide the look once, here, before any image exists (field rules in `shotlist-schema.md`):

- `world`: one place and one moment, e.g. "Kota Harapan, one sunny weekday afternoon".
- `light`: direction and quality at that moment. `grade`: one colour treatment, and what to avoid
  ("no purple dusk, no night"). `graphics`: one font, one accent colour, where captions sit (never
  over a face), one label style.
- `style_frames`: 1–3 prompts for key images of that look, e.g. the presenter in the world, and the
  world without people. They may ref character sheets. The human approves them before any
  storyboard image is made; after that the tool gives them to every frame as a reference.

Cohesion questions to answer before handing off:

- Is every AI shot in the same world and time of day? If the brief mixes day and dusk (a planned
  infrastructure render, say), say so in the look and keep it to one labelled beat.
- Does the hook's promise get paid off on screen (a "let me check it" hook must show the checking)?
- Does the product or place the video sells get real screen time, not only a closing card?
- Are there beats with nothing to look at (a map card, a text slide) that need a real picture?

## Step 7c — write the style prefix into `style_lock` (from the look)

`style_lock.image` and `style_lock.video` are appended by the tool to every frame and video prompt.
Write them from the `look` block as **rules, one short clause per axis**, not adjectives — the same
words in every prompt are what make separate clips read as one film:

- **Register:** e.g. "real phone video, handheld by a friend" (UGC) or "stabilised gimbal, slow
  moves" (property). A reel can have two registers (presenter handheld, property on gimbal); then
  write both and say which shots use which.
- **Light law:** one source and direction with a colour temperature ("bright mid-afternoon sun from
  camera left, about 5500 K; no second sun").
- **Colour:** dominant / secondary / accent, each tied to a source or surface ("green foliage,
  warm stone paving, orange accent only on graphics").
- **Lens:** "phone main camera, about 26 mm equivalent" or "107° rectilinear for interiors, verticals straight".
- **Skin and physics:** "matte skin with visible pores; weight and contact shadows are real".
- **Audio policy (video only):** "diegetic sound only; no music, no subtitles".

No resolution, aspect or duration numbers in it (those are settings). A shot whose look differs
(an aerial, a concept render) sets `"style_lock": false` and carries its own lines.

## Step 8 — validate and hand off

```bash
vg validate -p P
```

Fix everything it reports that belongs to this skill (see "What vg-scene owns" above), including
the `look` todos. Then hand off to `vg-storyboard` for the look review (style frames), and after the
human approves the look, to `vg-reference-sheets`.

## Common mistakes

| Mistake | Fix |
|---|---|
| Two ideas in one shot's `summary` | split into two shots |
| `dialogue` filled on a `real`/`mg` shot | there is no AI speaker on those shots; drop it |
| AI shot with no `mode` | every `ai` shot needs exactly one mode |
| A `real`/`mg` beat quietly turned `ai` | re-check the brief's source column |
| On-screen text as an afterthought | write it in step 4, not after the shot list is "done" |
| Asset planned but never referenced by any shot | drop it — do not generate sheets nothing uses |
