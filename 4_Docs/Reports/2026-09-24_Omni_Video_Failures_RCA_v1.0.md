# RCA — Gemini Omni video failures on kie.ai

**Date:** 2026-09-24 · **Project:** property-reel sample (5 AI shots) · **Status:** cause outside our
control (provider side, most likely); workaround proposed

## Summary

10 video tasks on `google/gemini-omni-flash-1-1` were submitted today. **1 succeeded, 9 failed**,
every failure with `500 Internal Error, Please try again later.` after 143–805 s of processing.
**Failures were charged 0 credits** (verified in `recordInfo.creditsConsumed` and the live balance).
The harness behaved as designed: no automatic retries, each retry needed a fresh human approval,
and the ledger matches kie.ai to the credit.

## Timeline and data

| Attempt | Shot | Mode | Key inputs | Run time | Result |
|---|---|---|---|---|---|
| 14:13 | S01 | character | new identity, 2K PNG ref, 8 s | 497 s | 500 |
| 14:13 | S02 | frames | first + last 2K PNG, 4 s | 206 s | 500 |
| 14:34 | **S04** | frames | first + last JPEG 1080 px, 4 s | 136 s | **success, 63 credits** |
| 14:34 | S05 | character | new identity, JPEG ref, 4 s | 442 s | 500 |
| 14:52 | S05 | character | identity re-created from JPEG | 570 s | 500 |
| 14:52 | S02 | frames | first + last JPEG | 334 s | 500 |
| 15:37 | S01 | character | JPEG identity, 8 s | 654 s | 500 |
| 15:37 | S08 | character | JPEG identity, 10 s | 805 s | 500 |
| 16:2x | S05 | character | + `seed: 123456` (test A) | ~340 s | 500 |
| 16:2x | S02 | frames | first frame only (test B) | ~145 s | 500 |

Reference: the same account's two character-mode clips on **2026-09-22 both succeeded** (4 s,
1080p, `seed: 123456`, identity created that day), one of them after 501 s.

## Hypotheses tested

| Hypothesis | Test | Verdict |
|---|---|---|
| Wrong field names or types | payloads compared with the live docs field by field; mutual exclusion respected | **ruled out** |
| Input images too large for the slow upload host (2K PNG, 5–8 MB) | sent 0.25–0.6 MB JPEGs; S02 and S05 still failed; a Sep 22 success used a PNG | **ruled out** as the cause (the lighter inputs are kept anyway) |
| Long processing = timeout | a Sep 22 success took 501 s | **ruled out** |
| Clip length | S05 failed at 4 s, the length of every success | **ruled out** |
| Missing `seed` (all Sep 22 character successes had one) | test A: S05 with `seed: 123456` | **ruled out** |
| First and last frames too different for the model | test B: S02 with the first frame only | **ruled out** |
| Today's character identity is broken | S02 uses no identity and fails too | **cannot explain** the frames-mode failures |
| Provider-side instability of Omni on kie.ai / Google today | 1/10 today vs 2/2 two days ago, across every mode and input type; same generic message; public reports of Omni Flash "internal error" regardless of prompt | **most likely** |

Content moderation is not fully excluded (S02 shows a large store; S01/S05/S08 show a realistic
person), but S04 is the only success and the failures span unrelated content, so it is a weaker
explanation than instability.

## What the harness got right

- No credits lost: 9 failures, 0 credits charged, ledger = kie.ai balance (724.23 = 907.23 − 120 images − 63 for S04).
- No silent retries: every retry needed the human's typed approval code.
- Clear failure signal: exit code 3 with the provider message; failed clips flagged in `vg status`.

## Changes made during the investigation

- Video inputs and character portraits are sent as 1080-px JPEGs (`video_input()`), not 2K PNGs.
- Optional `seed` per shot (`shots[].seed` or `video_defaults.seed`), covered by the approval.
- Troubleshooting note in `1_Skills/vg-video/references/troubleshooting.md`.

## Options

1. **Wait and retry Omni later** (e.g. tomorrow). No code change. Keeps character + voice lock.
   Each retry needs an approval code; failures stay free.
2. **Add Veo 3.1 Lite** as a second video model (kie.ai legacy endpoint `/api/v1/veo/generate`,
   `model: "veo3_lite"`, `generationType: FIRST_AND_LAST_FRAMES_2_VIDEO`, `aspect_ratio: 9:16`,
   4/6/8 s, audio included). Roughly **30–35 credits per clip** (about half of Omni). No character or
   voice lock: talking shots run in frames mode from the storyboard panel, so the face follows the
   panel but the voice can vary between shots. Needs a small provider module and one paid pilot.
3. **Finish the edit now** with S04 as the only moving AI shot and the storyboard panels as slow-zoom
   stills for the rest (free), then swap clips in when video works.

## Evidence

Task records: `vg status` and `project.json` of the sample project; raw kie.ai records via
`GET /api/v1/jobs/recordInfo` for each task id (fields `param`, `costTime`, `failCode`,
`creditsConsumed`).

## Addendum 2026-09-25

Retried on Omni the next day: S02 (frames) **succeeded** (63 credits); S01, S05, S08 (character
mode, identity + voice) **failed again** with the same 500. Totals over both days:

| Mode | Attempts | Successes |
|---|---|---|
| character (identity + voice created 2026-09-24) | 9 | **0** |
| frames (first frame, optional last frame) | 5 | 2 |

Character mode with the identities created on 2026-09-24 has never worked, while the same account's
Sep 22 identity worked twice. The narrowed conclusion: **the failures concentrate in Omni's
character/identity path** (either these identities or the character service), with frames mode
unreliable but usable. Workaround applied: the talking shots run in frames mode from their
storyboard panels (face held by the panel, voice not locked). A later test worth running when
cheap: one character-mode clip with a freshly created identity, and one with the Sep 22 identity.
