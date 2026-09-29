# Shotlist.json — the plan file

`<project>/1_Script/Shotlist.json` is the single plan for one video. The agent writes it; the `vg`
tool reads it to build every image and video request, and `vg board` renders it. Run
`vg validate -p <project>` after every edit.

Everything the tool generates is addressed by a **target**:

| Target | What it is | Saved as |
|---|---|---|
| `look:<StyleFrameId>` | a style frame from `look.style_frames[]` | `2_References/<StyleFrameId>_v<N>.png` |
| `asset:<AssetId>` | a reference sheet from `assets[]` | `2_References/<AssetId>_v<N>.png` |
| `storyboard:<ShotId>` | the storyboard panel of a shot | `3_Storyboard/SB_<ShotId>_v<N>.png` |
| `first:<ShotId>` | first frame of a shot | `4_Frames/Frame_<ShotId>_First_v<N>.png` |
| `last:<ShotId>` | last frame of a shot | `4_Frames/Frame_<ShotId>_Last_v<N>.png` |
| `clip:<ShotId>` | the video clip | `5_Clips/Clip_<ShotId>_v<N>.mp4` |

## Full example

```json
{
  "project": "Harbor_Homes_Tour",
  "title": "Harbor Homes, Under a Million?",
  "client": "Harbor Homes",
  "format": { "aspect_ratio": "9:16", "language": "en", "length_s": 40 },
  "models": { "image": "gpt-image-2", "video": "gemini-omni-flash-1-1" },
  "image_defaults": { "resolution": "2K" },
  "video_defaults": { "resolution": "1080p" },
  "style_lock": {
    "image": "shot on iPhone, natural daylight, realistic skin texture, subtle sensor grain, warm grade, vertical 9:16",
    "video": "shot on iPhone, handheld, natural light, realistic skin texture, warm grade, vertical 9:16"
  },
  "look": {
    "world": "Harbor Homes, a coastal suburb, one sunny weekday afternoon",
    "light": "warm late-afternoon sun from camera left, soft long shadows",
    "grade": "natural warm, medium contrast, no teal-orange, no dusk or night looks",
    "graphics": "one bold sans font, one accent #FF5A1F, white captions in the lower third, never over a face",
    "style_frames": [
      { "id": "Look_A", "prompt": "Use: style frame, the look of the whole reel. Scene: …", "refs": ["Char_Rani_Portrait"] },
      { "id": "Look_B", "prompt": "Use: style frame, the neighbourhood at the same hour, no people. Scene: …" }
    ]
  },
  "rules": [
    "Houses and units are real: real footage, or the client's real photos animated with a camera move only (client agreed). AI never invents the building for sale.",
    "Any not-yet-built infrastructure carries the on-screen label PLANNED — ILLUSTRATION ONLY."
  ],
  "characters": [
    {
      "name": "Rani",
      "description": "Young woman, 27, warm medium skin, dark brown hair in a low messy bun ...",
      "portrait": "Char_Rani_Portrait",
      "voice": {
        "preset": "sulafat",
        "name": "Rani - English UGC narrator",
        "description": "Warm, clear female voice, late twenties, conversational ...",
        "example": "Guess. How much do you think this house costs?"
      }
    }
  ],
  "assets": [
    {
      "id": "Char_Rani_Portrait",
      "kind": "character",
      "prompt": "Character reference portrait ...",
      "refs": [],
      "aspect_ratio": "3:4"
    },
    {
      "id": "Char_Rani_Turnaround",
      "kind": "character",
      "prompt": "One image laid out as a clean 2x2 grid ...",
      "refs": ["Char_Rani_Portrait"],
      "aspect_ratio": "1:1"
    },
    {
      "id": "Loc_Car_Interior",
      "kind": "location",
      "prompt": "Empty driver's seat of a modern compact SUV ...",
      "refs": []
    }
  ],
  "shots": [
    {
      "id": "S01",
      "time": "0-3s",
      "beat": "HOOK",
      "source": "ai",
      "summary": "Rani selfie-talks in the car, then glances at the window.",
      "vo": "Is this Harbor Homes unit still under a million? Let's go see it.",
      "on_screen_text": "",
      "mode": "character",
      "duration": "auto",
      "characters": ["Rani"],
      "dialogue": "Is this Harbor Homes unit still under a million? Let's go see it.",
      "storyboard": {
        "prompt": "UGC selfie still, Rani in the driver's seat ...",
        "refs": ["Char_Rani_Portrait", "Loc_Car_Interior"]
      },
      "first_frame": { "from": "storyboard" },
      "last_frame": null,
      "video_prompt": "Handheld selfie video ... she says in English, warm conversational tone, at a relaxed natural pace with no rush: \"Is this Harbor Homes unit still under a million? Let's go see it.\" She delivers the full sentence comfortably, including the final words, and then holds a brief natural pause in silence before the clip ends. Quiet street ambience under her voice, no music, no on-screen text. Avoid: identity drift, morphing face, warping hands, extra limbs, fused fingers, ..."
    },
    {
      "id": "S03",
      "time": "8-13s",
      "beat": "ACCESS",
      "source": "mg",
      "summary": "2D map, route lines light up, distance marker to the highway exit.",
      "vo": "Right off the highway. Airport's close too.",
      "on_screen_text": "EXIT 1.5 MI"
    }
  ]
}
```

This example validates as-is (`vg validate`) — the portrait/turnaround files don't need to exist for
`validate`, only for generation. It also shows the two rules a beat must never contradict: `S01` is
an `ai` shot that talks *about* the house without visually showing it (the `rules[]` entry says the
building itself is real footage only), and the `duration: "auto"` on `S01` resolves to `"8"` because
`dialogue`'s length fits `8s` but not `6s` (see *Dialogue fit* below) — always check a filled-in
example against its own rules, not just against the schema.

## Field rules

**Top level**

| Field | Required | Notes |
|---|---|---|
| `project` | yes | Title_Case_With_Underscores, used in file names |
| `format.aspect_ratio` | yes | default for every image and video; `9:16` for short-form |
| `format.language` | yes | language of dialogue and on-screen text (`id`, `en`, …) |
| `models.image` / `models.video` | no | registry ids; default from `.env` `VG_IMAGE_MODEL` / `VG_VIDEO_MODEL` |
| `image_defaults.resolution` | no | `1K` / `2K` / `4K`; default `2K` |
| `video_defaults.resolution` | no | default `1080p` |
| `style_lock.image` | no | appended by the tool to every **storyboard / first / last** prompt (not to assets) |
| `style_lock.video` | no | appended by the tool to every `video_prompt` |
| `rules` | no | client and production rules; shown on the board; the agent must obey them |

**look** — the reel's visual direction, planned in the scene stage and approved by the human before
any storyboard image (`vg approve look`). One world, one time of day, one grade, one graphic style.

| Field | Required | Notes |
|---|---|---|
| `world` · `light` · `grade` · `graphics` | todo until written | plain sentences; every later prompt and the edit plan must fit them |
| `style_frames` | 1–3 | `{id, prompt, refs}`; target `look:<id>`. Key images of the reel's look, e.g. the presenter in the world, and the world without people. May ref assets, never another style frame |

Once the look is approved, the tool adds the style frames as extra refs to every storyboard / first /
last image and to location, product and other assets (not character sheets). `"look_refs": false` on
a shot or an asset turns that off (e.g. a flat map graphic).

**characters[]** — one per recurring person.

| Field | Required | Notes |
|---|---|---|
| `name` | yes | short id, e.g. `Rani` |
| `description` | yes | appearance, age, wardrobe, personality — sent to the identity service |
| `portrait` | yes | asset id of a clean front portrait (index 0 of the identity) |
| `body` | no | asset id of a full-body image (index 1). A character with a `body` image counts **2** media-quota slots per shot instead of 1 (the tool counts it) |
| `voice` | no | `preset` (a Gemini Omni voice enum, e.g. `sulafat`), `name` (≤210), `description`, `example` (≤120) |

**assets[]** — reference sheets.

| Field | Required | Notes |
|---|---|---|
| `id` | yes | `Char_<Name>_<Sheet>` · `Loc_<Place>` · `Prod_<Item>` · `Ref_<Thing>` |
| `kind` | yes | `character` · `location` · `product` · `other` |
| `prompt` | yes | full gpt-image-2 prompt, English |
| `refs` | no | list of refs (see *Ref syntax*). Any ref → image-to-image |
| `aspect_ratio`, `resolution` | no | override the defaults |
| `look_refs` | no | `false`: do not add the approved style frames as refs (default: added, except character sheets) |

**shots[]** — in timeline order. One shot per beat is normal for short-form.

| Field | Required | Notes |
|---|---|---|
| `id` | yes | `S01`, `S02`, … (a split beat can be `S05A`, `S05B`) |
| `time` | yes | position in the edit, e.g. `3-8s` |
| `beat` | no | short label: HOOK, PROOF, CTA … |
| `source` | yes | `ai` (we generate) · `real` (client footage) · `mg` (motion graphic in the edit) |
| `summary` | yes | one line of what the viewer sees |
| `vo` / `on_screen_text` | no | voice-over line and on-screen text for the edit |
| `mode` | ai only | `frames` · `character` · `text` · `lipsync` (see below) |
| `duration` | ai only | `"auto"` or a value the video model allows (`"4"`, `"6"`, `"8"`, `"10"` on Omni) |
| `characters` | character mode | names from `characters[]`; the video model allows **at most 3** per shot (`character_ids` limit) |
| `lipsync` | lipsync mode | `{"audio": "file:6_Edit/1_Audio/Narration.wav", "start": 18.6, "end": 20.6}`: the window of the reel's approved narration this shot says on camera, in seconds of that file. The tool cuts it to an MP3 (44.1 kHz stereo) and sends it with the first frame; the clip's length is `end − start`, capped by the model (15 s on Kling AI Avatar Pro). Moving the window voids the visuals approval |
| `dialogue` | no | exact words spoken **on camera**; must appear word for word inside `video_prompt` (`vg validate` errors otherwise), and is checked against the fit rule. Normally on a `character`-mode shot with a locked voice; `frames`-mode shots can carry it too but the voice is unlocked (`vg validate` warns) |
| `storyboard` | ai only | `{prompt, refs}` — the panel |
| `first_frame` | frames mode | **Real photo:** `{"file": "0_Source/photo.jpg", "crop_x": 0.5}` — imported by `vg image --stage frames`, cropped to the reel's aspect (full height, window centred at `crop_x`, 0 = left, 1 = right), recorded as a frame at 0 credits, never sent to the image model (a property's first frame). Otherwise: `{prompt, refs}` or `{"from": "storyboard"}` (reuse the panel, costs nothing). For a real place, `refs` can point at a real photo (`["file:0_Source/photo.jpg"]`) so the frame is image-to-image from it rather than invented; otherwise give the beat `"source": "real"` or `"mg"` instead of `"ai"` |
| `last_frame` | no | `{prompt, refs}` or `null`. Usually refs `first:<ShotId>` so it stays consistent. Only sent to the video model in `frames` mode — set on a `character`/`text`-mode shot it still costs an image but is never used (`vg validate` warns) |
| `video_prompt` | ai only | the motion prompt, English, dialogue quoted in the video language |
| `video_refs` | no | extra soft reference images (`image_urls`) for `character` and `text` mode |
| `style_lock` | no | `false` skips appending `style_lock.video` to this shot's `video_prompt` (default: applied). Image `style_lock` for storyboard/first/last is always applied and never touches `assets[]` prompts |
| `notes` | no | anything the editor needs |
| `category` | no (todo on ai shots) | shot recipe from `vg-video-prompt/references/shot-categories.md`, e.g. `room_reveal`, `hook_talking` |
| `camera` | no | one move from `camera-moves.md`: `static`, `handheld`, `push_in`, `lateral_glide`, `drone_approach`, … |
| `size` | no | `ecu` · `cu` · `mcu` · `ms` · `mws` · `ws` · `ews` |
| `promise` / `pays_off` | no | the hook's promise in words / on the shot that delivers it, the hook's id; `vg validate` warns about an unpaid promise |
| `look_refs` | no | `false`: this shot's images do not get the style frames as refs (maps, flat graphics) |

**Ref syntax** (used in `refs` and `video_refs`)

| Ref | Resolves to |
|---|---|
| `Char_Rani_Portrait` | the selected version of that asset |
| `storyboard:S01` · `first:S01` · `last:S01` | the selected version of that shot image |
| `look:Look_A` | the selected version of that style frame |
| `file:0_Source/photo.jpg` | a file inside the project folder |

A ref to something not generated yet is an ordering error: generate the dependency first
(`vg image --stage` handles ordering for you).

## Modes

| Mode | Sent to the video model | Pick it when |
|---|---|---|
| `frames` | first frame (+ last frame) as hard frames | b-roll, location, product, transitions. Composition must match the frames exactly. Can still carry `dialogue`, but the voice is unlocked (`vg validate` warns) — use `character` mode when the voice must stay consistent |
| `character` | character id + voice id + the first frame (or panel) as a soft reference | a recurring person speaks or acts on camera. Same face and voice across shots |
| `text` | prompt only, plus `video_refs` as optional soft `image_urls` | cheap exploration, abstract shots |
| `lipsync` | the first frame (or panel) + a cut of the approved narration (`lipsync` window) to an audio-driven model (`kling-ai-avatar-pro`) | a presenter says the reel's own narration on camera: one voice for the whole reel, lips driven by that exact audio. The clip's own audio is muted in the edit (`clip_volume: 0`); the narration track plays |

On Gemini Omni Flash a hard first frame cannot be combined with character, voice or reference
images. The tool enforces this; the modes exist so you never have to think about it per payload.

## Dialogue fit

`characters_in_dialogue ≤ (duration − 0.7) × 10.5` — measured on a real truncation. With
`"duration": "auto"` the tool picks the shortest allowed duration that fits (minimum 4 s). A line
that does not fit 10 s must be split across two shots.

## What else `vg validate` checks

Beyond the field rules above:

- `look`: missing block or empty world/light/grade/graphics/style_frames are todos; more than 3 style frames, a style frame without `id` or `prompt`, a duplicate id, or a style frame that refs another style frame are errors.
- A `file:` ref that resolves outside the project folder is an error, not just a missing-file one.
- Every image target's `aspect_ratio`/`resolution` combination is checked against the image
  model's own limits (e.g. `4:5` at `2K` is an error at validate time on gpt-image-2, well before
  any request is sent).
- An asset in `assets[]` that no shot or character refs is a warning, not an error — it still costs
  an image to generate, so it's worth pruning, but validate won't block on it.
- `dialogue` set on a `frames`- or `text`-mode shot is a warning ("unlocked voice") — it still
  works, but the spoken voice isn't the character's locked one; prefer `character` mode when the
  voice must stay consistent.
