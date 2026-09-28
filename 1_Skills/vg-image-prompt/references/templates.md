# Image Prompt Templates

Nine templates, one per image type. Each follows the formula in `SKILL.md`. Replace the
bracketed parts; keep every other line. `<IDENTITY STRING>` means: copy `characters[].description`
from `Shotlist.json` verbatim, byte-identical every time it's used. `<ENVIRONMENT STRING>` /
`<PRODUCT STRING>` mean the same idea for a location or product — there's no dedicated schema
field for those, so treat that asset's own locked `prompt` wording in `assets[]` as the string to
repeat verbatim. See `vg-reference-sheets/SKILL.md`.

## 1. Character portrait (t2i — the identity origin)

The one image the character lock is built from. Generate as **text-to-image**: this is the
origin, not a derivative, so there is nothing to run image-to-image against yet.

Aspect: `3:4`. Refs: `[]`.

```
Use: character reference portrait, the identity anchor for every later shot of this person.
Scene: plain flat light-grey seamless background, no props.
Subject: <IDENTITY STRING>, neutral relaxed expression, facing camera, standing.
Details: wearing <base outfit>.
Composition: waist-up portrait, centered, eye level, chest-height camera.
Style: phone photo, candid, unposed, looks like a real phone photo.
Lighting: soft natural daylight from the left.
Constraints: natural skin texture, visible pores, no beauty filter, no smoothing.
Avoid: studio-perfect symmetry, airbrushed skin, jewelry or wardrobe not listed above, text, logos.
```

## 2. 2x2 turnaround (i2i from the portrait)

One image, four panels, generated together so the face and wardrobe stay consistent between
angles — far more reliable than four separate generations. Refs: `[Char_<Name>_Portrait]`.
Aspect: `1:1`.

```
Use: character turnaround sheet, four consistent angles of the same person.
Scene: same plain flat light-grey seamless background as the reference, repeated in all 4 panels.
Subject: <IDENTITY STRING>, same as the reference image exactly.
Details: laid out as a clean 2x2 grid of four panels: top-left front view, top-right
three-quarter view (head turned 45 degrees to her left), bottom-left full profile facing left,
bottom-right back view. Equal size panels, separated by thin crisp white gaps, no captions, no
labels, no text anywhere.
Composition: same scale and eye-line across all four panels.
Style: phone photo, candid, looks like a real phone photo.
Lighting: soft natural daylight from the left, identical across all 4 panels.
Constraints: keep the same face, same facial bone structure, same skin tone and texture, same
hair, same age in all 4 panels. Do not retouch, smooth, or beautify the face.
Avoid: a different outfit or hairstyle in any panel, panel borders/frames/numbers, mismatched lighting between panels.
```

## 3. Expression sheet (i2i from the portrait)

Only build this if the storyboard actually needs distinct emotions. Same grid trick, fewer panels
if only 2–3 expressions are needed. Refs: `[Char_<Name>_Portrait]`. Aspect: `1:1`.

```
Use: character expression sheet for storyboard reference.
Scene: same plain background as the reference.
Subject: <IDENTITY STRING>, same as the reference image exactly, front-facing in every panel.
Details: laid out as a clean 2x2 grid: [surprised, eyebrows raised] / [amused, slight smile] /
[concerned, brow slightly furrowed] / [neutral, relaxed] — replace with the expressions this
script actually needs. Equal size panels, thin white gaps, no labels.
Composition: same framing and scale as the reference in every panel.
Style: phone photo, candid.
Lighting: identical to the reference, soft natural daylight from the left.
Constraints: keep the same face, hair, and wardrobe as the reference in all 4 panels.
Avoid: exaggerated cartoon expressions, a different person emerging in any panel.
```

## 4. Hand sheet (i2i from the portrait)

Fused fingers and extra digits are the single most common failure this pipeline hits, and a bad
hand in a still only gets worse once it's animated. Build this whenever a shot needs a hand
holding, lifting, or gesturing. Refs: `[Char_<Name>_Portrait]`. Aspect: `1:1`.

```
Use: hand reference sheet — check every hand-bearing frame against this before approving it.
Scene: same plain background as the reference.
Subject: <IDENTITY STRING>'s hand and forearm only, same skin tone and any visible
accessories (rings, bracelets) as the reference.
Details: laid out as a clean 2x2 grid: open palm facing camera / holding a phone naturally /
relaxed at the side / both hands loosely clasped. Equal size panels, thin white gaps, no labels.
Composition: hand fills most of each panel.
Style: phone photo, candid, close-up.
Lighting: identical to the reference, soft natural daylight.
Constraints: exactly five fingers per hand, natural proportions, natural skin texture.
Avoid: extra or fused fingers, unnatural bends, objects merging into the hand.
```

## 5. Location plate (t2i, or i2i from a real photo)

The environment anchor. Generate it **empty** — a person in the plate makes it useless as an
anchor and becomes a second, competing identity. Match the camera angle the shots will actually
use. Aspect: `9:16`. Refs: `[]` for t2i, or `[file:0_Source/<photo>]` for i2i from a supplied
photo.

```
Use: empty location plate, the environment anchor for every shot in this scene.
Scene: <ENVIRONMENT STRING>.
Subject: the space itself — empty, no people.
Details: <2-4 specific objects that give the place a lived-in feel>.
Composition: <camera height and angle matching the storyboard's framing for this scene>, vertical.
Style: phone photo, candid, looks like a real phone photo.
Lighting: <direction, time of day> matching the ENVIRONMENT STRING.
Constraints: no people, no legible text, no signage.
Avoid: clutter, brand logos, screens showing content, a person entering frame.
```

If building from a real photo: replace `Subject`/`Details` with a preservation clause ("keep the
exact same room, same furniture layout, same wall colour — change only \<what's changing\>") per
the identity-lock phrasing above.

## 6. Product sheet (t2i, or i2i from a real product photo)

Packaging accuracy is binary — a bottle that reshapes itself between shots makes the video
unusable regardless of everything else. Aspect: `1:1`.

```
Use: product reference sheet — packaging accuracy anchor.
Scene: plain light wood surface or plain background, no props competing for attention.
Subject: <PRODUCT STRING>.
Details: <front flat on surface | held in a hand | in use — pick one view per generation>.
Composition: chest-height looking down, product fills most of the frame.
Style: phone photo, candid, looks like a real phone photo.
Lighting: soft natural daylight from the left.
Constraints: exact packaging shape and label layout as described, no visible brand wordmark
(the real logo is overlaid in post-production).
Avoid: invented brand text, a different bottle/box shape than described, a second product.
```

If a real product photo exists, use image-to-image with a preservation clause: "keep the exact
same [shape/material/label layout]. Do not change the packaging. Change only the background and
lighting."

## 7. Storyboard panel (i2i from the relevant sheets)

Refs: whichever character/location/product asset ids this shot actually needs — see
`vg-storyboard/SKILL.md` for how to pick them. Aspect: `9:16`.

```
Use: storyboard panel — the video model's starting frame for this shot.
Scene: <ENVIRONMENT STRING>.
Subject: <IDENTITY STRING>, if a character is in this shot.
Details: <this shot's ONE action, framed at its START, not its climax — e.g. "hand entering
frame toward the product, product still on the desk">.
Composition: <shot size and camera position from the shot list — selfie / chest-height / eye
level / desk-level>, vertical, leave headroom for any movement the shot will make.
Style: phone photo, candid, looks like a real phone video still.
Lighting: <direction, matching the ENVIRONMENT STRING and any earlier shots in the same scene>.
Constraints: natural skin texture, visible pores, no beauty filter, keep wardrobe/props matching the sheets.
Avoid: the action already completed, a second person, legible text, mirror reflections.
```

## 8. First frame

Two paths:

- **`{"from": "storyboard"}`** — reuse the storyboard panel as-is. Free (no extra generation).
  Default choice whenever the panel's framing is already exactly the video's starting point.
- **A separate `{prompt, refs}`** — only when the first frame needs different framing or extra
  precision the panel didn't nail (e.g. the panel proved the composition but drifted on a hand or
  a product angle). Write it the same way as a storyboard panel, refs = the storyboard panel plus
  whatever sheet needs correcting, and describe only what changes: "same as the reference, but
  fix the right hand to match the hand sheet."

## 9. Last frame (i2i from the first frame)

Only for shots where the end state differs meaningfully from the start — a camera move, a
reveal, a transition. Skip it for a static talking-head/character-mode shot; there is nothing for
a last frame to add. Refs: `[first:<ShotId>]`. Describe **only the change**, not the whole scene
again:

```
Use: last frame — the end state of this shot's motion, for a smoother generated transition.
Scene: same as the reference image, unchanged.
Subject: same as the reference image, unchanged.
Details: <only what has moved/changed by the end — e.g. "she has turned fully to face the
camera" or "the bottle is now upright and open">.
Composition: same framing as the reference unless the shot is a push-in/pull-out — then state
the new framing.
Style: same as the reference.
Lighting: same as the reference.
Constraints: keep everything else — face, wardrobe, background, lighting — identical to the reference.
Avoid: introducing new objects or people, changing anything not named in Details.
```

For continuity across a cut, the next shot's first frame often refs this shot's last frame
(`refs: ["last:S01"]`) so the cut reads as continuous — see `vg-storyboard/SKILL.md`.
