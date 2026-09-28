# Visual review page — design

2026-09-28 · v1.0 · status: approved by Andre in chat ("combine": keep the Visual Review Gate, add
a clickable page on top). Supersedes `2026-09-28_Image_Review_Gate_Design_v1.0.md`.
Builds on `2026-09-28_Visual_Review_Gate_Design_v1.0.md` (the gate: look approval, then whole-reel
visuals approval with an animatic, enforced in `vg`).

## Why

The Visual Review Gate decides *what* must be approved before video: the look (style frames plus the
look text), then the whole reel as images (every beat plus a silent animatic). Andre asked for the
review itself to be visual instead of chat and command lines: look at the images, switch between
takes, write what to change next to the picture, and approve by clicking.

## What Andre decided

| Question | Decision |
|---|---|
| Gate logic | the Visual Review Gate as built by the other session; this page adds none of its own |
| Interface | a review page in the browser with Approve and Change controls |
| Where it runs | on Andre's machine (`127.0.0.1`), Python standard library only |

## `vg review -p P [--port N] [--no-open]`

- If nothing is generated yet (no style frame, no reference sheet, no beat with an image), prints
  "Nothing to review yet" and exits 0.
- Otherwise starts `http.server.ThreadingHTTPServer` on `127.0.0.1` (port 0 = any free port), prints
  the URL, opens it with `webbrowser` unless `--no-open`, and blocks until Andre clicks
  **Done, back to the agent** (or Ctrl-C, exit 130). The agent runs it in the background.
- The URL carries a random token (`secrets.token_urlsafe(16)`). Every request must present it (the
  `t` query parameter for the page and files, the `X-VG-Token` header for API calls); anything else
  gets 403.
- Files are served only when they are on the page: a recorded version of a `look:`, `asset:`,
  `storyboard:`, `first:` or `last:` target, a beat's image, or the latest animatic, each resolved
  inside the project folder. Anything else gets 404.
- The page never generates, renders or pays for anything.

## The page

Built in the browser from `GET /api/state`, re-fetched after every action and on Refresh. Inline CSS
and JS, no external resources, light and dark.

1. **Header:** project name, both gates from `review.gate_status` (approved, not approved, or changed
   since approval with the labels that changed), and the approval mode.
2. **Look:** world, light, grade and graphics text; one card per style frame with its takes (v1, v2…)
   to switch between, a note box, and **Approve look**.
3. **Reference sheets:** one card per asset with takes and a note box (reference sheets are not a
   separate approval in the gate; notes tell the agent what to redo).
4. **Reel:** every beat in timeline order (the edit plan's segments when `6_Edit/Edit_Spec.json`
   exists, else the shot list), each with the picture the viewer sees, the beat's on-screen text or
   voice-over, the AI frames behind it with their takes, and a note box. Then the latest animatic
   (video player) with a warning when it was rendered from older visuals, and **Approve reel**.
5. **Done, back to the agent.**

**Approve buttons:**
- `VG_APPROVAL_MODE=chat`: calls `review.approve_look` / `review.approve_visuals`. Their refusals (look
  not approved yet, the animatic out of date, a frame missing) are shown on the page word for word.
- `VG_APPROVAL_MODE=terminal`: the page does not call them (a click cannot prove a human); it shows
  the exact command to run in Andre's own terminal, where he types the code, and Refresh then shows
  the gate as approved.
- A successful approval clears the notes it covers (look notes for the look; beat and reference-sheet
  notes for the reel).

**Takes:** switching a take is `vg select`: it changes which version later steps use and, through the
gate's snapshots, makes an approval that included the old take stale.

**Notes:** saved by the tool in `project.json` under `review_notes` (`{"look:Look_A" | "asset:X" |
"beat:S05": {"note", "at"}}`); an empty note removes it.

## API (JSON, token header required)

| Call | Body | Does |
|---|---|---|
| `GET /api/state` | – | everything the page shows |
| `POST /api/note` | `{"item", "note"}` | saves or clears a note (item must be on the page) |
| `POST /api/select` | `{"target", "version"}` | same as `vg select` (look/asset/storyboard/first/last only) |
| `POST /api/approve` | `{"stage": "look" \| "visuals"}` | as above |
| `POST /api/done` | – | ends the session |

Errors come back as `{"ok": false, "error": "<message>"}` with status 400 (403 for a bad token).

## What the agent gets back

When Andre clicks Done, the command prints and exits 0:

```
GATE  look: approved
GATE  visuals: visuals changed since approval: S05 first frame
NOTE  beat:S05  make her mid-step, not posed
NEXT  act on the notes (re-roll or re-prompt), render the animatic again (vg edit animatic), then vg review again
```

`NEXT` is one of: act on the notes; wait for Andre to run the approve command (terminal mode, nothing
left to fix); or both gates are approved, go on to video prompts and the video gate.

## Skills and docs

- `AGENTS.md`: the review page is the human's; never click its buttons or call its API yourself.
- `vg-director`, `vg-storyboard`: the look and sequence reviews run through `vg review`: look at every
  image first, render the animatic before the sequence review, run `vg review` in the background, tell
  Andre the page is open, act on the NOTE lines, repeat.
- `cli.md`: documents `vg review`.

## Testing

New file `2_Tools/vg/tests/test_review_page.py` (standard `unittest`; `test_vg.py` untouched):
page data (look, reference sheets, beats in order, takes, gates); notes (save, clear, unknown item,
non-ASCII); take switching voids an approval; approve in chat mode records and clears notes; approve
in terminal mode refuses with the command and records nothing; a gate refusal is passed through;
the summary's NOTE and NEXT lines; the server's token check, file allow-list and a full round-trip
ending with Done; "Nothing to review yet"; the board still renders after the shared helper move.

## Out of scope

Per-shot approvals (the gate approves the whole reel), a hosted page, rendering the animatic or
re-rolling images from the page, authentication beyond the localhost token.
