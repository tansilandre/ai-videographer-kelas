# Gemini Omni Flash 1.1 — verified reference

`google/gemini-omni-flash-1-1` on kie.ai, called through `POST /api/v1/jobs/createTask` and polled
with `GET /api/v1/jobs/recordInfo?taskId=`. `vg` builds and validates every payload from the model's
registry file (`2_Tools/vg/models/gemini-omni-flash-1-1.json`) — this file explains the facts that
registry encodes, so a refusal makes sense instead of looking arbitrary.

Identity and voice go through two different, synchronous endpoints, not `createTask`:
`POST /api/v1/omni/character/create` (`characterId`) and `POST /api/v1/omni/audio/create`
(`audioId`). Both return their id inline, with no `taskId` and no polling. `vg character create`
wraps both — voice first if the character definition includes one, then the character.

## Video input parameters

| Field | Type | Required | Notes |
|---|---|---|---|
| `prompt` | string | yes | max 20000 chars |
| `duration` | **string** | yes | `"4"`, `"6"`, `"8"`, `"10"` — an integer here is the classic `422` |
| `image_urls` | array[string] | no | ≤7, ≤20MB each, public URLs — a **soft** reference, not a hard frame |
| `first_frame_url` | string | no | 1 URL — a **hard** anchor, exclusive with everything below |
| `last_frame_url` | string | no | requires `first_frame_url` |
| `audio_ids` | array[string] | no | ≤3, must be `audioId`s returned by `/omni/audio/create` — **not** a preset name |
| `video_list` | array[object] | no | ≤1 item; when present, `duration` is **ignored** — the model chooses |
| `character_ids` | array[string] | no | ≤3, a flat cap the registry enforces regardless of `video_list`; must be `characterId`s from `/omni/character/create` |
| `aspect_ratio` | string | no | `"9:16"` for this harness |
| `resolution` | string | no | `"360p"`, `"720p"`, `"1080p"`, `"4k"` — default `"720p"`; use `"1080p"` for delivery |
| `seed` | **integer** | no | `0`–`2147483647` — never a string |

Only `model`, `input`, `callBackUrl` are valid top-level keys. `vg` polls rather than using
`callBackUrl`.

## Two separate caps: per-field limits, then the 7-unit media quota

`character_ids` is capped at **3** and `image_urls` at **7** on their own, before anything else is
summed — this is a flat field limit, not conditional on whether `video_list` is present. On top of
that, the registry sums a weighted quota:

```
(image_urls entries) + (video_list entries × 2) + (character_ids entries) ≤ 7
```

`audio_ids` cost nothing in the quota. A character built from a **portrait + body** pair (two
images at character-create time) costs **2** quota slots wherever its id is used in a shot, not 1
— `vg` adds that extra unit itself when it builds the payload.

| Scenario | Field-limit check | Quota arithmetic | Result |
|---|---|---|---|
| 1 soft image + 1 character id | ok | 1 + 1 = 2 | fine, room for more |
| 7 images, no character | ok | 7 | fine, at the cap |
| 7 images + 1 character id | ok | 8 | rejected by the quota |
| 4 character ids, no other media | **rejected** (>3) | not reached | the flat `character_ids` cap fires first |
| video_list item + 3 character ids (portrait only) | ok | 2 + 3 = 5 | fine |

`vg` checks both before sending; a rejection here is the tool catching it, not kie.ai.

## Mode exclusivity — why the three `Shotlist.json` modes exist

Providing `first_frame_url` makes `image_urls`, `audio_ids`, `video_list`, and `character_ids`
all unusable on that same request. This is a hard provider rule, not a harness choice.

| If the shot sends… | it may not also send… |
|---|---|
| `first_frame_url` | `image_urls`, `audio_ids`, `video_list`, `character_ids` |
| `image_urls` | `first_frame_url` (everything else composes) |
| `audio_ids` / `video_list` / `character_ids` | `first_frame_url` |
| `last_frame_url` | requires `first_frame_url` present |

Three identity strategies fall out of this, ranked by anchor strength:

| Strategy | Field | Anchor strength | Composes with voice? | Composes with `character_ids`? |
|---|---|---|---|---|
| Hard first frame | `first_frame_url` | strongest, pixel-level, single shot | no | no |
| Reusable character | `character_ids` | strong, reusable across shots and future projects | yes | — |
| Soft reference | `image_urls` | weakest — guidance only | yes | yes |

This is exactly `Shotlist.json`'s `frames` / `character` / `text` split (schema, §Modes): `frames`
takes the hard anchor and gives up voice and reuse; `character` gives up the hard anchor to keep a
reusable identity and a reusable voice, and passes the storyboard panel as a soft `image_urls`
reference instead; `text` has neither.

## Creating a character and a voice

`POST /api/v1/omni/character/create` — top-level body fields (not nested in `input`):

| Field | Type | Required | Notes |
|---|---|---|---|
| `descriptions` | string | yes | appearance, identity, style, clothing, personality |
| `image_urls` | array[string] | yes | 1–2: index 0 = portrait, index 1 = body (optional) |
| `audio_ids` | array[string] | no | binds a voice to the character |
| `character_name` | string | no | label |

Returns `data.characterId`.

`POST /api/v1/omni/audio/create`:

| Field | Type | Required | Notes |
|---|---|---|---|
| `audio_id` | string | yes | one of the 30 preset voice names below |
| `name` | string | yes | ≤210 chars |
| `voice_description` | string | no | ≤20000 chars |
| `example_dialogue` | string | no | ≤120 chars |

Returns `data.audioId`. Note the naming trap: `audio_id` (singular, input) is a preset name;
`audio_ids` (plural, video input) is an array of *returned* `audioId`s. Passing a preset name where
a video payload expects `audio_ids` is a `422`.

**30 preset voices:** `achernar`, `achird`, `algenib`, `algieba`, `alnilam`, `aoede`, `autonoe`,
`callirrhoe`, `charon`, `despina`, `enceladus`, `erinome`, `fenrir`, `gacrux`, `iapetus`, `kore`,
`laomedeia`, `leda`, `orus`, `puck`, `pulcherrima`, `rasalgethi`, `sadachbia`, `sadaltager`,
`schedar`, `sulafat`, `umbriel`, `vindemiatrix`, `zephyr`, `zubenelgenubi`. `Shotlist.json`'s
`characters[].voice.preset` field takes one of these.

## Pricing (verified, 2026-09-24; 1 credit = $0.005)

Same price at 360p / 720p / 1080p — resolution is not a cost lever, only a quality choice:

| Duration | Credits | 4K credits |
|---|---|---|
| 4s | 63 | 147 |
| 6s | 84 | 168 |
| 8s | 105 | 189 |
| 10s | 126 | 210 |

Character and voice creation cost is **not published** — `vg` records whatever the ledger shows
after the call, and an estimate for a project with unbuilt characters will be incomplete for that
part.

## Operational facts

- Balance: `GET /api/v1/chat/credit` — `vg credits`.
- Rate limit: 20 new requests / 10 seconds.
- Result URLs expire — download immediately. `vg` does this as part of `vg video` / `vg resume`.
- Uploaded input files expire (~24h observed) — re-upload per session; don't reuse a URL from a
  previous day's `vg upload`.
- A dedicated kie.ai API key with an hourly/daily/total credit cap, set at kie.ai/api-key, is the
  outer safety net beyond everything `vg` enforces in code (`vg-setup`).
