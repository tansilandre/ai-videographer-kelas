# AI Videographer

An agent harness that turns a client brief into short-form vertical video with AI image and video
models. It is built so that any capable coding agent (Claude Code, Tencent WorkBuddy, Codex,
Cursor) can run it end to end, and so that it never burns credits on a video nobody approved.

```
brief → scenes & shot list → reference sheets (character · location · product)
      → storyboard panels → first + last frame per shot → video prompts
      → ✋ video gate (you approve, cost shown) → clips → rough cut → edit
```

The idea is the one good human AI videographers already follow: lock the look on cheap still
images first, then only "make the image move" once every frame is right. A 2K image costs
10 credits; a 4–10 s clip costs 63–126. Iterating on stills is the cheap part.

## What's inside

| Folder | What it is |
|---|---|
| `1_Skills/` | 10 agent skills (`SKILL.md` format). Start with `vg-director`. |
| `2_Tools/vg/` | `vg`, a small Python CLI (standard library only) that calls the APIs, keeps the ledger and enforces the money rules |
| `2_Tools/vg/models/` | one JSON file per model: fields, limits, prices. Add a model by adding a file |
| `3_Templates/` | the project folder template |
| `4_Docs/` | design spec and guides |
| `5_Projects/` | your video projects (git-ignored) |

Providers today: [kie.ai](https://kie.ai) with `gpt-image-2` for images and Google Veo 3.1 Lite
(`veo-3-1-lite`, 35 credits per 8 s 1080p clip) for video; `gemini-omni-flash-1-1` is registered too.
Narration and music come from [OpenRouter](https://openrouter.ai) (`vg audio`, a few cents per take).

## Quick start

Requirements: macOS (the caption and graphics renderer is Swift), Xcode Command Line Tools
(`xcode-select --install`), Python 3.9+, FFmpeg, a kie.ai API key, and an OpenRouter API key for narration
and music.

```bash
git clone <this repo> My_Videos && cd My_Videos
bash install.sh                 # creates .env, links skills for Claude Code / Codex / WorkBuddy
# put your keys in .env  ->  KIE_API_KEY=...  OPENROUTER_API_KEY=...
python3 2_Tools/vg/vg.py doctor
```

Then open the folder in your agent and say something like *"Here's a brief in
5_Projects/…/0_Source — make the video."* The agent follows `vg-director`.

Or drive it yourself:

```bash
vg() { python3 2_Tools/vg/vg.py "$@"; }
vg new Acme_Launch --client "Acme"           # 5_Projects/<date>_Acme_Launch/
# write 1_Script/Shotlist.json (see 1_Skills/vg-director/references/shotlist-schema.md)
vg validate -p Acme_Launch
vg image -p Acme_Launch --stage refs         # character / location / product sheets
vg image -p Acme_Launch --stage storyboard
vg image -p Acme_Launch --stage frames
vg board -p Acme_Launch                      # open Board_<Project>.html
vg character create -p Acme_Launch --name <Name>  # character-mode shots only; paid, price
                                                    # unpublished, measured afterwards — tell the
                                                    # human first, every time, including re-creates
vg estimate -p Acme_Launch --stage video
vg approve video -p Acme_Launch --shots S01 --confirm 105
vg video -p Acme_Launch --shots S01
```

`vg approve video` is where a human confirms in person: it prints the shot table, then asks you to
type a random 4-digit code on this same terminal before it records anything.

## Credit safety

Enforced in code, so a weaker model that skips instructions still cannot spend by accident:

1. **Dry run** on every paid command (`--dry-run`): prints a summary — model, params, input files,
   a shortened prompt, and the credit cost, not the exact request payload — and sends nothing.
2. **Local validation** of field names, types, limits and model-specific traps before any request,
   including per-target image aspect/resolution combinations, `file:` refs that try to leave the
   project folder, assets nothing uses, and dialogue outside character mode (an unlocked voice).
3. **No double spend**: every request has a content key. Done means skipped; pending means resumed
   by task id (`vg resume`), never re-submitted. The ledger is written before polling starts. A row
   left `submitting`, `unknown` (network error, outcome unclear) or a `pending` row that can never
   finish blocks that target until a human checks the kie.ai dashboard: the task is there →
   `vg adopt -p P --target <kind:id> --task-id <id>` so `vg resume` downloads it; nothing was
   created → `vg release -p P --target <kind:id>`. A released row becomes `abandoned` and still
   counts toward the budget at its estimate.
4. **Budget caps** from `.env`: per project and per request, plus a live balance check. Read only
   from `.env` — an environment variable of the same name cannot raise them. Only the human edits
   `.env`; the agent only checks it with `vg doctor`, and a cap refusal means ask the human, not
   raise it yourself.
5. **Video gate**: `vg video` refuses any shot without a matching, unused approval. `--confirm`
   must equal the total the human just agreed to in chat — if `vg approve video` prints a different
   number, stop and ask again, never resend the command with the tool's number. With
   `VG_APPROVAL_MODE=page` the human approves every gate by clicking on the review page
   (`vg review`), which shows each clip's cost and asks once more; the command line never approves.
   By default (`VG_APPROVAL_MODE=terminal`) `approve` asks a human to type a random code on a real
   terminal; an agent has none (WorkBuddy's agent shell is recognised and refused too), so it must
   hand the human the exact command to run
   (it now starts `cd '<workspace>' && python3 2_Tools/vg/vg.py approve video -p <project> ...`,
   keeping `--new-take`/`--resolution`/`--allow-untested`). **Never run `vg approve` through
   script, expect, a pty, tmux or any terminal you control; only the human types the code.** An
   agent may open the command in the human's own terminal panel for them, but the human types the
   code. An approval is a snapshot of the shot's frames, prompt, mode, duration and identity —
   change anything and it is void — and pays for **exactly one take**; a re-roll, or a retry after
   a failed take, needs a new yes and `--new-take` on both `approve` and `video`. This stops
   accidental or casual spend, not a deliberately hostile agent.
6. **Provider cap**: give the kie.ai key its own total credit limit at kie.ai/api-key — this is the
   actual hard wall beneath everything above.

## Shot modes

Gemini Omni cannot combine a hard first frame with a locked character or voice. Each AI shot
therefore picks a mode:

| Mode | Sent | Use for |
|---|---|---|
| `frames` | first frame (+ last frame) | b-roll, locations, products, transitions |
| `character` | character id + voice id + the panel as a soft reference | a recurring person speaking on camera |
| `text` | prompt only | exploration |

## Using it with other agents

`bash install.sh` links `1_Skills/` into `.claude/skills`, `.agents/skills`, `.workbuddy/skills`
and `.codebuddy/skills` for this project. `bash install.sh --global` additionally links every
`vg-*` skill into your user-level folders — `~/.claude/skills`, `~/.agents/skills`,
`~/.workbuddy/skills`, `~/.workbuddy-ai/skills` — so any workspace on the machine sees them.

- **Claude Code**: reads `CLAUDE.md` → `AGENTS.md`; skills from `.claude/skills`.
- **Codex / Cursor / Gemini CLI**: `AGENTS.md`; skills from `.agents/skills`.
- **WorkBuddy**: reads `AGENTS.md`; skills from `.codebuddy/skills`. Install the **AI Videographer
  expert** with `bash 2_Tools/workbuddy/install_workbuddy.sh` (`--add-models` also adds
  GLM-5.3-Flash and MiniMax-M3.1-Flash-Preview as custom models). Its playbook drives the
  pipeline with `vg next`, one step at a time, so a fast, cheap model can run it. Set
  `VG_APPROVAL_MODE=page` so every approval is a click on the review page, and keep the keys in the
  workspace `.env` (WorkBuddy's sandbox does not read your shell profile).

For any agent app: `vg next -p P` prints the one next step (command, file to write, or what to ask
the human), and `vg review -p P --detach` opens the review page without blocking the agent.

## Adding a model

Copy the closest file in `2_Tools/vg/models/`, change the model string, fields and prices, mark it
`"status": "untested"`, dry-run a shot, run one paid pilot, then mark it `live-tested`. A new
provider with a different API shape is one module in `2_Tools/vg/providers/`. See
`2_Tools/vg/models/README.md`.

## Development

```bash
python3 -m unittest discover -s 2_Tools/vg/tests
```

The tests use a fake provider and cost nothing. Design decisions live in `4_Docs/Specs/`.

## Roadmap

- MCP providers (e.g. Higgsfield) through the same registry, gate and ledger.
- More models: Veo 3.1 live test, Kling, Seedance.
