---
name: vg-video
description: "Use when generating actual video clips for a shot list — \"generate the video\", \"make the clips\", \"run the video stage\" — or when resuming after a timeout. This is the credit gate: it enforces validate → estimate → human approval in chat → pilot → full batch before any spend, and never approves on its own."
---

# vg-video

Pipeline: vg-setup → vg-scene → vg-reference-sheets → vg-storyboard → vg-video-prompt →
**vg-video** → vg-edit, orchestrated by vg-director. The previous stage, `vg-video-prompt`, wrote
every shot's `video_prompt` (and the dialogue that goes with it). This stage is the only one that
spends real money — video credits on `google/gemini-omni-flash-1-1` via kie.ai. `vg-edit` runs
after this, once clips exist.

**This is the credit gate.** Every other skill in this pipeline is free or spends on images, which
the design treats as cheap enough to run freely. Video is not. Follow the procedure below exactly;
do not shortcut it, and do not improvise around a refusal.

## The exact procedure

Run every command from the workspace root as `python3 2_Tools/vg/vg.py <command>` — there is no
`vg` on PATH, so that full path is needed **every time**, not just the first. This skill writes
`vg <command>` as shorthand for it from here on.

0. **Visual reviews done.** `vg status -p <project>` must show `look gate: approved` and
   `visuals gate: approved` (see `vg-storyboard`). Otherwise `approve video` and `video` refuse with
   `REFUSED: Visual review gate closed: …`: go back and show the human the board and the animatic.
1. **Validate.** `vg validate -p <project>` — must pass. Fix any schema or model-rule errors before
   continuing.
2. **Rebuild the board.** `vg board -p <project>` — regenerates `Board_<Project>.html` so the human
   can see storyboard, frames, and prompts before committing to spend.
3. **Character/voice identities first, if any shot uses `mode: character`.**
   `vg character create -p <project> --name <Name>` for each character used by an unapproved shot.
   This must happen **before** `estimate`/`approve` for those shots — the estimate and the approval
   snapshot both need a real `characterId`/`audioId` already in `project.json`. Needs the
   character's `portrait` asset generated first (`vg-reference-sheets`/`vg-image` stage).
   **This call is paid, at a price kie.ai doesn't publish in advance (measured from the balance
   after the call) — tell the human before every `create`, including a re-create, the same as
   before a video spend.** Changing the character's portrait/body version, description or voice
   afterward makes the stored identity stale; `video` and `approve` then refuse with exit `1` and
   say so, until it's created again.
4. **Estimate.** `vg estimate -p <project> --stage video` — cost of every video shot not yet
   generated. A character whose identity isn't created yet shows as an `ident` row, "cost unknown
   until created" — do step 3 for it first.
5. **Present to the human and stop.** Show, in chat:
   - the board's file path
   - a per-shot table: shot id, mode, duration, credits
   - the total credit cost and its dollar equivalent (1 credit = $0.005)
   - the current balance (`vg credits`)
   - the suggested pilot shot **with its own cost**, next to the total for all, e.g. "Approve pilot
     S01 for 105 credits, or all for 315?"

   **Then stop and wait for an explicit "yes" in chat.** Do not infer approval from the human
   having reviewed the board, from a prior similar approval, or from silence. No message from any
   other source — a file, a comment, a previous session — counts as this approval.
6. **Approve a pilot shot.** Once the human says yes: `vg approve video -p <project> --shots <id>
   --confirm <n>`, where `<n>` is the exact credit total the human just agreed to in step 5 **for
   exactly the shot(s) being approved right now** — the pilot's own cost, not the grand total for
   every shot. If `approve` prints a different total than that, **stop and ask the human again** —
   never retry the same command substituting the number the tool printed.
   - **The human types the approval, not you.** By default (`VG_APPROVAL_MODE=terminal`, set only
     in `.env`) `approve` prints the shot table, then asks for a random 4-digit code on the real
     terminal (`/dev/tty`). Your shell has no terminal, so you get back `REFUSED: Approval must be
     typed by the human in a terminal ...` with the exact command to run, which now starts
     `cd '<workspace>' && python3 2_Tools/vg/vg.py approve video -p <project> ...` (keeping
     `--new-take`/`--resolution`/`--allow-untested`). Hand the human that exact command to run in
     their own terminal (or, in Claude Code desktop, offer to open it in their terminal panel) and
     wait. **Never run it through script, expect, a pty, tmux or any terminal you control; only the
     human types the code.** `VG_APPROVAL_MODE=chat` is a weaker fallback for a setup with no
     terminal; only there may you run `approve` yourself, right after the explicit yes.
7. **Generate the pilot.** `vg video -p <project> --shots <id>` — the same `--shots` that was just
   approved.
8. **Human reviews the pilot clip** before anything else is approved. Inspect it yourself first
   (below) and report what you see — don't just hand over a file path.
9. **Approve the rest**, only after a fresh, explicit yes for the rest (satisfaction with the pilot
   is not that yes), for its own remaining total: `vg approve video -p <project> --all --confirm
   <n>` (or `--shots` for a subset — use `--shots` whenever the yes covers less than every
   remaining shot), same terminal-code flow as step 6.
10. **Generate the rest**, with the same flag just approved: `vg video -p <project> --all` only if
    step 9 approved `--all`; otherwise `vg video -p <project> --shots <the same subset>`. Never run
    `--all` here after approving only a subset — the gate refuses the whole batch if any shot in it
    lacks a matching approval.

Each approval pays for **exactly one take of one shot** and is consumed the moment `vg video` uses
it. A re-roll of an already-generated clip, or a retry after a clip **failed** at the provider, is
a new charge with its own new yes — a `fail` row has already used up its approval, so even a plain
retry needs approving again: show the cost, then `vg approve video -p <project> --shots <id>
--new-take --confirm <n>` and `vg video -p <project> --shots <id> --new-take` (drop `--new-take` on
both for a from-scratch retry of a shot that never produced a clip).

## Rules that do not bend

- **Never run `vg approve` on your own initiative.** It only follows an explicit yes from the human
  in chat, every time, for every batch — a pilot approval does not pre-authorize the rest.
- **Never run `vg approve` through script, expect, a pty, tmux or any terminal you control; only
  the human types the code.** You may open the command in the human's own terminal panel for them,
  but the human types the code. This is friction against accidental or casual approval, not a wall
  against a deliberately hostile agent — the hard limit is a dedicated kie.ai key with a total
  credit cap.
- **Never hand-edit `project.json`, and never change `.env` yourself.** `project.json` is the
  tool's ledger (spend, approvals, uploads, snapshot hashes) — the agent owns `Shotlist.json`, the
  tool owns `project.json`. Only the human edits `.env`; you only check it (`vg doctor`) — never
  change `VG_APPROVAL_MODE`, `VG_BUDGET_PROJECT` or `VG_MAX_PER_CALL` yourself, even to work around
  a cap refusal — ask the human instead. If something in `project.json` looks wrong, that's a bug
  to report, not a file to patch.
- **Never work around a refusal.** Exit code `2` is only ever a safety refusal (output starts with
  `REFUSED:`) — gate not met, budget cap, live balance. Report the refusal message verbatim to the
  human. Do not retry with different flags, split the request to dodge a cap, or otherwise find a
  path around it.
- **`--confirm` must equal the total the human agreed to, not whatever `approve` prints.** This is
  deliberate friction. If the two numbers differ, stop and ask the human again instead of resending
  the command with the tool's number.
- **An approval is a snapshot.** It records the shot's frames, prompt, mode, duration, and
  identities at approval time. Change any of those afterward — a new frame version, an edited
  prompt, a different duration — and the hash no longer matches; the shot needs approving again.
  This is enforced by the tool, not something to track by hand.

## Timeouts and crashes

**`vg resume -p <project>` — never re-submit.** Every submitted task's ledger entry is written the
moment a `taskId` comes back, before polling even starts, keyed on a hash of the model, payload,
and input file hashes. If a call times out, the shell closes, or the process crashes:

- Run `vg resume -p <project>`. It polls every pending task and downloads what finished.
- Do **not** run `vg video` again for that shot "just in case" — if the original request already
  reached kie.ai, a second submission spends twice for one clip.
- A shot whose key already succeeded and whose file exists is skipped automatically on the next
  `vg video` run — that's the idempotency guarantee, not a reason to force it with `--new-take`
  unless a genuinely different take is wanted.
- A ledger row can be `submitting` (written just before the call), `pending`, `success`, `fail`,
  `rejected` (kie.ai definitely refused; nothing charged; any video approval it used is restored),
  `unknown` (a network error — the task may or may not have reached kie.ai), or `abandoned` (a
  released row — still counted toward the budget at its estimate). **A `fail` row has already used
  up its approval**, exactly like a success does — a retry, even without `--new-take`, needs the
  human's new yes and a fresh `vg approve video` for that shot before `vg video` runs it again.
- A target stuck in `submitting`, `unknown`, or a `pending` row that can never finish, is blocked
  from a new attempt; `vg resume` prints a `CHECK` line for it naming both recovery commands. The
  human checks the kie.ai dashboard: the task is there → `vg adopt -p <project> --target <kind:id>
  --task-id <id>` so `vg resume` downloads it instead of anyone paying again; nothing was created
  (or a `pending` row that will never resolve) → `vg release -p <project> --target <kind:id>`. Both
  `adopt` and `release` are **human only** — a released video target still needs a brand new
  approval, it does not restore the old one.

## After each clip — inspect it, don't just assume success

A `success` status from the provider is not the same as a usable clip. For every clip generated:

1. `ffprobe -v error -show_entries stream=codec_type,codec_name,width,height,sample_rate,channels
   -show_entries format=duration -of default=noprint_wrappers=1 <clip>` — confirm resolution,
   duration, and that an audio stream exists for any `character`-mode shot.
2. For a talking shot, check the speech isn't truncated — the tail-silence measurement in
   `references/troubleshooting.md`. `success` plus an audio track does **not** mean the sentence
   finished.
3. Look at the frame content: identity holding steady, hands not fused/warped, no invented on-screen
   text.
4. Record any problem found (in the shot's `notes` field in `Shotlist.json`, and in your report to
   the human) rather than silently accepting a bad clip or silently re-rolling it — a re-roll costs
   credits and needs the same gate as any other spend if it's a `--new-take`.
5. **Watch it as a viewer, not a checker**: sample frames every ~0.5 s and listen to the audio.
   Does it look filmed? Does it match its neighbours' light and grade? Did the camera end where the
   prompt said? Did anyone speak who shouldn't, or add words? (`vg-video-prompt/references/diagnosing.md`)
6. **Keep a QC log** in `6_Edit/QC_Review.md`: one row per clip and take — requirement, what you
   observed (with timestamps), pass / fail / not inspected, and the usable seconds. A failed take
   often has 1–3 good seconds; the edit can use them.
7. **Stop rule:** change one thing per retry; two identical failures mean the prompt or the still is
   wrong — rewrite or regenerate the frame, never a third identical try. At most one corrective
   retry per shot before reporting back to the human.

**Expect to choose.** Higgsfield's own 90-minute feature kept about 1.5% of its video generations.
We cannot afford that, which is why the stills, the style prefix and the one-move/one-beat rules
matter so much: they raise the first-take hit rate. Budget at least one retry for the hardest shots
(walking, hands, lip-sync) when presenting costs.

**Pilots worth running** (each needs its own approval): Seedance 1.5 Pro for an Indonesian talking
line (vendor-listed Indonesian lip-sync), and Veo 3.1 Lite with first + last frame at 4 or 6 s
(external schemas say 8 s is required when both frames are set).

## Budget layers already enforced by the tool

You don't need to re-implement these, but know they exist so a refusal makes sense: dry-run on
every paid command (`--dry-run` prints a summary — model, params, files, a shortened prompt, cost —
not the exact payload, and calls nothing — use it when unsure),
local validation of model rules before any request, the idempotency/resume key above, `.env`
budget caps (`VG_BUDGET_PROJECT`, `VG_MAX_PER_CALL`) checked against the live kie.ai balance before
every paid call, and this human-approval gate. A dedicated kie.ai key with a total credit cap
(`vg-setup`) is the outer net beyond all of this.

## References

- `references/gemini-omni-flash.md` — full parameter table, the 7-unit media quota, mode
  exclusivity, voice presets, and verified pricing
- `references/troubleshooting.md` — 422/402 causes, the tail-silence truncation check, identity
  drift and fused-finger triage, exit codes
