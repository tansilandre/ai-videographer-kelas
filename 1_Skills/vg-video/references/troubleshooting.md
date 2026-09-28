# Troubleshooting — vg video

## Exit codes

| Code | Meaning | What to do |
|---|---|---|
| `0` | ok | — |
| `1` | usage, validation or bad-flag error | fix `Shotlist.json` / the command, re-run `vg validate` |
| `2` | only ever a safety refusal, output starts with `REFUSED:` (gate, budget cap, live balance) | **report it to the human verbatim — do not work around it** |
| `3` | provider error, output starts with `PROVIDER ERROR:` (kie.ai rejected or failed the task) | read the failure message; usually a `422`/`402` below |
| `130` | interrupted (Ctrl-C, closed terminal, killed process) | `vg status -p <project>` and `vg resume -p <project>`; the human checks the kie.ai dashboard before any `release`/`adopt` |

## 422 — payload rejected

| Symptom | Cause | Fix |
|---|---|---|
| `422` on a payload that looks right | `duration` sent as an integer (`4`) instead of a string (`"4"`) | send the string form |
| `422` | `last_frame_url` present without `first_frame_url` | supply both or neither |
| `422` or a generic parameter rejection | quota sum over 7 (`image_urls` + `video_list`×2 + `character_ids` > 7) | reduce inputs; `audio_ids` are free, images/videos/characters are not |
| `422`, or a silently wrong result | `first_frame_url` combined with `image_urls` / `audio_ids` / `video_list` / `character_ids` | pick one identity strategy per shot — see `gemini-omni-flash.md` mode table |
| `422` or missing audio | `audio_ids` holds a preset name (`"sulafat"`) instead of a returned `audioId` | call `/omni/audio/create` first, use the returned id |
| `422` or wrong/absent identity | `character_ids` holds a URL or a name instead of a returned `characterId` | call `/omni/character/create` first |
| field silently dropped, unexpected behavior | extra top-level keys beyond `model`, `input`, `callBackUrl` | remove them |
| `422` | `prompt` over 20000 chars | shorten — this is rare; hitting it usually means the video prompt re-describes the frame (see `vg-video-prompt`) |
| `422` | an input image over 20MB | compress before upload |
| `422` | `video_list` clip over 100MB, over 30s, or a `start`/`ends` span over 10s | trim the source clip |
| `422` | more than 3 `character_ids` | the registry caps `character_ids` at 3 regardless of `video_list` — cap at 3 |

`vg validate` and the model registry catch most of these before a request is ever sent — a `422`
that reaches kie.ai despite `validate` passing is worth reporting as a registry gap.

## 402 — insufficient credits

- Check `vg credits` before a batch — the live balance is checked before every paid call, but a
  batch of several shots can still run out partway through.
- A `VG_BUDGET_PROJECT` or `VG_MAX_PER_CALL` cap from `.env` refuses a call with exit code `2`
  *before* it ever reaches kie.ai, even if the kie.ai balance itself would cover it — that's the
  cap doing its job, not a bug.
- Top up the balance or ask the human whether to proceed with a smaller batch; never split a call
  into smaller pieces specifically to dodge a cap.

## A failed clip has already used up its approval

A `fail` row (the provider accepted the task, then it failed — e.g. content policy, a transient
model error) consumed its approval the moment it was submitted, exactly like a successful clip
does. Retrying is not free of the gate just because nothing downloadable came out of it: get the
human's new yes, then `vg approve video -p <project> --shots <id> --confirm <n>` again before
running `vg video` for that shot a second time. A row stuck `submitting`/`unknown`, or a `pending`
row that can never finish, is different — that's not a `fail`, it's an unclear outcome, and the
human resolves it on the kie.ai dashboard first: task exists there → `vg adopt -p <project>
--target clip:<id> --task-id <id>` so `vg resume` downloads it; nothing was created → `vg release
-p <project> --target clip:<id>` (the row becomes `abandoned`, still counted toward the budget at
its estimate). Either way a video target needs a brand new approval afterward.

## Truncated speech

**Signature:** the clip reports `success`, has a full-length audio stream, but the sentence is cut
off mid-word. This is a content problem, not a transport problem — confirm that first:

```bash
ffprobe -v error -show_entries stream=codec_type,codec_name,width,height,sample_rate,channels \
  -show_entries format=duration -of default=noprint_wrappers=1 <clip>
```

If audio duration equals video duration equals the requested duration, the container is fine and
the loss is in the model's output, not the file. Then measure whether speech actually completes:

```bash
ffmpeg -v error -i <clip> -ac 1 -ar 16000 -f s16le - | python3 -c "
import sys, array, math
a = array.array('h'); a.frombytes(sys.stdin.buffer.read())
sr, win = 16000, int(0.05*sr)
rms = []
for i in range(0, len(a)-win, win):
    ch = a[i:i+win]
    rms.append(math.sqrt(sum(x*x for x in ch)/len(ch)))
peak = max(rms) or 1
th = peak * 0.15
dur = len(a)/sr
last = max((j for j,v in enumerate(rms) if v >= th), default=-1)
end = last*0.05 + 0.05
print(f'duration      {dur:.2f}s')
print(f'speech ends   {end:.2f}s')
print(f'TAIL SILENCE  {dur-end:.2f}s')
print('VERDICT:', 'COMPLETES' if dur-end >= 0.25 else 'TRUNCATED')
"
```

| Tail silence | Meaning |
|---|---|
| ≥ 0.25s | completed — safe |
| 0.10–0.25s | completed but no headroom — tighten the line before reusing it elsewhere |
| ≈ 0s | truncated — speech is still at full level at the cut |

**Fix:** shorten the `dialogue` field or move to the next allowed `duration` up — recompute with
the fit rule in `vg-video-prompt/SKILL.md` (`chars ≤ (duration − 0.7) × 10.5`). Never fix this by
asking the model to "speak faster" or by time-stretching the audio afterward — a rushed or
stretched read is audible and undermines the format's whole point. A corrected, longer shot costs
*more* credits, not less — say so plainly rather than implying there's a free fix.

## Identity drift / fused fingers / warped hands

**Fix the frame, not the prompt.** These are almost always inherited from a weak reference or
first frame, not something the video prompt caused:

1. Look at the actual frame that was sent (`4_Frames/Frame_<ShotId>_First_v<N>.png` or the
   storyboard panel) — is the defect already visible there? If yes, the fix is a new frame
   (`vg-storyboard`'s guidance, run with `vg image -p <project> --target <target> --new-take`), not
   a different `video_prompt`.
2. If the frame looks fine but the *video* drifts, simplify the motion (one clear beat, the ACTION layer of
   `vg-video-prompt/references/prompt-formula.md`) and shorten the clip — drift compounds with
   duration.
3. Positive locks and short bans (`vg-video-prompt/references/avoid-list.md`) are a supporting guard, not a
   substitute for a clean frame — Gemini Omni has no real negative-prompt field, so it will not
   reliably rescue a bad reference.
4. Never spend a `--new-take` re-roll without the human's awareness — it's a new video charge and
   always needs its own new approval: each approval pays for exactly one take, so even an unchanged
   snapshot's earlier approval is already used up. Show the cost, get a new yes, then
   `vg approve video -p <project> --shots <id> --new-take --confirm <n>` and
   `vg video -p <project> --shots <id> --new-take`.

## Naming traps worth knowing (even though this harness only uses one model id)

- The video model's id string is `google/gemini-omni-flash-1-1` (hyphens, `google/` prefix) — not
  the operation-id spelling `gemini-omni-1.1-flash` (dots) that appears in some docs.
- A separate model, `gemini-omni-video`, exists on the same jobs endpoint with **no** `google/`
  prefix and does not document `first_frame_url`/`last_frame_url`. It is a different model — never
  add or drop the prefix trying to "fix" a typo between the two.

## `500 Internal Error, Please try again later` after several minutes

Seen on 2026-09-24: every Omni task whose inputs were full-size 2K PNGs (5–8 MB) ran 200–500 s and
then failed with this 500 (charged 0). The same frames sent as ~0.3–0.6 MB JPEGs succeeded in about
136 s. kie.ai's workers fetch inputs from a slow temporary file host and time out. The tool now
sends every video input and every character portrait as a 1080-px JPEG (`video_input()` in
`generate.py`); identities created before that fix are treated as stale and must be re-created with
`vg character create` (free so far: 0 credits measured). If this error still appears, it is more
likely a real outage: wait, then retry with a new approval (failed clips use up their approval).

## Fast `500` (under ~90 s) on a shot with a person = content filter

Seen on 2026-09-25 (Omni, frames mode): two shots failed within a minute while others succeeded.
Rewording fixed both on the next try:

| Failed wording / image | What worked |
|---|---|
| selfie in the **driver's seat**, holding the phone ("in the car") | "recorded in a **parked car with the engine off**, the car is standing still"; add `driving, moving car` to Avoid |
| woman **seen from behind, walking away**, "tracking from behind" | "friendly lifestyle vlog **filmed by a friend walking alongside her**; she turns toward the camera and smiles" |

Rule of thumb: remove anything that reads as unsafe behaviour (phone use while driving) or as
following/surveilling a person. The image model (gpt-image-2) rejects the same patterns.

## Character mode failing, frames mode working (Omni, 2026-09-24/25)

Character mode (identity + voice) failed 9/9 with identities created on 2026-09-24, while frames
mode from the storyboard panel succeeded. If character mode keeps failing, switch talking shots to
`frames` mode: the face is held by the panel, the voice is not locked.
