# The `vg` command-line tool

Run every command from the **workspace root**:

```bash
python3 2_Tools/vg/vg.py <command> [options]
```

There is no `vg` on PATH — every `vg <command>` below is shorthand for that full path, run in full
every time, not a literal command.

`-p/--project` takes a project folder name under `5_Projects/` (the full dated folder, e.g.
`2026-09-24_Acme_Launch`), or just the slug (`Acme_Launch`) if only one dated folder matches it —
if the slug matches several dated folders, the tool refuses and lists them, and the full folder
name must be given instead. `-p` can also be a path, or omitted entirely when the current directory
is inside a project folder.

Every paid command accepts `--dry-run`: it prints a summary — model, params, input files, a
shortened prompt, and the credit cost — not the exact request payload, and calls nothing. Use it
whenever you are unsure.

## Setup and info (free)

| Command | Does |
|---|---|
| `vg doctor` | checks Python, ffmpeg (+libass), swiftc, `.env`, the API keys, the balance, the approval mode, and the skills folders Claude Code and WorkBuddy read |
| `vg credits` | prints the kie.ai credit balance |
| `vg models` | lists models in the registry, their kind and test status |
| `vg new <Slug> [--client "Name"]` | creates `5_Projects/<YYYY-MM-DD>_<Slug>/` from the template |
| `vg validate -p P` | checks `Shotlist.json`: fields, ids, refs, modes, dialogue fit; warns on craft: unknown category/camera/size, an unpaid hook promise, product screen share below `format.product_share_min`, three cuts in a row with the same size and move |
| `vg status -p P` | every target with its state, version, and credits spent, plus the look gate and visuals gate lines |
| `vg estimate -p P [--stage images\|video\|all]` | cost of what is still missing |
| `vg board -p P` | rebuilds `Board_<Project>.html`: review gates, Look (style frames + look text), Filmstrip (every beat in timeline order + the latest animatic), references, timeline |
| `vg next -p P` | **the one next step**, from Shotlist.json, the ledger and the disk: `STAGE` (where the project is), then `RUN` (a command; `TIME` when it is long), `WRITE` (a file to write and the skill to read), `DO`, `NOTE` (the human's notes), `ASK` (stop and wait for the human), `THEN`, or `DONE`. Runs nothing. Start here when unsure. |
| `vg review -p P --detach` / `--summary` / `--stop` | for agent apps whose commands must end: `--detach` starts the review page in its own process, prints its link and returns (a second call reuses the open page); `--summary` prints the `GATE`/`NOTE`/`APPROVED`/`NEXT` lines without a page; `--stop` ends a detached page. |
| `vg review -p P [--port N] [--no-open]` | opens the **review page** on this machine (127.0.0.1, one-time token in the URL): the look text and style frames, the reference sheets and every reel beat with the frames behind it, takes to switch between (same as `vg select`), a change-note box per card, the animatic, Approve look / Approve reel buttons, and a Video section (once both are approved) with every clip, its cost and an Approve button that asks once more before it approves (in `VG_APPROVAL_MODE=terminal` the page shows the approve command to type instead; in `page` mode these clicks are the only way to approve). Blocks until the human clicks **Done, back to the agent**, then prints `GATE`, `NOTE` and `NEXT` lines; exit 0 (130 on Ctrl-C). Prints "Nothing to review yet" and exits 0 when no image exists. Run it in the background; never click its buttons or call its API yourself. |
| `vg upload -p P <file>` | uploads a file, prints its URL (cached ~20 h by file hash) |

## Images (paid, no approval needed)

```bash
vg image -p P --stage look                             # style frames (+ the sheets they ref)
vg image -p P --target asset:Char_Rani_Portrait        # one target
vg image -p P --target storyboard:S01 --target first:S02
vg image -p P --stage refs                             # every missing asset
vg image -p P --stage storyboard                       # every missing storyboard panel
vg image -p P --stage frames                           # every missing first/last frame (real-photo frames are imported, 0 credits)
vg image -p P --target asset:Char_Rani_Portrait --new-take   # deliberate re-roll -> v2
vg image -p P --target asset:Char_Rani_Portrait --dry-run    # print a summary and cost, send nothing
```

- A target that already succeeded with the same prompt and refs is **skipped** (no spend).
- Changing a prompt or a ref makes the next run a new version automatically.
- `--new-take` re-rolls the same prompt as a new version.
- `--model <id>` and `--resolution <value>` override the Shotlist/`.env` defaults for this run only.
- `--allow-untested` lets a model marked `"status": "untested"` in the registry run anyway.
- `vg select -p P --target asset:Char_Rani_Portrait --version 1` picks which take later steps use
  (default: newest).
- Stage runs respect dependencies: a sheet that refs another sheet waits for it. If a dependency
  failed or is still pending after the poll, its dependents are not built that run (`stop ...
  not built this run`) — run the same `--stage`/`--target` again once the dependency is fixed.
- A `--dry-run` no longer fails just because an earlier stage isn't generated yet; a missing
  dependency shows in the refs list as `(pending)`.
- `vg image -p P --stage X` prints `Nothing to generate at stage X` and exits `0` only when that
  stage defines no targets at all (e.g. no shot has a `storyboard.prompt` written yet) — that's
  success, not failure. A target that's already done instead prints `skip ... no spend` per target;
  both cases exit `0`.
- A fast, repeated `FAILED ... 500 Internal Error` on the same prompt is usually kie.ai's content
  filter, not a transport problem — reword the prompt rather than retrying it unchanged (see
  `vg-image/SKILL.md`).

- **Storyboard and frame images are refused until the look is approved** (`REFUSED: storyboard:S01:
  look not approved …`, exit `2`), before anything is paid. After the approval the tool adds the
  style frames as refs to every storyboard/first/last image and to location/product/other assets
  (not character sheets), unless the shot or asset sets `"look_refs": false`. Assets made before the
  approval get a new version the next time `--stage refs` runs. `--dry-run` reports the gate
  instead of refusing.

## Visual review (free, gated by the human)

```bash
vg approve look -p P          # after the human's explicit "approved" to the style frames
vg edit animatic -p P         # the whole reel as stills: 6_Edit/Animatic_<Project>_v<N>.mp4
vg approve visuals -p P       # after the human's explicit "approved" to the board + animatic
```

- `approve look` needs a `look` block with every style frame generated (exit `1` otherwise).
- `edit animatic` uses the edit plan's timing, captions, graphics and transitions, the shots' first
  frames (or panels, or cutaway images) instead of clips, and the planned narration, music and sound
  effects. It records which images and edit plan it showed.
- `approve visuals` refuses (exit `2`) unless the look approval is current, and unless the latest
  animatic shows exactly the current frames, photos and edit plan: re-render after every fix. It
  needs `6_Edit/Edit_Spec.json` and every planned frame (exit `1` otherwise).
- `approve visuals` also needs every AI shot as a clip segment in the edit plan (exit `1` names the
  missing ones) and the latest animatic file on disk. `edit animatic` records nothing if images
  changed while it rendered; run it again.
- What the visuals approval covers: the shot list, every image a video request would send (frames,
  character anchor, `video_refs`), each shot's picture, its words (`dialogue`, `vo`,
  `on_screen_text`), the character sheets of character shots, the edit plan and its images.
- Both follow `VG_APPROVAL_MODE` like `approve video` (a typed code in terminal mode).
- A later change to a style frame, the look text, a frame, a photo in the edit plan, or the edit
  plan's text or timing voids the approval; `vg status` names what changed. Audio-only edit-plan
  fields (`output`, `voice`, `music`, a segment's `audio`/`clip_volume`) do not.

## Identity (Gemini Omni only)

```bash
vg character create -p P --name Rani        # creates voice (if defined) then character
```

**Paid, price unpublished, measured after the call** — tell the human before every `create`,
including a re-create. Needs the character's `portrait` asset generated first. Stores
`characterId` and `audioId` in `project.json`. Re-running with nothing changed does nothing;
changing the character's portrait/body version, description or voice makes the stored identity
stale, and `video`/`approve` then refuse (exit `1`) until it's created again.

## Video (paid, gated)

```bash
vg estimate -p P --stage video                          # show the cost
vg approve video -p P --shots S01 --confirm 105         # only after the human said yes
vg video -p P --shots S01                               # pilot
vg approve video -p P --all --confirm 315               # the rest, after a new yes for the rest
vg video -p P --all
vg approve video -p P --shots S01 --new-take --confirm 63   # a re-roll is a new charge
vg video -p P --shots S01 --new-take
```

- `vg approve video` and `vg video` refuse everything while the look or visuals approval is missing
  or stale (`REFUSED: Visual review gate closed: …`), and check again just before sending.
- `vg video` refuses any shot without a matching, unused approval.
- `--confirm` must equal the total the human just agreed to in chat, for exactly the shots being
  approved in that call (the pilot's own cost when only the pilot is approved, not the grand
  total). If `approve` prints a different total, stop and ask the human again — never retry the
  same command with the number the tool printed.
- **The human types the approval, not the agent.** By default (`VG_APPROVAL_MODE=terminal` in
  `.env`) `approve` prints the shot table, then asks for a random 4-digit code on the real terminal
  (`/dev/tty`). An agent's shell has none, so it gets `REFUSED: Approval must be typed by the human
  in a terminal ...` with the exact command to hand the human — it now starts `cd '<workspace>' &&
  python3 2_Tools/vg/vg.py approve video -p <project> ...` and keeps whatever `--new-take`/
  `--resolution`/`--allow-untested` flags this call used. **Never run it through script, expect, a
  pty, tmux or any terminal you control; only the human types the code** — an agent may open the
  command in the human's own terminal panel for them, but the human types the code.
  `VG_APPROVAL_MODE=chat` (set only in `.env`) is the weaker fallback for a setup with no terminal
  (e.g. a chat app); there the agent may run `approve` itself right after an explicit yes. Budget
  caps and the approval mode come only from `.env` — an environment variable of the same name
  cannot override them, and only the human edits `.env` itself.
- **Each approval pays for exactly one take.** A re-roll of an already-generated clip, or a retry
  of a clip that failed at the provider, is a new charge: show the cost, get a new yes, then
  approve and generate with `--new-take` (both flags, same call shape — a plain retry after a
  `fail` still needs its own new approval even without `--new-take`). `approve` skips a shot
  that's already generated (unless `--new-take`) or has a task in flight, and prints
  `Nothing to approve` if every requested shot falls in one of those states.
- The follow-up `vg video` call uses the same `--shots`/`--all` that was just approved — never
  `--all` after approving only a subset, since the gate refuses the whole batch if any shot in it
  lacks a matching approval. Approving the remainder afterward is a new question with its own new,
  remaining total.
- An approval stores a snapshot of the shot (frames, prompt, mode, duration, identities). If any of
  that changes afterwards, the approval is void and the shot must be approved again.
- `--resolution <value>` and `--allow-untested` work the same way here as on `vg image`; `approve`
  and `video` must be given matching values or the approval snapshot won't match.
- Budget caps from `.env` (`VG_BUDGET_PROJECT`, `VG_MAX_PER_CALL`) and the live balance are checked
  before every paid call. This stops accidental or casual spend, not a deliberately hostile agent —
  the hard wall is a dedicated kie.ai key with its own total credit cap (`vg-setup`).

## Recovery (free)

| Command | Does |
|---|---|
| `vg resume -p P` | polls every pending task and downloads finished results. Use after a timeout or crash. Never re-submit instead. Also prints `CHECK` lines naming both `vg adopt` and `vg release` for any target stuck `submitting`/`unknown`. |
| `vg release -p P --target <kind:id>` | **human only**, after checking the kie.ai dashboard and confirming nothing was created there — unblocks a target stuck in `submitting`/`unknown`/`pending` (including a `pending` row that can never finish). The row becomes `abandoned` and still counts toward the budget at its estimate. A released video target still needs a brand new approval. |
| `vg adopt -p P --target <kind:id> --task-id <id>` | **human only**, after the kie.ai dashboard shows a task *was* created for a `submitting`/`unknown` row — attaches that task id so `vg resume` downloads it instead of anyone paying again. |

## Audio (sound first)

| Command | Does |
|---|---|
| `vg audio voice -p P --text-file 1_Script/Narration.txt --voices Callirrhoe,Leda --style "<direction>"` | one narration take per voice (OpenRouter `google/gemini-3.8-flash-lite-tts`, about $0.003 per 20 s take) into `6_Edit/1_Audio/Narration_Take_<Voice>_v<N>.wav`. The text is read as written: spell numbers and names the way they should sound. The human picks the take by ear |
| `vg audio music -p P --prompt-file <file> --label Quiz_Pop [--takes 1-3]` | music takes (OpenRouter Lyria, about $0.04 per 30 s clip) into `Music_Take_<Label>_v<N>.mp3`. Describe the structure with times: quiet under the voice, a build, half a beat of silence, the drop |
| `vg audio sfx -p P` | four synthesized effects, free: Whoosh (whip cut), Tap (a title or callout appears), Ding (the reveal), Tick (a counter) |
| `vg audio curve -p P --file <audio file> [--step 0.5]` | the track's loudness every step and where its drop is; set `music.at` = reveal time − drop time |

## Edit (local, free)

| Command | Does |
|---|---|
| `vg edit roughcut -p P` | normalises the selected clips to 1080x1920/30fps and joins them in shot order into `6_Edit/Roughcut_<Project>_v<N>.mp4`. A beat with no clip yet shows its storyboard panel if one exists (including an AI shot not yet sent to video); otherwise a dark green placeholder for `real` and dark purple for `mg`. Does not trim — an AI clip goes in at its full generated length. |
| `vg edit animatic -p P` | the reel as stills for the sequence review (see *Visual review*); `6_Edit/Animatic_<Project>_v<N>.mp4` |
| `vg edit final -p P [--draft]` | builds the finished video from `6_Edit/Edit_Spec.json`: trims clips, temporary voice-over (macOS `say`), word-by-word captions, motion graphics (Swift renderer, macOS), ducking, −14 LUFS; writes `99_Output/<output>` plus an `.srt`, or a numbered draft in `6_Edit/` with `--draft`. See `1_Skills/vg-edit/references/edit-spec.md` |

## Exit codes

`0` ok · `1` usage, validation or bad-flag error · `2` only ever a safety refusal, output starts
with `REFUSED:` (gate, budget, balance) · `3` provider error, output starts with `PROVIDER ERROR:`
(kie.ai rejected or failed the task) · `130` interrupted (Ctrl-C, closed terminal, killed process) —
run `vg status` and `vg resume`; the human checks the kie.ai dashboard before any `release`/`adopt`.
