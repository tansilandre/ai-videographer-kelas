# kie.ai video models — cost and capability survey

**Date:** 2026-09-24 · **Why:** Gemini Omni Flash failed 9/10 tasks today (see
`2026-09-24_Omni_Video_Failures_RCA_v1.0.md`) and the owner asked for the cheapest working models.
**Method:** kie.ai's live pricing API (269 video price rows, 39 model families) plus the API docs of
each family, read by six research agents; key prices re-checked against the raw price list. Nothing
was generated and nothing was spent. 1 credit = $0.005.

## Our four open shots

S01 selfie in a car, presenter speaks an 8 s Indonesian line · S08 presenter speaks ~8–10 s to
camera · S05 presenter walks and glances back, no speech, 4 s · S02 aerial flyover from a first
frame, 4 s. Baseline on Omni Flash: 105 + 126 + 63 + 63 = **357 credits**.

## Cheapest options that fit (credits per clip, 9:16)

| Model (kie `model`) | Speech | First frame / last | Price rule | 4 s | 8 s | 10 s | Notes |
|---|---|---|---|---|---|---|---|
| Seedance 1.5 Pro, no audio (`bytedance/seedance-1.5-pro`, `generate_audio: false`) | none | yes / no | 1.75/s 480p · 3.5/s 720p | 7 · 14 | 14 · 28 | — | cheapest b-roll; send `aspect_ratio: "9:16"` (default is 1:1) |
| Seedance 1.5 Pro, with audio | from prompt; kie.ai page lists Indonesian | yes / no | 3.5/s 480p · 7/s 720p | 14 · 28 | 28 · 56 | 35 · 70 | only model whose Indonesian support kie.ai states |
| Grok Imagine 1.5 preview (`grok-imagine-video-1-5-preview`) | from prompt; language unknown | yes / no | 2.4/s 480p · 4.5/s 720p | 9.6 · 18 | 19.2 · 36 | 24 · 45 | cheapest talking option on paper; preview model |
| Veo 3.1 Lite (legacy `/api/v1/veo/generate`, `model: "veo3_lite"`) | from prompt | yes / yes | 30 per clip 720p · 35 per clip 1080p | 30 | 30 | max 8 s | flat price per clip up to 8 s; 1080p costs 35 |
| MeiGen InfiniteTalk (`infinitalk/from-audio`) + ElevenLabs TTS | lip-sync to supplied audio | image / no | 3/s 480p · 12/s 720p; TTS 12 per 1000 chars (multilingual v2) | 12 + ~1 | 24 + ~1 | 30 + ~1 | same voice in every shot (voice lock via TTS); 720p is 4x the price |
| Hailuo 02 Standard | none | yes / yes | 12 per 6 s 512p | 12 | — | 20 | cheap silent b-roll with a last frame; 512p |
| Gemini Omni Flash (current) | from prompt; character + voice lock | yes / yes | 63 per 4 s … 126 per 10 s | 63 | 105 | 126 | failing today |

Everything else surveyed was dearer or not a fit (Kling 2.x/3.0, Wan 2.5–3.0, Runway, PixVerse,
HappyHorse, OmniHuman, Seedance 2/2.5, Veo Fast/Quality). Full per-variant data (61 variants, exact
field names, doc URLs, risks) was produced by the survey run; key points are captured above.

## Plans for the four shots

| Plan | S01 | S08 | S05 | S02 | Total | Trade-off |
|---|---|---|---|---|---|---|
| A. Veo 3.1 Lite for talking + Seedance 1.5 (no audio, 720p) for the rest | 30 | 30 (line trimmed to fit 8 s) | 14 | 14 | **88** | 720p, native speech, Google quality; needs a small provider module for the legacy Veo endpoint |
| B. InfiniteTalk 480p + ElevenLabs voice + Seedance 1.5 (720p) | ~25 | ~31 | 14 | 14 | **~84** | same voice in both talking shots; talking heads are 480p; little body motion |
| C. All Seedance 1.5 Pro 720p | 56 | 70 | 14 | 14 | **154** | one model, stated Indonesian support; no voice lock |
| D. All Seedance 1.5 Pro 480p | 28 | 35 | 7 | 7 | **77** | cheapest native-speech plan; 480p looks soft on phones |
| Omni Flash (baseline) | 105 | 126 | 63 | 63 | 357 | character + voice lock, but failing today |

Side benefit of ElevenLabs (any plan): the temporary macOS voice-over for S03 and S05 can be replaced
by a real Indonesian voice for about 1 credit per line.

## Integration cost in the harness

- Seedance 1.5 Pro, Grok, InfiniteTalk, Hailuo, ElevenLabs: same `jobs/createTask` API as today →
  one registry JSON each, marked `untested` until a paid pilot.
- Veo 3.1 Lite: the tier is only selectable on the legacy endpoint → one small provider module.
- Every new model: one paid pilot to confirm field names and the charged price before wider use.
