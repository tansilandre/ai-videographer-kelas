# Image review gate — design

2026-09-28 · v1.0 · status: **superseded** by `2026-09-28_Visual_Review_Page_Design_v1.0.md`. Andre
chose to keep the other session's Visual Review Gate and build only the clickable review page on top.

## Why

Image inputs decide the video. A bad reference sheet spreads into every frame built from it, and a
bad frame can only give a bad clip, which costs video credits. Andre wants to review and approve
the visuals first and move to video only once he is satisfied. Today the harness makes images freely
and shows them for the first time at the video gate, where approving the video implies the frames are
fine. The ViMax test on 2026-09-28 (`~/Documents/VIMAX_KIE_TEST/99_Output/`) showed the cost of
skipping this: a portrait's pose leaked into a walking shot, and a last frame broke the geography of a
fly-over, and both were only visible once the clips had been paid for.

## Decisions (Andre, 2026-09-28)

| Question | Decision |
|---|---|
| Which pipeline | the harness (`vg`), not the ViMax test runner |
| How approval is given | by the human; the agent never approves on its own |
| Checkpoints | two: reference sheets before storyboards and frames; shot frames before video |
| Enforcement | in the `vg` tool, not only in skill text (approach A) |
| Interface | visual: a review page in the browser, not typed commands |
| Where the page runs | on the human's machine (`127.0.0.1`), Python standard library only |

Unchanged: images still need no approval to generate or re-roll (6–16 credits), and the video gate
(cost shown, a yes in chat, a code typed on a real terminal) stays exactly as it is.

## The flow

1. **Reference sheets.** The agent generates `assets[]`, looks at every image, rebuilds the board,
   then runs `vg review`. Andre opens the page, approves each sheet or clicks Change and writes a note,
   and clicks "Done, back to the agent". The agent re-rolls what he flagged and opens the page again.
   This repeats until every sheet the storyboards and frames use is approved.
2. **Storyboard panels and frames.** Generation is refused for any `storyboard:`, `first:` or `last:`
   target whose refs include a reference sheet that is not approved, or has changed since it was
   approved.
3. **Frame review.** After frames, the same page loop, per shot. A shot is approved as a unit: the
   exact set of images the video model will receive.
4. **Video gate.** `vg approve video` and `vg video` refuse any shot whose frames are not approved or
   have changed since approval. Everything after that is today's gate.

An approval is tied to the image file's content (sha256). Re-rolling, selecting another take, or
changing which images a shot sends makes it stale; stale shows as "changed since approval" and counts
as not approved.

## What gets approved

**Reference sheets** are the entries of `assets[]` (characters, locations, products, other). Each is
approved on its own, for its selected version.

- Gated: a `storyboard:`, `first:` or `last:` target that refs an `asset:` target.
- Not gated: an asset made from another asset (a turnaround from a portrait) and `file:` refs (client
  photos in `0_Source/`). If a parent sheet is re-rolled after its child was approved, the child's
  approval stands, because the child's own file did not change.

**Shot inputs** are exactly the images the video request would send, taken from one helper,
`shot_input_images(project, sl, shot, state)`, which `build_video_job` also uses, so the two can
never disagree:

| Mode | Images |
|---|---|
| `frames` | the first frame (`first:SID`, or `storyboard:SID` when `first_frame` is `{"from": "storyboard"}`), plus `last:SID` when `last_frame` is set |
| `character` | the first frame or storyboard panel used as the soft reference, plus `video_refs` |
| `text` | `video_refs` only |

A shot with no input images (a `text` shot without `video_refs`) needs no frame approval; the page and
the board say "no input images".

A storyboard panel that is not reused as the first frame is a sketch and is not gated.

## Ledger

The tool writes approvals and change notes to `project.json` (never edited by hand), in a new
`approvals.images` map next to `approvals.video`:

```json
"approvals": {
  "video": {},
  "images": {
    "asset:Char_Rani_Portrait": {"status": "approved", "version": 2, "sha256": "…",
                                  "at": "2026-09-28T15:02:11", "via": "review page"},
    "shot:S05": {"status": "changes", "note": "make her mid-step, not posed",
                 "images": {"storyboard:S05": "…sha256…"}, "at": "…", "via": "review page"},
    "shot:S01": {"status": "approved", "images": {"storyboard:S01": "…", "last:S01": "…"},
                 "at": "…", "via": "cli", "human_said": "S01 OK"}
  }
}
```

`read_state` adds an empty `images` map to older ledgers. An entry is **approved** only when
`status` is `approved` and every current input image's sha256 matches (for a shot, the set of
targets must match too). A `changes` entry keeps its note until the item is approved.

## `vg review`

```
vg review -p P [--port N] [--no-open]
```

- If the project has no generated reference sheet and no shot with input images yet, it prints
  "Nothing to review yet" and exits 0 without starting a server.
- Starts `http.server.ThreadingHTTPServer` on `127.0.0.1` (port 0 = any free port), prints the URL and
  opens it with `webbrowser` unless `--no-open`.
- The URL carries a random token (`secrets.token_urlsafe(16)`). Every request must present it (query
  parameter for pages and images, `X-VG-Token` header for API calls); anything else gets 403. This
  stops other local web pages from submitting clicks.
- Serves only images that are recorded versions of this project's targets, resolved inside the
  project folder; any other path gets 404.
- **The page** (built on every load from `Shotlist.json` and `project.json`, inline CSS and JS, no
  external resources, light and dark):
  - a header naming the project and the current checkpoint (references, frames, or video unlocked),
    with a progress count;
  - a References section, one card per asset: the image large, its takes (v1, v2…) to switch between,
    a status badge (needs your review, approved vN, changes requested, changed since approval),
    Approve and Change buttons, a note box after Change;
  - a Shots section, one card per AI shot: its input images side by side (first and last frame),
    takes per image, the same status, buttons and note; plus the shot's summary and dialogue so the
    frame can be judged against the beat;
  - a "Done, back to the agent" button.
- **API** (JSON, POST, token required), each validated and written through `project.transaction()`:
  - `/api/approve` `{"item": "asset:X" | "shot:S01"}`: records the current selected images
  - `/api/change` `{"item": …, "note": "…"}`: note must not be empty
  - `/api/select` `{"target": "storyboard:S05", "version": 2}`: same as `vg select`; any approval that
    included that target becomes stale
  - `/api/done`: ends the session
- The page never generates or pays for anything. Re-rolls stay with the agent.
- **When Andre clicks Done**, the server stops and the command prints a summary for the agent, then
  exits 0:

  ```
  APPROVED asset:Char_Rani_Portrait v2
  CHANGES  shot:S05  "make her mid-step, not posed"
  PENDING  shot:S08
  NEXT     re-roll shot:S05 as noted, then run vg review again
  ```

  Ctrl-C ends it the same way with exit 130. The agent runs `vg review` in the background (it blocks
  until Done) and reads the summary.

## Where the tool refuses

All refusals use the existing `Refused` error (exit 2, output starting `REFUSED:`), name the items,
and say what to do: "show the human the review page (`vg review -p P`)".

| Command | Refuses when |
|---|---|
| `vg image --stage storyboard / frames / all` | a target refs an unapproved or stale reference sheet (`--dry-run` lists it as blocked instead) |
| `vg approve video` | a selected shot's frames are not approved or are stale |
| `vg video` | same check, again, before any spend |

`vg estimate --stage video` and `vg status` show each shot's review status; the static board
(`vg board`) shows the same badges on every asset and shot.

## Command-line fallback

For setups with no browser (a remote agent, WorkBuddy without a local desktop):

```
vg approve refs   -p P (--assets A,B | --all) --human-said "<the human's words>"
vg approve frames -p P (--shots S01,S02 | --all) --human-said "<the human's words>"
vg approve refs|frames ... --revoke
```

`--human-said` must not be empty; it is stored in the ledger as the record of who approved. These
write the same entries as the page, with `"via": "cli"`.

## Skills and docs

| File | Change |
|---|---|
| `AGENTS.md` | new rule: images are approved only by the human (review page, or `--human-said` quoting their words); never on the agent's own initiative |
| `1_Skills/vg-director/SKILL.md` | pipeline gets stage "Reference review" after reference sheets and "Frame review" after frames; the video gate says frames must be approved first |
| `1_Skills/vg-reference-sheets/SKILL.md` | ends with the reference review loop |
| `1_Skills/vg-storyboard/SKILL.md` | ends with the frame review loop; how to act on change notes |
| `1_Skills/vg-video/SKILL.md` | the gate checks frame approval; what the refusal means |
| `1_Skills/vg-director/references/cli.md` | documents `vg review` and `vg approve refs / frames` |

The review loop the skills describe: look at every image yourself first; rebuild the board; run
`vg review` in the background and tell the human the page is open; wait for the summary; re-roll or
re-prompt what they flagged (a change note is an instruction for the prompt, not a suggestion);
repeat until nothing is pending.

## Existing projects

Finished clips are untouched. Any new video take needs its frames approved, so a project already in
progress (our first test reel) needs one visit to the review page before its next take. No migration script:
`read_state` adds the empty map.

## Testing

A new file, `2_Tools/vg/tests/test_image_gate.py` (standard `unittest`, like `test_vg.py`, which it
does not touch):

- a storyboard or frame that refs an unapproved sheet is refused; approving it lets generation run
- re-rolling a sheet, or selecting another take, makes its approval stale and generation is refused
- `shot_input_images` returns the right images per mode (frames with and without a last frame, frames
  from the storyboard, character, text with and without `video_refs`)
- `vg approve video` and `vg video` refuse unapproved and stale shots and accept approved ones
- a shot with no input images passes
- API handlers: approve, change (empty note rejected), select (voids the approval), done
- token check (missing or wrong token gets 403) and path check (a path outside the project gets 404)
- one real round-trip: start the server on port 0 in a thread, fetch the page and an image, post an
  approval, post done, and read the summary
- the CLI fallback refuses an empty `--human-said`
- `python3 -m unittest discover -s 2_Tools/vg/tests` passes in full before the merge

## Out of scope

- A hosted page or client-facing approvals (Andre chose local)
- Generating or re-rolling images from the page
- Approving storyboard panels that are not used as first frames
- Authentication beyond the localhost token

## Build notes

Another session has uncommitted changes to `2_Tools/vg/vglib/finish.py` and
`2_Tools/vg/tests/test_vg.py` on `main`. This work is built on its own branch in a separate git
worktree, touches neither file, and is merged after that session commits.
