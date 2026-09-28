---
name: vg-image-prompt
description: Use when writing or fixing a gpt-image-2 prompt — trigger phrases like "write the image prompt", "character portrait prompt", "2x2 turnaround", "expression sheet", "hand sheet", "location plate", "product sheet", "storyboard panel prompt", "first frame prompt", "last frame prompt", or when a generated image looks wrong and the prompt needs a diagnosis.
---

# vg-image-prompt

`vg-image-prompt` is not its own pipeline stage — it is the prompt-writing reference that
`vg-reference-sheets` and `vg-storyboard` both call into whenever they write a gpt-image-2 prompt
for an asset, a storyboard panel, or a first/last frame. `vg-image` is what actually runs the
finished prompt through `vg image` (shorthand here for `python3 2_Tools/vg/vg.py image` — there is
no `vg` on PATH) and handles the result. Read `vg-image` for the mechanics of running generation;
read this skill for what to put in the prompt.

## The formula

Every gpt-image-2 prompt — text-to-image or image-to-image — follows this order. Fill only the
lines that matter; drop the rest. Order matters: gpt-image-2 weights earlier information more
heavily, and a long run-on sentence works worse than short labelled clauses.

```
Use: <what this image is for — character reference, location plate, storyboard panel, first frame...>
Scene: <setting / background / environment — copy the environment string verbatim if one exists>
Subject: <the main thing — copy the identity string verbatim if a locked character is in frame>
Details: <secondary elements, props, wardrobe, what someone is doing — one action only>
Composition: <framing (close-up/waist-up/wide), camera height, aspect in words>
Style: <phone photo / candid / documentary — never "cinematic" or "render">
Lighting: <direction, quality, time of day>
Text: "<exact text>" — only if this image is allowed to contain text (rare; see below)
Constraints: <what must stay unchanged, realism requirements>
Avoid: <what must NOT appear — gpt-image-2 has no negative-prompt field, so this is the only place to say it>
```

`Avoid:` does the job a negative-prompt field would do elsewhere. Always include it: name the
specific failure modes for this shot (extra fingers, text artifacts, a second person, a different
outfit), not generic junk like "bad quality."

## Identity-lock phrasing (image-to-image)

Any image-to-image call that must preserve a face, a product, or a place needs an explicit
preservation clause — without one, gpt-image-2 will "improve" the subject into someone or
something else:

```
Keep the same face, the same facial bone structure, the same eye shape, the same nose, the same
lips, the same skin tone and texture, the same hair, and the same age. The face must match the
reference images exactly — same jawline, same eyebrow thickness, same eye size and shape. It
must read as the identical person, not a similar-looking model. Do not retouch, smooth, or
beautify the face.
```

**Two anchors beat one.** A single reference image drifts (rounder face, thicker eyebrows,
different jaw) noticeably more often than two. `input_urls` accepts up to 16 with no cost
penalty — pass at least two views of the same subject whenever one is available, and prefer
adding a second anchor over adding more descriptive adjectives when a result drifts. End the
prompt with the subject's verbatim identity/environment/product string — for a character this is
`characters[].description` in `Shotlist.json`, copied byte-identical; for a location or product
there is no dedicated field, so treat that asset's own `prompt` in `assets[]` as the locked string
and repeat its wording (see `vg-reference-sheets`).

## Text-in-image rules

Avoid asking gpt-image-2 to render legible text — logos, prices, addresses, signage. Text
rendering is undocumented and unreliable; it comes out as garbled glyphs more often than not.
Plan for on-screen text (`on_screen_text` in the shot list) to be added in the edit instead.
Exception: a short constraint like "no text, no signage" is a fine thing to *ask for* — the rule
is against asking the model to *produce* readable words in the frame.

## Realism / anti-AI-look vocabulary

| Want | Say |
|---|---|
| Real skin | natural skin texture, visible pores, no beauty filter, no smoothing |
| Real camera | phone photo, shot on iPhone, candid, unposed, slight handheld feel |
| Real light | soft natural daylight from \<direction\>, name the time of day |
| Avoid the "AI look" | Avoid: airbrushed skin, perfect symmetry, studio-perfect lighting, plastic texture, oversaturated colour |
| Avoid slop words | delete "stunning, 8K, masterpiece, hyperrealistic, perfect, flawless, cinematic"; name the light, lens and material instead |
| Avoid a generic model face | keep the small imperfections from the identity string — a scar, freckles, an asymmetry — do not let the model average them away |

## gpt-image-2: what it is bad at, and the fixes

Research notes: `4_Docs/Research/2026-09-28_Higgsfield_Learnings_v1.0.md` §6.

- **Faces come out plastic when you ask for realism.** Frame realism as film photography instead:
  "35 mm film photo", "candid phone photo", "editorial portrait, natural light". **Do not write
  "photorealistic"** when a face is in frame. Add "matte skin, visible pores, no retouching".
- **Every edit softens skin.** Never pass a face through the model twice; regenerate from the
  original portrait refs instead of editing an edit.
- **It skews warm/yellow on locations.** Name the white balance ("neutral daylight, about 5500 K")
  and check stills side by side before approval.
- **Choose stills by their light.** A still with bad light makes a bad video; no video prompt fixes
  it. Keep one light logic per location (one sun direction, never two).
- **Edits need a keep clause.** When changing part of a still, list the change, then end with
  "keep everything else exactly the same: lighting, angle, walls, floor, every other object".
  Without it the whole image re-renders and drifts.

## Frames that become video

- **A real place starts from a real photo.** For a property, use the client's photo as the first
  frame (i2i with `file:0_Source/...`, or directly), and never invent the building.
- **Location plates:** shoot them at a ¾ angle, not straight-on (a frontal plate becomes flat
  wallpaper and the model invents the rest). Leave one distinctive anchor object in view. No people
  unless the shot needs them. Reflections, signage and strong symmetric lines expose drift.
- **Reference sheets:** plain grey background, flat even light, no baked-in shadows or bokeh (baked
  light is inherited and amplified later). Only one readable face per sheet. A sheet is a menu:
  whatever is on it will be used, so leave off anything that should not appear.
- **Bake the look into the stills.** A look that keeps drifting in video (grade, lens character)
  belongs in the start frame, where it holds, not in the video prompt.
- **9:16 frames:** keep faces and key subjects out of the top and bottom 10% (platform buttons and
  captions cover them) and leave room in the lower third for captions.
- **No text in images meant for video.** Add words in the edit.

## Field names — do not invent these

gpt-image-2 has exactly two models and a small field set. Getting a field name wrong is the most
common cause of a rejected task. See `vg-image/SKILL.md` for the full verified list; the traps
that matter while writing a prompt:

- The image-input field for i2i is **`input_urls`** (an array), not `image_urls` or `input_image`.
- There is **no** `seed`, `output_format`, `quality`, `size`, or `background` field usable above 1K.
- There is **no** negative-prompt field — that is what `Avoid:` in the formula is for.

## Templates

`references/templates.md` has a filled example for each image type: character portrait, 2x2
turnaround, expression sheet, hand sheet, location plate, product sheet, storyboard panel, first
frame, last frame. Start from the matching template and edit the bracketed parts — do not write a
prompt from a blank page.
