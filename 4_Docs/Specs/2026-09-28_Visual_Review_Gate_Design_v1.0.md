# Visual review gate: design v1.0

Date: 2026-09-28 · Status: approved by Andre in chat (flow, scope, feedback channel, tool enforcement)

## Why

Our first test reel (2026-09-28) was generated and checked one shot at a time. Every frame passed
its own check, but the reel had no shared look (six different times of day and grades), the story
broke its hook, and the graphics fought each other. Andre found this only after 175 credits of video.
His rule: **image input decides the video, so the human approves the visuals as images first.**

## What Andre decided

| Question | Answer |
|---|---|
| What is approved before video | The whole reel as images: first the look (style frames), then every beat in timeline order plus a slideshow preview |
| How feedback is given | Board + chat. Andre replies in chat; the agent fixes and shows again; on his "approved" the agent runs the approve command |
| How strongly it is enforced | In the `vg` tool (approach A), like the credit gate, not only in skill text |

## Flow

| # | Stage | Change |
|---|---|---|
| 1 | Project + scene | `Shotlist.json` gets a `look` block (world, light, grade, graphics, style frames) |
| 2 | **Look** (new) | `vg image --stage look` → Andre reviews → `vg approve look` |
| 3 | Reference sheets | Location/product/other assets get the approved style frames as extra refs; character sheets do not (identity anchors stay neutral) |
| 4 | Storyboard + frames | Refused until the look is approved; every storyboard/first/last image gets the style frames as extra refs (`"look_refs": false` on a shot opts out). `6_Edit/Edit_Spec.json` (text, map, photos, captions) is written at this stage |
| 5 | **Sequence review** (new) | `vg board` filmstrip + `vg edit animatic` → Andre reviews → `vg approve visuals` |
| 6 | Video prompts | Written against approved images |
| 7 | Video gate | Refuses unless look and visuals approvals exist and still match |
| 8 | Video → edit | Unchanged |

## Shotlist `look` block

```json
"look": {
  "world": "Kota Harapan, one sunny weekday afternoon",
  "light": "warm late-afternoon sun from camera left, soft shadows",
  "grade": "natural warm, medium contrast, no teal-orange, no purple dusk",
  "graphics": "one font, one accent #FF5A1F, captions in the lower third off the face",
  "style_frames": [
    {"id": "Look_A", "prompt": "…", "refs": ["Char_Rani_Portrait"]}
  ]
}
```

- Targets are `look:<id>`; files `2_References/<id>_vN.png`. One to three style frames.
- `vg validate`: a missing `look` block or empty world/light/grade is a todo; a style frame without
  `id` or `prompt`, a duplicate id, or more than three frames is an error.

## Ledger (`project.json`, tool-written only)

- `approvals.look = {snapshot, items, project_path, at}`. `items` maps a label to a SHA-256: the look
  text (world, light, grade, graphics) and each style frame's selected file.
- `approvals.visuals = {snapshot, items, animatic, project_path, at}`. `items`, in timeline order:
  the look snapshot; each AI shot's storyboard, first and last frame file; the edit plan
  (`Edit_Spec.json` without `output`, `voice`, `music` and each segment's `audio`/`clip_volume`);
  every image the edit plan references (`file:` photos, `storyboard:`/`asset:` targets).
- `animatics[] = {path, snapshot, at}`: the visuals snapshot each animatic was rendered from.

A snapshot is `sha256_json(items)`. Any new selected version, changed photo or edited text changes
it. Stale approvals are reported with the labels that differ, e.g. `S05 first frame, edit plan`.

## Commands

| Command | Refuses (`REFUSED:`, exit 2) or errors when |
|---|---|
| `vg image --stage look` | – (images are free to iterate) |
| `vg approve look` | no `look` block, or a style frame not generated yet |
| `vg edit animatic` | no `Edit_Spec.json`, or an image it needs is missing. Output `6_Edit/Animatic_<Project>_vN.mp4`: every beat as a still at edit timing, captions and graphics, no audio; clips are never used |
| `vg approve visuals` | look not approved or stale; an AI shot lacks a frame its mode needs; no `Edit_Spec.json`; the latest animatic was rendered from a different snapshot than the current one (Andre must approve what he saw) |
| `vg approve video`, `vg video` | look or visuals approval missing or stale (checked again inside the submit transaction) |
| `vg image` storyboard/first/last | look not approved or stale |

Approvals follow `VG_APPROVAL_MODE`: `chat` = the agent runs the command after an explicit
"approved" in chat; `terminal` = the human types the random code, as for video. `vg estimate` and
`vg board` never refuse; they report the gate state.

No grandfathering: projects made before this change need both approvals before more video.

## Board

`Board_<Project>.html` gets, above the shot cards:
1. **Look**: the style frames and the look text, with gate state (approved / changed / not approved).
2. **Filmstrip**: every beat in timeline order as a thumbnail (AI frame, edit-plan photo, or a
   labelled card for a beat with no image), the latest animatic path, and the visuals gate state.

## Skills and docs

- `vg-director`: pipeline table gains Look and Sequence review; rule "no storyboard before the look
  is approved, no video before the visuals are approved"; review is done on the whole reel, not
  shot by shot.
- `vg-scene`: writes the `look` block. `vg-storyboard`: style frames, look refs, sequence review
  loop. `vg-edit`: Edit_Spec is written at the storyboard stage; `vg edit animatic`.
  `vg-video`: gate preconditions. `cli.md`, `shotlist-schema.md`, `AGENTS.md` updated.

## Tests

Unit tests with the existing fake provider: look targets and validation; storyboard refused before
the look approval; look refs appended after it (not for character assets, not with `look_refs:
false`); `approve look` refusals; `approve visuals` refused without animatic / with a stale animatic;
video and approve-video refused without or with stale approvals, naming what changed; a new take of
an approved frame makes the approval stale.

## Hardening after the adversarial review (2026-09-28)

An Opus reviewer broke the first version in 11 ways (tests in `2_Tools/vg/tests/test_visual_gate_attacks.py`).
The rules that closed them:

- **One source for video inputs.** `review.shot_inputs()` lists exactly the images a video request
  sends (frames: first + last; character: the anchor = planned first frame, else the panel, plus
  `video_refs`; text: `video_refs`). `build_video_job` takes its images from it, and the visuals
  snapshot hashes the same list, so an image nobody reviewed cannot reach the video model.
- The visuals snapshot also covers: the shot list (ids, sources, modes; a shot added later closes
  the gate), each AI shot's picture as the animatic shows it (`review.still_target()`), its words
  (`dialogue`, `vo`, `on_screen_text`), and the portrait/body sheets of characters in character shots.
- `approve visuals` needs every AI shot as a clip segment in the edit plan, and the latest animatic
  file on disk. `vg edit animatic` re-checks the snapshot after rendering and records nothing if the
  images changed during the render.
- Sheets a style frame is built from never get the look refs (that loop re-rolled the approved look
  on every `--stage all`).
- Ids of assets, shots and style frames may use only letters, digits, `_` and `-` (they become file
  names); a `first_frame` with both a prompt and `"from": "storyboard"` is an error; the edit plan's
  shapes are checked (a clear error, never a traceback); `vg status` and `vg board` report a broken
  edit plan instead of failing.

## Decided while building (assumptions, open to change)

- The animatic is silent. Captions carry the words; the macOS temporary voice was judged more
  distracting than useful for a visual review.
- Character sheets do not get look refs, so identity anchors stay on a neutral background.
