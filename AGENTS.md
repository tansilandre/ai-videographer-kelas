# AI Videographer — agent instructions

This workspace is an AI video production harness. Any request to make, plan, generate or edit a
video starts with the **`vg-director` skill** (`1_Skills/vg-director/SKILL.md`). Read it first; it
names the other skills in pipeline order.

## Non-negotiable

1. **No video spend without the human's explicit yes.** Show the review board and the
   per-shot cost (`vg estimate -p P --stage video`) first. Never run `vg approve` on your own
   initiative. `VG_APPROVAL_MODE` in `.env` decides how the human says yes: `page` (they click
   Approve on the review page, with the cost shown; the command line always refuses), `terminal`
   (they type a random code in their own terminal; an agent's shell is refused and must hand them
   the exact command), or `chat` (you run `vg approve` after their explicit yes). Each approval pays for
   exactly one take; a failed clip used up its approval too, so a retry needs a fresh yes and a
   fresh `vg approve`.
2. **Never run `vg approve` through script, expect, a pty, tmux or any terminal you control; only
   the human types the code.** An agent may open the command in the human's own terminal panel for
   them, but the human types the code. This is friction against accidental or casual approval, not
   a wall against a hostile agent — the hard limit is a dedicated kie.ai key with a total credit cap.
3. Images may be generated without asking. Look at every image before using it downstream.
   **But the human approves the visuals before video:** no storyboard or frame image before the
   human approves the look (`vg approve look`), and no video before they approve the whole reel as
   images (`vg edit animatic` + board, then `vg approve visuals`). In page mode the human clicks
   these approvals; otherwise run them only after their explicit "approved" in chat.
4. Never edit `5_Projects/*/project.json` (the spend ledger). Write only `1_Script/Shotlist.json`.
5. Never print, echo, log or commit `KIE_API_KEY` or anything from `.env`.
6. **Only the human edits `.env`.** Keys go in through `vg setup` (a local page the human fills in); never
   ask for a key in the chat. The agent only checks `.env` with `vg doctor`; never change
   `VG_APPROVAL_MODE`, `VG_BUDGET_PROJECT` or `VG_MAX_PER_CALL` yourself — a cap refusal means ask
   the human whether to raise it.
7. Follow the client's rules recorded in `Shotlist.json` `rules`.
8. A task that timed out is collected with `vg resume`, never re-submitted. A target stuck in the
   `submitting`/`unknown`/`pending` ledger state stays blocked until a human checks the kie.ai
   dashboard: task exists there → `vg adopt -p P --target <kind:id> --task-id <id>`; nothing was
   created (or a `pending` row that can never finish) → `vg release -p P --target <kind:id>`.
   Released rows become `abandoned` and still count toward the budget at their estimate.
9. **The review page is the human's.** Open it with `vg review -p P --detach` (returns at once; the page
   runs until the human clicks Done) and wait for the human to say they are done; `vg next -p P` or
   `vg review -p P --summary` then shows their clicks and notes. Never click its buttons, call its API
   or approve on the human's behalf. Act on every `NOTE` line before asking again.

## Tool

`vg` below and in every skill means `python3 2_Tools/vg/vg.py` — there is no `vg` on PATH, so the
full path is run every time. Most commands take `-p P` for the project folder, e.g.
`python3 2_Tools/vg/vg.py estimate -p P --stage video`. **`vg next -p P` prints the one next step**
(the command to run, the file to write, or what to ask the human): follow it when unsure. Reference:
`1_Skills/vg-director/references/cli.md`. Run `vg doctor` if anything looks wrong.

## One source of truth

This folder **is** the public GitHub repo https://github.com/tansilandre/ai-videographer-kelas. There is no
other copy: the harness, skills, WorkBuddy expert, setup scripts and every class material live here
(`6_Kelas/`: lessons, handouts, deck and its builder in `6_Kelas/4_Deck/Build/`, run-sheet) and are pushed
there. Private work stays in this folder but git ignores it: `5_Projects/`, `99_Output/`, `0_Source/`,
`4_Docs/Private/` (client-named originals and plans) and `.env`. The real client's name must never be
committed; the pre-commit hook refuses it (enable once per clone: `git config core.hooksPath 2_Tools/git_hooks`).
Class material goes into `6_Kelas/`, never into `99_Output/` or a second folder; keep only the newest
version of a class file there (git keeps the old ones).

## Workspace convention

- Folders are numbered by stage; `0_Source/` holds untouched inputs, `99_Output/` final deliverables.
- File names: `Topic_Name.ext` in Title_Case with underscores; dated items `YYYY-MM-DD_Topic.ext`.
- Versioning: the **tool** names its own generated media (images, frames, clips, the roughcut)
  `_v1`, `_v2`, ... — plain integers, never edit these by hand. **You** name documents and final
  deliverables `_vX.Y` (e.g. `Script_Acme_Launch_v1.0.md`, `99_Output/<Project>_v1.0.mp4`).
- Never overwrite a delivered version; save the next version.

## Developing the harness itself

- Tool code: `2_Tools/vg/` (Python 3.9+, standard library only). Tests:
  `python3 -m unittest discover -s 2_Tools/vg/tests`. Run them before every commit.
- New model: one JSON file in `2_Tools/vg/models/` (see its README), marked `untested` until a paid
  pilot confirms field names and price.
- Design and decisions: `4_Docs/Specs/`.
