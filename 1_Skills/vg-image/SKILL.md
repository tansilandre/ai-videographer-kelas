---
name: vg-image
description: Use when running `vg image` to generate reference sheets, storyboard panels, or frames, or when an image generation call needs to be checked, resumed, or re-rolled — trigger phrases like "generate the images", "run the storyboard stage", "resume the generation", "re-roll this image", "why did this image call fail".
---

# vg-image

`vg-reference-sheets` and `vg-storyboard` both write prompts (using `vg-image-prompt`) and then
call `vg image` to actually generate them. This skill is the mechanics of that call: how to run
it safely, what the exit codes mean, and the verified facts about gpt-image-2 on kie.ai that keep
a call from being rejected. It sits before `vg-video-prompt`/`vg-video`, which spend on video
only after images are approved.

There is no `vg` on PATH — every example below runs as `python3 2_Tools/vg/vg.py <command>`; `vg
<command>` is shorthand for that full path, used from here on.

## Dry-run first when unsure

Every paid command takes `--dry-run`. It prints a summary — model, params, input files, a
shortened prompt, and the credit cost, not the exact request payload — and calls nothing:

```bash
python3 2_Tools/vg/vg.py image -p P --target asset:Char_Rani_Portrait --dry-run
```

Use it whenever a new prompt, a new ref chain, or an unfamiliar aspect/resolution combination is
involved — it's free and it catches a bad payload before it's submitted.

## Stage vs target

```bash
vg image -p P --target asset:Char_Rani_Portrait          # one thing
vg image -p P --target storyboard:S01 --target first:S02 # several named things
vg image -p P --stage refs                                # every missing asset
vg image -p P --stage storyboard                           # every missing storyboard panel
vg image -p P --stage frames                                # every missing first/last frame
```

Use `--stage` for a batch once prompts are settled; use `--target` to regenerate or check one
thing without touching the rest. Stage runs respect dependencies (a sheet that refs another sheet
waits for it) — hand-running targets out of order does not. If a dependency failed or is still
pending after this run's poll, its dependents are simply not built this run (`stop N dependent
image(s) not built this run: ...`) — nothing is lost, just run the same `--stage`/`--target` again
once the dependency is fixed. `--model <id>` and `--resolution <value>` override the Shotlist/
`.env` defaults for one run; `--allow-untested` permits a model the registry marks
`"status": "untested"`. `--dry-run` no longer needs earlier stages generated first — a missing
dependency just shows in the refs list as `(pending)`. A `--stage` run prints `Nothing to
generate at stage <stage>` and exits `0` only when that stage defines no targets at all (e.g. no
shot has a `storyboard.prompt` written yet) — that is success, not a bug. A target that's already
done instead prints `skip ... already done (vN), no spend` per target; that also exits `0`.

## Idempotency — why re-running is safe

- A target that already succeeded with the same prompt and the same refs is **skipped**, no
  spend. Re-running `--stage refs` after adding one new asset only generates the new one.
- Changing a prompt or a ref automatically makes the next run produce a new version.
- A deliberate re-roll of the *same* prompt needs `--new-take` — this is the only way to spend
  credits on an unchanged prompt on purpose.
- Pick which version later stages use:
  ```bash
  vg select -p P --target asset:Char_Rani_Portrait --version 2
  ```
  Default is newest; use this to fall back to an earlier take.

## Resuming instead of resubmitting

```bash
vg resume -p P
```

Use this after any timeout, crash, or closed laptop. It polls every pending task and downloads
finished results. Never re-run the same `image`/`video` command to "retry" a call that might
still be in flight — that risks a duplicate spend before the idempotency key can catch it.
`resume` is always free and always safe.

## Always look at the output before moving on

Downloading a file is not the same as checking it. Open every generated image — portrait,
turnaround panel, storyboard frame — before treating that target as done. `vg-reference-sheets`
and `vg-storyboard` both have QC checklists; run them here, not after the whole stage finishes.

## Exit codes

| Code | Meaning | What to do |
|---|---|---|
| `0` | ok | continue |
| `1` | usage, validation or bad-flag error | fix `Shotlist.json` (bad field, bad ref, bad enum value) and re-run `vg validate` |
| `2` | only ever a safety refusal (output starts with `REFUSED:`) | check the reason — gate not approved, budget cap, low balance (`vg credits`) — this is the tool protecting spend, not a bug |
| `3` | provider error (output starts with `PROVIDER ERROR:`) | kie.ai rejected or failed the task — read the message before retrying; don't resubmit an identical prompt that got rejected for content policy |
| `130` | interrupted (Ctrl-C, closed terminal, killed process) | `vg status -p P` and `vg resume -p P`; the human checks the kie.ai dashboard before any `release`/`adopt` |

## Verified gpt-image-2 facts

| Fact | Value |
|---|---|
| Text-to-image model id | `gpt-image-2-text-to-image` |
| Image-to-image model id | `gpt-image-2-image-to-image` |
| Image-input field (i2i only) | `input_urls`, an array, max **16** |
| Resolutions | `1K` (6 credits) · `2K` (10 credits) · `4K` (16 credits) |
| 2K unsupported aspect ratios | `5:4`, `4:5`, `3:1`, `1:3`, `9:21` |
| 4K unsupported aspect ratios | `3:1`, `1:3`, `9:21`, and `1:1` cannot go to 4K |
| `auto` aspect ratio | only ever yields 1K |
| Seed | none — there is no reproducibility control; the version history is the only record |
| Images per task | one |
| Fields that don't exist | `size`, `quality`, `output_format`, `background` (above 1K), `seed` |

These are the two model ids `vg` will actually call — never substitute a different image family's
field names (`image_urls`, `input_image`, etc. belong to other providers, not gpt-image-2).

## Common mistakes

| Mistake | Fix |
|---|---|
| Re-running a command to "make sure" it went through | run `vg status -p P` or `vg resume -p P` instead |
| Treating exit code `2` as a bug | it's a safety refusal — read the message, it names the cap or gate |
| Assuming a skipped target means something is wrong | skipped = idempotent success, nothing changed |
| Requesting 4K at `1:1`, or 2K at `5:4`/`4:5` | pick a supported ratio, or drop to a supported resolution |
| Moving to the next stage without opening the image | always look first |
| Retrying the same prompt after `FAILED ... 500 Internal Error` twice | a fast, repeated 500 on one prompt is usually kie.ai's content filter (failed tasks cost 0). Reword the prompt: on one project, "camera following behind her ... walking away" failed twice; "strolling, three-quarter back view, glancing over her shoulder" worked first time |
