# What Higgsfield teaches us: learnings for the harness v1.0

Date: 2026-09-28 · Written after the redo of our first test reel, where every shot passed its own check but the
reel looked like stitched AI clips. Research: four parallel readers of ~12 public GitHub repos
(read-only, nothing cloned or run), plus Higgsfield's public docs pages.

## 1. The short version

- **Higgsfield's "agent" is not the magic.** Its public agent API is a thin chat client (send text,
  poll for text). The real advantage is (a) **named preset lists** that turn taste into data
  (camera styles, light schemes, colour grades, genres, marketing modes, hooks, settings), (b)
  **hidden server-side prompt builders** behind those presets, and (c) **workflows** that fix the
  order of work. The presets' names are public; their prompt templates are not.
- **The craft lives in the community skill repos**, above all `OSideMedia/higgsfield-ai-prompt-skill`
  (evidence-labelled, 32 sub-skills, a production brief Higgsfield open-sourced for a 95-minute AI
  feature). Most of its doctrine was measured on Seedance 2.0; transfer to our models is marked below.
- **Ten lessons that would have saved our first test reel:**
  1. One frozen **style prefix** (rules, not adjectives) pasted verbatim into every image and video
     prompt; one grade pass over every clip in the edit.
  2. **Images first, and choose stills by their light.** A bad still cannot be rescued by the video prompt.
  3. **Property shots are animated from the real photo**: the prompt describes only camera and
     light, never the room. The house stays real; only the camera moves.
  4. **One camera move per clip, with speed, easing, an end frame and a hold.** Compound moves jitter.
  5. **Write physics, not adjectives**: measurable words (Kelvin, degrees of view, seconds, metres);
     delete "cinematic, stunning, 8K".
  6. **People need micro-life** (a visible micro-event every 1–2 s) and **eyes with a task**.
  7. **Dialogue is built in a fixed order** (voice → the quoted line → action → reaction), every
     non-speaker gets a mouth state, and lines too short for the clip make the model babble.
  8. **Keep lips out of most shots**: few, short on-camera lines; voice-over over b-roll.
  9. **Cuts every 1.5–3 s** in a reel; plan cuts inside generated clips.
  10. **Expect to choose, not to succeed**: Higgsfield's own feature kept ~1–1.5% of generations.
      Change one thing per retry; after two identical failures, rewrite the prompt.

## 2. Sources and how much to trust them

| Repo | License | What it gave us | Trust |
|---|---|---|---|
| `higgsfield-ai/cli`, `higgsfield-client`, `higgsfield-js`, `skills` (official) | MIT / Apache-2.0 / (JS: no LICENSE file) | Model catalog, preset names, agent API shape, audio-first explainer workflow, routing tables | Facts about Higgsfield's platform; not about kie.ai |
| `OSideMedia/higgsfield-ai-prompt-skill` | see repo | Prompt formula, style prefix, engine rules, failure modes, dialogue timing, acting/FACS, model routing, benchmarks | Best source; every claim labelled OFFICIAL / FIELD / DEMO / EMPIRICAL / MEASURED / HOUSE / OPEN |
| `charlesdove977/re-walkthrough-pro` (+ `UGC-Factory`) | MIT | Real-estate walkthrough from listing photos: room order, room→move map, anti-warp ladder, QC bands | Practical, one author |
| `machina-exm/film-studio-skills` | none (ideas only) | Shot cards, visual bible, asset passport, stress tests | Workflow ideas |
| `cth9191/motion-design` | none | Motion-graphics presets, exact-copy inventory, QC table | Graphics craft |
| `rediumvex/ai-video-generator-claude` | MIT | Numbered camera/light/micro-motion rules | Medium; self-contradicts |
| `beshuaxian/…seedance2…` (= AKCodez copies) | none | Real-estate hook list, camera durations, audio layering | Low; padded LLM text |

We re-express everything in our own words; nothing is copied verbatim.

## 3. How Higgsfield categorizes work (and our equivalent)

| Higgsfield | What it is | Ours |
|---|---|---|
| Marketing Studio modes: `ugc`, `ugc_how_to`, `ugc_unboxing`, `product_showcase`, `product_review`, `tv_spot`, try-on… | A format picks camera register, framing and structure | **Formats** (to add): Property Tour, UGC Review, Before/After… |
| Cinema Studio axes: `camera_style` (classic_static, intimate_observer, documentary_snap, dreamy_flow…), `light_scheme` (soft_cross, contre_jour, window, practicals…), `color_grading` (naturalistic_clean, bleached_warm, teal_orange_epic…), `genre` | Style as fixed, named parameters expanded server-side | Our `look` block (world/light/grade/graphics) — should use a small named vocabulary |
| Camera-control presets (Static, Handheld, Dolly In/Out, Crane Up, Arc, FPV Drone, Aerial Pullback, Through Object, Hyperlapse…) | Named moves with a strength | **Camera library** (`vg-video-prompt/references/camera-moves.md`) |
| Hooks (visual scene templates) + settings (Kitchen, In Car, Street…) | Reusable openers and places | `hook-library.md` (now also visual hooks) |
| Workflows: explainer (audio first), dubbing, voice-change, reframe | Fixed order of work | Our pipeline stages |

**Lesson:** categorization is valuable because it makes choices **checkable and repeatable**, not
because a model understands the labels. We get the same by giving every shot a category and a
named camera move from a fixed list, and by having recipes per category.

## 4. Workflow lessons

- **Assets first, locked and tested.** Characters, locations and props are each a text + image
  pair, stress-tested before any narrative shot. The model has no memory between generations;
  "the pipeline is the memory".
- **A written bible, reused verbatim.** Character descriptor, voice descriptor, location, light
  law, grade, props, negative rules. Never swap a synonym ("warm" → "rich" shifted a voice).
- **Global style prefix** (FIELD, 13 productions): one block of rules pasted at the top of every
  prompt — style register, lighting law, colour ratio (60:30:10, each colour tied to a source),
  camera/lens, skin, acting, physics, continuity, audio policy. Override one line per scene only.
  Format and resolution never go in it.
- **Bake stubborn looks into the stills.** If a property keeps drifting (lens character, colour
  cast), generate it into the start frame and stop fighting it in the video prompt.
- **Choose stills by their light**: bad light in a still is the most common cause of "slop" video.
- **One job per scene** (introduce, show the place, build tension, reveal the product, create
  emotion, deliver action), and six questions per shot: who is in shot, where is the camera, what
  does the subject do, what should the viewer notice first, what must stay visible, what must not happen.
- **Edit as supervision**: assembly → rough cut → generation supervision (the only window for
  regenerating) → fine cut → picture lock. The colourist's first job is making neighbours match.
- **Stop-rule ladder**: 2 re-rolls with the same flaw → rewrite the prompt; change one variable per
  attempt; after 10–15 attempts, simplify the shot (split it, drop an action, change the angle),
  not the wording. Salvage: keep the 1–3 good seconds of a "failed" take.
- **Reality check**: Higgsfield's 90-minute feature kept ~1% of images and ~1.5% of videos
  (FIELD). Budget for choosing among takes; generate long, cut the best seconds.

## 5. Video prompt craft

**Structure.** Short-form: 50–100 words of body, subject and action in the first 20–30 words.
Labelled blocks when a shot needs more (STYLE / SCENE / CAMERA / PERFORMANCE / AUDIO / LOCKS).
Image-to-video: **describe only what moves and the camera, never re-describe the frame** (two
competing inputs cause drift). One action beat per 4–6 s; 1–2 per 8 s.

**Measurable language.** The test: could a camera, light meter or stopwatch measure the word?
Replace "cinematic lighting" with "hard key 45° camera-left, 4000 K", "fast" with a speed or a
duration, "wide" with a field of view in degrees (anchors: 107° ultra-wide ≈ 14 mm, 84°, 63°, 47°,
29°). Delete: cinematic, epic, stunning, breathtaking, masterpiece, 8K, ultra-real, premium.

**Camera.** Name one move, its speed or duration, its easing and its **endpoint** (what the frame
shows when it ends), then a hold of 1.5–2 s (clean cut points). A move with no destination drifts
or reverses. Compound moves only as timed phases (rise 0–3 s, hold, push 4–8 s). Handheld as a
texture ("slight handheld drift, operator half a step behind") on top of one primary move.

**Motion realism.** A visible micro-event every 1–2 s on people (blink every 2–4 s, a breath
before speaking, weight shift before moving, hair and fabric lagging ~0.2 s). Write states, not
processes. Chain actions in one direction so the model does not play the action back in reverse
to fill time; name the completed state before the cut. Walking is the hardest stunt: write it as
physics (heel strike, strict alternation, one foot always down) and repeat the same absolute
speed in every clip of one walk. Hands: waist-up framing, or a hand count and owner.

**Acting.** Behaviour, not labels: "jaw tightens, gaze drops" instead of "looks worried". Give the
presenter a physical task and talk over it; stopping the task is the accent. Eyes need a task
("checks whether the point landed"). Dead eyes are the number-one AI tell.

**Dialogue and lip-sync.**
- Order: voice and delivery → the quoted line → physical action → facial reaction.
- Speech lives in the audio part only; add "only this line, nothing else". Every visible non-speaker
  gets "lips at rest, jaw closed" (not "listens without speaking", which names speaking).
- Line length: a line too short for the clip makes the model invent filler (≤6 words in 4 s babbled
  every time; 8–12 words were clean, Seedance 2.0, English). Our fit rule caps the top; add a floor.
- Name the language and register before the line ("in casual Jakarta Indonesian"); spell numbers and
  rare names the way they are said.
- Lip-sync works best: 3–8 s, medium close-up or tighter, one face, locked or slow dolly-in camera,
  no nodding/head-turn words, speech slightly slower than natural.
- No voice lock on Veo: repeat one voice descriptor verbatim in every clip, and prefer voice-over
  over b-roll for anything longer than a line or two (their explainer workflow never generates
  speech inside b-roll).

**Audio.** Four layers: dialogue, one dominant sound per action (tied to the visible action),
ambience (≤2–3 elements, one sentence reused verbatim across a scene), music (never in the video
model; "No music, no subtitles"). Name the room acoustic.

**Negatives.** No negative list in the prompt body; state positive constraints ("stable face,
rectilinear verticals, consistent light"). Short lock tails are fine. The words you write summon
things — to stop a colour, allocate it to one named source instead of banning it. A ban is right
only when the model's untouched default is the failure (e.g. music, subtitles, slow motion in action).

**Continuity.** Restate positions and eyelines after every cut; the first second of a scene is a
wide; exit = cut; off-screen = nonexistent; avoid reflections; text never in the generation (add
it in the edit). Adjacent clips: end one and start the next on the same gesture, or chain the
last frame into the next first frame.

## 6. Our models

| Model (kie.ai) | What the research says | Status |
|---|---|---|
| **Veo 3.1 Lite** | Start + end frame. Prompt order: subject, action, style, camera, composition, lens/focus, ambience, audio. Dialogue in quotes with a speaker/delivery tag; single speaker most reliable; rated best for English (Indonesian untested). Negatives, if any, as plain nouns. Higgsfield's schema says 8 s when both frames are set; Google's API says reference/last frames force 8 s. | Our S04 worked at 8 s with first+last; 4/6 s with two frames untested |
| **Seedance 1.5 Pro** | Vendor-listed **Indonesian lip-sync**; the repo's pick for talking heads (start image + native audio); state dialogue, SFX, music mood and the language. Audio on by default; 4/8/12 s. | Registered, untested; key allowlist blocked it on 2026-09-24 |
| **Gemini Omni Flash** | No documented prompting dialect anywhere. Motion and style rated 3/5 by the repo. Reference-role doctrine (one role and one exclusion per image) is the closest guide. | Character mode failed 9/9 for us |
| **gpt-image-2** | Strong at layout and text; **weak at photoreal faces (plastic)** — frame realism as film photography, avoid the word "photorealistic" with faces; skews yellow on locations; every edit softens skin (mask edits back onto the original). For 9:16, keep text out of the top and bottom 10%. Edits need a closing "keep everything else exactly the same" clause. | Our image model |

## 7. Real estate playbook

- **Animate the real photo.** First frame = the real listing photo; the prompt names only the camera
  move and the light. Re-describing the room fights the photo and drifts the architecture. Screen
  out photos with watermarks, badges or "for sale" banners. Pick 6–10 hero rooms.
- **Order:** exterior → entry → living → dining → kitchen → bedrooms → bathrooms → outdoor.
- **Room → move:** exterior: slow drone approach or facade glide · entry: doorway threshold reveal
  · living: slow arc or lateral glide · kitchen: glide along the counter · bathroom: threshold then
  short push-in · window/view: slow approach until the view fills the frame · tall ceiling: tilt up
  · garden: rising crane · details: pull back from a close-up with a focus shift.
- **Anti-warp ladder:** one slow move per clip (~5 s) → if furniture melts, shorten the push-in →
  if a doorway bends, switch to a lateral glide → skip the room after one failed retry.
- **Lens and light:** architectural ultra-wide ≈ 107° (14–16 mm), "rectilinear, verticals straight,
  no fisheye"; one light logic (never two suns); reflections, strong sight lines and signage expose drift.
- **Visual hooks:** door opens onto the interior · light floods a dark room · slow approach to a window
  view · close-up material detail pulling back to the room · drone drop to the house.
- **Honesty:** call it a "cinematic walkthrough", never a 3D tour; label any AI illustration.
- For our client rule "houses are real footage only": ask whether **a camera move animated from the
  developer's real photo, with nothing in the picture changed**, counts as real. If not, use a slow
  push on the still in the edit instead of a placeholder.

## 8. UGC playbook

- Register: phone selfie or friend-held phone, eye level, one continuous take per clip, casual.
- Beats: hook (1–3 s, direct to camera, first words before ~0.8 s) → problem/claim → reveal →
  proof → CTA settling to a steady frame. A 15–30 s reel may use hook → reveal → CTA only.
- Consistency: one presenter reference set (front, ¾ left, ¾ right, profile, same wardrobe and
  light) plus one environment plate per space; never re-describe the person per prompt.
- Performance: a physical task while talking; slight off-lens glances; no "endorsement pose".
- B-roll: product/place cutaways under the voice, each with the same references.

## 9. Pacing, graphics and the edit

- **Cuts:** 1.5–3 s for b-roll and product; longer only for a spoken line. Generate 6–8 s and cut
  2–3 times inside one clip. No three consecutive cuts with the same shot size and camera move.
- **Grade:** one grade and grain pass over the whole timeline; match neighbouring shots first.
- **Text:** 2–4 words, bold sans, high contrast; first text within ~0.5 s; keep it inside the
  central area and out of the top/bottom 10% (platform UI); never on faces; each graphic starts on
  the matching spoken word; one element animates at a time; one type family and one accent colour;
  a "Forbidden List" of generic looks.
- **Audio:** one continuous room tone and music bed under the cuts; J/L cuts; foley for the visible
  actions (footsteps on the real floor surface, a door latch).

## 10. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Plastic, airbrushed skin | Image model beautified the face; face passed through a model twice | Film-photography framing, "matte skin, visible pores"; never re-pass the base face; mask edits |
| Clips don't look like one film | Each clip got its own light and grade | Style prefix in every prompt; stills chosen by light; one grade pass in the edit |
| Stiff, floaty motion | Adjectives instead of physics; no micro-life | Physics verbs, micro-event every 1–2 s, degree adverbs, a completed state |
| Action plays forward then backward | Leftover clip time | Chain same-direction actions; name the end state; shorter clip |
| Camera drifts or reverses | Move without an endpoint | Name the end frame, then a hold |
| Jitter / morphing | Two moves or too many beats | One move; 1 beat per 4–6 s |
| Room widens, furniture appears | The model invents environment | Lock the set to the reference; describe only motion; use the real photo |
| Walls or doorways bend | Push-in too long or too fast | Shorter move, lateral glide, slower |
| Mumbled extra words, repeated line | Line too short for the clip | Lengthen the line or shorten the clip; "only this line"; mouth states |
| Lips out of sync | Head motion, wide framing, long line | MCU, locked camera, no head words, 3–8 s line |
| Voice changes between clips | No voice lock | Same voice descriptor verbatim; voice-over for longer speech |
| Garbled text on screen | Text generated in the video | Add text in the edit |
| Same defect twice | Prompt or source problem, not luck | Rewrite the prompt or fix the still |

## 11. What we change in the harness

Applied now (skills):
- `vg-video-prompt`: rewritten for our real models, with the structure, camera, motion, acting,
  dialogue and audio rules above; new references `camera-moves.md`, `shot-categories.md`,
  `troubleshooting.md`; `hook-library.md` gains visual and property hooks.
- `vg-image-prompt`: gpt-image-2 realism and plate rules, 9:16 safe zones, edit-keep clause.
- `vg-scene`: style prefix written from the look; formats and categories; pacing budget; speech
  discipline; real-estate playbook reference `property-tour.md`.
- `vg-storyboard`: choose stills by light; real-photo first frames; bake the look into stills.
- `vg-edit`: pacing, grade, text and audio rules; `vg-video`: QC log and stop-rule ladder.

Proposed next (tool changes, need a decision):
- Shot tags in the shot list (`category`, `camera`, `purpose`, `promise` / `pays_off`) with
  `vg validate` warnings: a hook with no payoff shot, the product's share of screen time, three
  cuts in a row with the same size and move.
- A grade/grain pass in `vg edit final` (one LUT or colour settings for every clip).
- Pilot Seedance 1.5 Pro for Indonesian lip-sync, and Veo 3.1 Lite with first + last frame at 4/6 s.
