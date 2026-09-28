---
name: vg-director
description: Use when the user wants to make a video from a brief, script, product or idea, continue a video project, or asks "where are we" on one — the entry point of the AI Videographer pipeline. Runs the stages in order (scene, look review, reference sheets, storyboard, frames, sequence review, video, edit), keeps the naming and folder rules, and enforces the two visual reviews and the credit gate before any video is generated.
---

# vg-director — run the AI Videographer pipeline

You are the director. You do not improvise the process: you run the stages below in order, each
through its own skill, and you stop at the video gate. The `vg` tool does the API work and
enforces the money rules; your job is judgment, prompts, checking outputs, and talking to the human.

Before anything else, confirm you are in a harness workspace: `2_Tools/vg/vg.py` must exist in the
current workspace root. If it does not, say so and stop.

## Rules that are never broken

1. **No video without an explicit yes.** Before any `vg video` run, show the human the board and
   the per-shot cost, and wait for a clear yes in chat. Only then run `vg approve video`. Never
   approve on your own, never "assume it's fine", never work around a `REFUSED` message.
2. **Images need no approval** (they are cheap: 6–16 credits). Generate them, then look at every
   one before moving on.
3. **Never edit `project.json`** by hand. It is the ledger of what was spent and approved. Only
   the tool writes it. You write `1_Script/Shotlist.json`.
4. **Never print, echo, log or commit the API key.** It lives in `.env` only.
5. **Obey the client's rules** in `Shotlist.json` `rules` (for example "houses are real footage
   only"). A beat the brief marks as real footage or motion graphic stays that way.
6. **Never re-submit a task that timed out.** Run `vg resume`. Re-submitting pays twice.
7. **Prompts in English; dialogue and on-screen text in the video's language.**
8. **File names**: Title_Case_With_Underscores. The tool versions its own generated media `_v1`,
   `_v2`, ...; you version documents and final deliverables `_vX.Y` (e.g.
   `Script_Acme_Launch_v1.0.md`, `99_Output/<Project>_v1.0.mp4`).
9. **Never run `vg approve` through script, expect, a pty, tmux or any terminal you control; only
   the human types the code.** You may open the command in the human's own terminal panel for
   them, but the human types the code. This is friction against accidental or casual approval, not
   a wall against a hostile agent — the hard limit is a dedicated kie.ai key with a total credit cap.
10. **Only the human edits `.env`.** You only check it, with `vg doctor`; never change
    `VG_APPROVAL_MODE`, `VG_BUDGET_PROJECT` or `VG_MAX_PER_CALL` yourself — a cap refusal means ask
    the human whether to raise it.
11. **The human approves the visuals as images before any video.** No storyboard or frame image
    before the human approves the look (`vg approve look`), and no video before they approve the
    whole reel as images (`vg approve visuals`). Review the reel as a whole (one world, one time of
    day, one grade, one graphic style, a story that pays off its hook), never only shot by shot. Run
    these commands only after the human's explicit "approved" in chat; the tool refuses otherwise.

## The pipeline

Run from the workspace root. `vg` below means `python3 2_Tools/vg/vg.py`.

| # | Stage | Skill | Main commands | Done when |
|---|---|---|---|---|
| 0 | Setup | `vg-setup` | `vg doctor` | doctor shows no FAIL |
| 1 | Project | — | `vg new <Slug> --client "Name"`, copy the brief into `0_Source/` | folder exists, brief inside |
| 2 | Scene | `vg-scene` | write `1_Script/Shotlist.json` including the `look` block, `vg validate -p P` | valid; beats cover the brief; the look is written |
| 3 | **LOOK** | `vg-storyboard`, `vg-image-prompt` | `vg image -p P --stage look`, `vg board -p P` → show → `vg approve look -p P` | **the human said "approved"** to the style frames |
| 4 | Reference sheets | `vg-reference-sheets`, `vg-image-prompt`, `vg-image` | `vg image -p P --stage refs` | every sheet looked at and accepted |
| 5 | Storyboard + frames | `vg-storyboard`, `vg-image-prompt`, `vg-image` | `vg image -p P --stage storyboard`, `--stage frames` | panels match the script, the look and each other |
| 6 | Audio + edit plan | `vg-edit` (§ Audio first) | narration takes and music in `6_Edit/1_Audio/`, then `6_Edit/Edit_Spec.json` cut to the narration's phrases (timing, text, map, photos, captions, transitions, sfx) | the human picked the voice; every beat has its picture, words and sound |
| 7 | **SEQUENCE REVIEW** | `vg-storyboard`, `vg-edit` | `vg edit animatic -p P`, `vg board -p P` → show → `vg approve visuals -p P` | **the human said "approved"** to the whole reel as images |
| 8 | Video prompts | `vg-video-prompt` | edit `video_prompt` in Shotlist, `vg validate -p P` | prompts describe motion, dialogue fits |
| 9 | Identities | `vg-video` | `vg character create -p P --name <Name>` (character-mode shots only) | ids shown in `vg status -p P` |
| 10 | **VIDEO GATE** | `vg-video` | `vg estimate -p P --stage video`, `vg board -p P` → ask → `vg approve video -p P` | the human said yes |
| 11 | Video | `vg-video` | pilot `vg video -p P --shots S01`, then `vg video -p P --all` | every clip watched and accepted |
| 12 | Edit | `vg-edit` | `vg edit final -p P --draft`, then `vg edit final -p P` | final file in `99_Output/` |

Between stages, post a short progress note to the human (what was made, credits spent, what is
next) so they can redirect early. Stages 3 (look), 7 (sequence review) and 10 (video gate) need the
human's explicit approval; the others do not. Identity
creation (stage 9) has an unmeasured-in-advance cost — the ledger records whatever the balance
actually dropped by after the call — so tell the human before **every** `vg character create` call
for a project, the same as you would before a video spend, including a re-create after the
character's portrait/body version, description or voice changed (a stale identity makes `video`
and `approve` refuse with exit 1 until it's re-created).

## The two visual reviews, exactly

Both are loops: show, collect notes, fix only what was flagged, show again, until the human says
"approved". Look at every image yourself before you show it.

1. **Look** (stage 3): generate the style frames, `vg board -p P`, send the human the style frames
   and the look text. On their explicit "approved": `vg approve look -p P`. Until then the tool
   refuses every storyboard and frame image.
2. **Sequence** (stage 7): with every frame generated and `6_Edit/Edit_Spec.json` written, run
   `vg edit animatic -p P` (the whole reel as stills at edit timing, captions and graphics, no
   audio) and `vg board -p P` (filmstrip). Send both. Judge the reel as a whole: does every shot
   live in the same world and light, does the story pay off the hook, does the product get screen
   time, do the graphics use one style and stay off faces? On their explicit "approved":
   `vg approve visuals -p P`. It refuses unless the latest animatic shows exactly the current images
   and edit plan, so re-render after every fix.

Changing a style frame, the look text, any frame, a photo the edit plan uses, or the edit plan's
text or timing afterwards voids the approval; show it again. `vg status -p P` prints both gates.

**How the human reviews images: the review page.** At both reviews, after you have looked at every
image yourself (and, for the sequence review, rendered the animatic), run `vg review -p P` in the
background and tell the human the page is open. On it they see the look, the reference sheets and
every beat, switch takes, write a change note next to a picture, and approve by clicking (in
`VG_APPROVAL_MODE=terminal` the page shows them the approve command to type instead). When they click
**Done, back to the agent**, the command prints `GATE`, `NOTE` and `NEXT` lines. A note is an
instruction for the prompt: re-roll or re-prompt exactly what it names, render the animatic again,
and open the page again. Repeat until both gates say approved. Never click the page's buttons or call
its API yourself; the page is the human's. Without a browser, fall back to the board plus chat.

## The video gate, exactly

0. `vg status -p P` → both the look gate and the visuals gate must say "approved".
1. `vg validate -p P` → must be valid.
2. `vg board -p P` → give the human the board path to open.
3. `vg estimate -p P --stage video` → gives the per-shot table and total. A character-mode shot
   whose identity isn't created yet shows as an `ident` row, "cost unknown until created" — that
   character needs `vg character create` before its shots can be estimated for real.
4. `vg credits` → the current balance.
5. Tell the human, in this shape:

   > Frames are ready for review: `<board path>`.
   > Video would cost **N credits** for K clips (balance B): S01 character 8s 105 · S02 frames 4s 63 · …
   > Approve pilot **S01** for **105 credits**, or all for **N**?

6. **Stop.** Wait for the answer.
7. On a yes: `vg approve video -p P --shots <approved> --confirm <the total the human just agreed
   to>`. `--confirm` is always the total for exactly the shots being approved right now — the
   pilot's own cost when only the pilot was approved, not the grand total for every shot. If
   `approve` prints a different total than the human agreed to, **stop and ask again** — never
   retry the same command with the number the tool printed. On the real terminal
   (`VG_APPROVAL_MODE=terminal`, the default from `.env`), `approve` then shows the table and asks
   for a random 4-digit code typed by a human on `/dev/tty`; your shell has no terminal, so you
   cannot type it. It replies `REFUSED: Approval must be typed by the human in a terminal ...` with
   the exact command to run, which now starts `cd '<workspace>' && python3 2_Tools/vg/vg.py approve
   video -p <project> ...` (keeping `--new-take`/`--resolution`/`--allow-untested`). Give the human
   that command to run in their own terminal (or, in Claude Code desktop, offer to open it in their
   terminal panel) and wait for them to type the code — **never run it through script, expect, a
   pty, tmux or any terminal you control; only the human types the code.** Only then run
   `vg video -p P --shots <approved>` — the same `--shots`/`--all` that was just approved, never
   `--all` after approving only a subset.
8. Watch every clip (see `vg-video`), report, and repeat 5–7 for the rest — each approval pays for
   exactly one take of one shot; a re-roll, a retry after a failed take, or the next batch needs its
   own new yes for its own remaining total and its own `approve` call, never a re-use of an earlier
   one.

If a frame, prompt, mode or duration changes after approval, the tool voids that shot's approval.
Ask again; do not look for a way around it. A target left in state `submitting`, `unknown` (a crash
or network error while a task was in flight) or a `pending` task that can never finish blocks
further approval/video on it until the human checks the kie.ai dashboard: the task is there →
`vg adopt -p P --target <kind:id> --task-id <id>` so `vg resume` downloads it; nothing was created →
`vg release -p P --target <kind:id>`. A released row becomes `abandoned` and still counts toward
the budget at its estimate; either way, a video target needs a brand new approval afterward.

## Starting and resuming

- **New video**: `vg new <Client>_<Angle> --client "<Client>"`, copy the brief into
  `5_Projects/<folder>/0_Source/`, then the `vg-scene` skill.
- **Resume**: `vg status -p P` and `vg board -p P`, read `Shotlist.json`, then continue at the first
  stage that is not done. Pending tasks → `vg resume -p P` first.

## Where things are

| What | Where |
|---|---|
| Command reference | `1_Skills/vg-director/references/cli.md` |
| Shotlist format | `1_Skills/vg-director/references/shotlist-schema.md` |
| Models and prices | `2_Tools/vg/models/*.json` (`vg models`) |
| Project plan | `5_Projects/<project>/1_Script/Shotlist.json` |
| Review board | `5_Projects/<project>/Board_<Project>.html` |
| Design | `4_Docs/Specs/` |

## When something fails

| Exit | Meaning | Do |
|---|---|---|
| 1 | usage, validation or bad-flag error | read the message, fix Shotlist or the command |
| 2 | only ever a safety refusal (output starts with `REFUSED:`) | report it to the human; never work around it |
| 3 | provider error (output starts with `PROVIDER ERROR:`) | read the code (402 no credits, 422 bad field, 429 rate limit); fix or report |
| 130 | interrupted (Ctrl-C, closed terminal, killed process) | run `vg status -p P` and `vg resume -p P`; the human checks the kie.ai dashboard before any `vg release`/`vg adopt` |

## Reporting to the human

Short and plain: what was made (paths), credits spent this stage and in total, what failed and
why, the next step. Show images when the interface allows it. Never claim a clip or image is good
without having looked at it.
