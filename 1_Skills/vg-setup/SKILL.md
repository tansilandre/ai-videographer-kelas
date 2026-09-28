---
name: vg-setup
description: Use when doing first-time setup or an environment check — "set up the harness", "install", "vg doctor", "check my setup", "copy this to a new workspace", "add a new model". Covers requirements, .env configuration, install.sh, and extending the model registry.
---

# vg-setup

Pipeline: **vg-setup** → vg-scene → vg-reference-sheets → vg-storyboard → vg-video-prompt →
vg-video → vg-edit, orchestrated by vg-director. This is the first stage — there is no previous
skill. `vg-scene` runs next, once `vg doctor` passes clean. Nothing here spends credits. There is
no `vg` on PATH — every command below is shorthand for `python3 2_Tools/vg/vg.py <command>`.

## Requirements

| Requirement | Why | Needed for |
|---|---|---|
| Python ≥ 3.9, standard library only | runs `vg` — no `pip install` | every stage |
| ffmpeg + ffprobe | roughcut, clip inspection, animatic, final mix | `vg-video` (inspection), `vg-edit` |
| macOS + Xcode Command Line Tools (`swiftc`) | the caption and graphics renderer (`2_Tools/vg/render/overlay.swift`) | `vg edit animatic`, `vg edit final` |
| A kie.ai API key | image and video generation | `vg-reference-sheets`, `vg-storyboard`, `vg-video` |
| An OpenRouter API key (`OPENROUTER_API_KEY`) | narration and music (`vg audio voice`, `vg audio music`) | `vg-edit` (audio first) |

Nothing here requires `pip install` — the tool is standard-library Python by design, so there's no
dependency drift to manage between machines.

## Install

```bash
bash install.sh
```

Plain `bash install.sh` checks the versions above, links `1_Skills/` (one link) into
`.claude/skills`, `.agents/skills`, `.workbuddy/skills` and `.codebuddy/skills` for the **current
project** — so Claude Code, Codex/Cursor/Gemini CLI, WorkBuddy and CodeBuddy all see the same
skills without copying them — copies `.env.example` to `.env` if `.env` doesn't already exist
(never touching an existing one), sets `.env` to `chmod 600` (owner read/write only) either way,
and finishes by running `vg doctor`.

`bash install.sh --global` additionally links every `vg-*` skill (one link per skill this time)
into the **user-level** folders `~/.claude/skills`, `~/.agents/skills`, `~/.workbuddy/skills` and
`~/.workbuddy-ai/skills`, so other workspaces/agents on the same machine can see them too.
Re-running `install.sh` (with or without `--global`) is always safe: it prints `ok` for a link
that's already correct, and **recreates/repoints** any link that's missing or points somewhere
else — including a `vg-*` link left over from `--global` on a different workspace, which gets
repointed at this one (`repoint <link> (was <old target>)`).

## `.env`

**Only the human edits `.env`.** The agent's part is checking it — `vg doctor` — never writing to
it or changing a value in it, even to work around a cap refusal (ask the human instead). Copy
`.env.example` to `.env` if `install.sh` hasn't already done it, and the human fills in:

| Variable | Meaning |
|---|---|
| `KIE_API_KEY` | the kie.ai API key this harness calls with |
| `OPENROUTER_API_KEY` | OpenRouter key for `vg audio voice` and `vg audio music` (the short name `OPENROUTER` also works) |
| `VG_BUDGET_PROJECT` | total credit cap enforced per project, checked before every paid call |
| `VG_MAX_PER_CALL` | credit cap enforced per single call |
| `VG_IMAGE_MODEL` | default image model id (registry key in `2_Tools/vg/models/`) |
| `VG_VIDEO_MODEL` | default video model id (registry key in `2_Tools/vg/models/`) |
| `VG_APPROVAL_MODE` | `terminal` (default) or `chat` — how `vg approve video` confirms with a human; see `vg-video/SKILL.md` |

Budget caps and `VG_APPROVAL_MODE` are read **only** from `.env` (or the built-in default) — a
process environment variable of the same name is ignored for these, specifically so a command
prefix like `VG_BUDGET_PROJECT=99999 vg ...` cannot raise the cap.

`.env` is git-ignored. **Never print the key to chat, a log, a commit, or a board file, and never
commit `.env`.** If a key ever needs to be shared or rotated, that's a step for the human to do
directly in their own terminal or password manager — not something to paste through this agent.

## Recommended: a dedicated, capped kie.ai key

Create a separate API key for this harness at kie.ai/api-key and set an hourly, daily, or total
credit cap on it, rather than reusing a key shared with other work. This cap is the outer safety
net — it holds even if every check inside `vg` were somehow bypassed. Put that key's value in
`.env`, never anywhere else.

## `vg doctor`

```bash
python3 2_Tools/vg/vg.py doctor
```

Run this first, and any time something seems off. It checks Python, ffmpeg (and whether it has
`libass`, needed only for a raw-FFmpeg caption fallback — see `vg-edit`), `swiftc` (the caption and graphics renderer), the
OpenRouter key (`vg audio`), that `.env` exists
and parses, that the API key is present, the live kie.ai balance (`vg credits`), and that `.env`
isn't readable by other users on the machine (warns `.env permissions: readable by other users:
chmod 600 .env` if so — `install.sh` sets this correctly on a fresh install, but a manually copied
or edited `.env` can drift). A clean `vg doctor` is the precondition for starting real work, not a
courtesy check.

## Starting a project

```bash
python3 2_Tools/vg/vg.py new <Slug> [--client "Client Name"]
```

Creates `5_Projects/<YYYY-MM-DD>_<Slug>/` from the template in `3_Templates/`. `vg-scene` picks up
from there.

## Copying the harness to a new workspace

1. Copy the whole repository — skills, `2_Tools/vg`, `3_Templates`, docs. Leave `5_Projects/` and
   `99_Output/` behind; they're per-workspace and already git-ignored.
2. Create a fresh `.env` from `.env.example` in the new location — never copy an existing `.env`
   with a live key into a new workspace.
3. Run `bash install.sh` again in the new location so skills get linked for whichever agent will
   run there (Claude Code, WorkBuddy, Codex, ...).
4. Run `vg doctor` to confirm the new environment is clean before starting a project.

## Adding a new model

Adding a model to an **existing provider** (the kie.ai jobs API this harness already speaks) is a
data change, not a code change: add one JSON file to `2_Tools/vg/models/` describing the provider,
model id(s), field names, allowed values and types, limits, exclusivity rules, and a pricing table.
**Don't invent the file's shape from this description — read `2_Tools/vg/models/README.md` for the
exact format** before writing one; if that file doesn't exist yet, ask rather than guessing at
fields.

Adding a genuinely **new provider** (a different API shape, e.g. an MCP-only tool that can't be
called from Python) means one new file in `2_Tools/vg/providers/`. `vg models` lists everything in
the registry along with its test status.

**An untested model is refused by the tool unless explicitly allowed.** A model shipped "from docs,
marked untested" (the way `veo-3-1.json` was added to prove the registry handles a second video
model) exists to show the registry mechanism works — it is not cleared for real spend until someone
verifies it live and updates its status. Don't work around that refusal by editing the registry
entry to claim it's tested; get it actually verified first, or ask the human to explicitly accept
the risk for a specific run.

## Don't invent commands

Every command in this skill, and in every other `vg-*` skill, exists in
`1_Skills/vg-director/references/cli.md`. If a task seems to need a flag or subcommand that isn't
listed there, it doesn't exist yet — say so and ask, rather than guessing at a plausible-looking
one.
