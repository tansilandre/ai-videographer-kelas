---
name: vg-reference-sheets
description: Use when building character, location, or product reference sheets — trigger phrases like "build the character sheet", "make the reference sheets", "generate the turnaround", "lock the character", "build the location plate", "make the product sheet", or whenever `assets[]` in Shotlist.json still needs images.
---

# vg-reference-sheets

`vg-scene` planned `assets[]` — which character, location, and product sheets the shots need.
This skill turns that list into generated images and QCs them. The next skill, `vg-storyboard`,
refs these sheets to build the storyboard panel for every AI shot — a weak or drifting sheet here
propagates into every shot downstream, so this is worth doing carefully. Prompts follow
`vg-image-prompt`; the mechanics of running `vg image` safely (dry-run, versions, exit codes) are
in `vg-image`. There is no `vg` on PATH — every command below is shorthand for
`python3 2_Tools/vg/vg.py <command>`.

## Why a sheet, not one image

A single reference image lets the model reinterpret every angle it wasn't shown, and the
reinterpretation is a slightly different subject. A small sheet of views constrains enough angles
that later generations land on the same subject. More views is not better either — every
additional generation is another chance to drift. Build few, build carefully.

## Character sheets

| Sheet | Path | Refs | Aspect | Build when |
|---|---|---|---|---|
| Portrait | t2i (or i2i from a real supplied photo) | `[]` (or `file:...`) | `3:4` | always — this is the identity anchor and the `portrait` file in `characters[]` |
| Turnaround (2x2: front/3-4/profile/back) | i2i | `[Portrait]` | `1:1` | always — covers angles the storyboard will need |
| Expression sheet | i2i | `[Portrait]` | `1:1` | only if the script needs distinct emotions the portrait's neutral expression doesn't cover |
| Hand sheet | i2i | `[Portrait]` | `1:1` | only if a shot has the character's hand holding/lifting/gesturing prominently |
| Body (full-body) | i2i | `[Portrait]` | per shot need | only if a shot needs full-body framing; a character with a body image counts **2** media-quota slots per shot instead of 1 |

Chain every derivative view from the **portrait**, never from another derivative (turnaround →
expression is wrong; portrait → turnaround and portrait → expression are right). Chaining
derivatives compounds drift with every hop.

## Location plates

One plate per distinct camera angle the shots actually use, always **empty** — a person in the
plate competes with the character's identity and makes the plate useless as an anchor. Match the
plate's framing to the shot that will ref it: an overhead desk shot needs an overhead desk plate,
not an eye-level room shot. Refs `[]` for t2i, or `file:0_Source/<photo>` for i2i from a supplied
location photo.

## Product sheets

Product accuracy is binary — a bottle that reshapes between shots makes the video unusable
regardless of the rest. Build front/held/in-use views as needed by the shots; if the brief
supplies a real product photo, always build from it via i2i with a preservation clause (never
redesign the packaging from imagination when a real photo exists). Never ask for a legible brand
wordmark in the image — plan a post-production overlay instead and note it in the shot's `notes`.

## Writing `assets[]` with correct refs chains

```json
{ "id": "Char_Rani_Portrait", "kind": "character", "prompt": "...", "refs": [], "aspect_ratio": "3:4" },
{ "id": "Char_Rani_Turnaround", "kind": "character", "prompt": "...", "refs": ["Char_Rani_Portrait"], "aspect_ratio": "1:1" },
{ "id": "Char_Rani_Hands", "kind": "character", "prompt": "...", "refs": ["Char_Rani_Portrait"], "aspect_ratio": "1:1" },
{ "id": "Loc_Car_Interior", "kind": "location", "prompt": "...", "refs": [] }
```

A ref to an asset that hasn't been generated yet is an ordering error — `vg image --stage refs`
resolves the order for you, but hand-editing `Shotlist.json` still requires the referenced asset
to exist earlier in the conceptual chain.

## Generate

```bash
python3 2_Tools/vg/vg.py image -p P --stage refs
```

This generates every missing asset in `assets[]`, respecting the refs chain (portraits before
turnarounds). Already-succeeded assets with an unchanged prompt/refs are skipped — no spend.

## Look at every image and QC it

Do not move on without opening every generated sheet. Check:

| Check | Fail looks like |
|---|---|
| Identity | face doesn't match the portrait — rounder, different jaw, different eyebrows |
| Hands | fused or extra fingers, unnatural bends |
| Text artifacts | garbled logo/label text that was never supposed to render |
| Logos | a brand wordmark attempted and mangled — should have been left blank for a post overlay |
| Wardrobe | outfit differs from the portrait's base outfit without a reason |
| Realism | smoothed/airbrushed skin — missing the realism constraints |

## Fixing a drifted sheet

1. **Add a second anchor before adding adjectives.** If a derivative view drifted, add the
   portrait plus another already-approved view to `refs` rather than piling on descriptive text.
2. Re-roll with a deliberate new take (bumps the version, does not overwrite the old one):
   ```bash
   vg image -p P --target asset:Char_Rani_Turnaround --new-take
   ```
3. Compare versions and pick the one later stages use:
   ```bash
   vg select -p P --target asset:Char_Rani_Turnaround --version 2
   ```
4. If it's still wrong, edit the asset's `prompt` in `Shotlist.json` (this also forces a new
   version on the next run) and re-run `vg validate` before generating again.

## Common mistakes

| Mistake | Fix |
|---|---|
| Building 6 views "to be safe" | 3–4 is the sweet spot; every extra view is another drift risk |
| A location plate with a person in it | regenerate empty |
| Chaining turnaround → expression | re-anchor both to the portrait |
| Asking for a readable logo | drop the wordmark from the prompt, overlay in post |
| Approving a sheet without opening the image | always look before moving to `vg-storyboard` |
