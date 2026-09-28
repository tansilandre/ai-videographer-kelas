# Edit_Spec.json — the edit plan

`<project>/6_Edit/Edit_Spec.json` drives `vg edit final`. The agent writes it after the clips exist
(or earlier, with `"fallback": "still"`, for drafts). Times inside graphics are **seconds from the
start of their segment**, so trimming one clip never breaks the graphics of another.

## Top level

| Field | Notes |
|---|---|
| `output` | file name in `99_Output/`, e.g. `Harbor_Homes_Tour_v1.0.mp4`. Never reuse a delivered name |
| `voice` | `{"voice": "Damayanti", "rate": 180}` — macOS `say` voice for temporary VO (`say -v '?'` lists voices) |
| `style` | `caption_y` (0–1 of height, default 0.74), `caption_size` (px, 74), `caption_chunk` (words per caption, 3), `highlight` (colour of the word being spoken), `fonts` (`{"heavy": "AvenirNext-Heavy", ...}`) |
| `segments[]` | the timeline, in order |
| `graphics[]` | overlays placed on segments |
| `grade` | one colour treatment over the **picture** of every segment (graphics and captions stay exact): `lut` (`"file:0_Source/Look.cube"`, a .cube file in the project), `contrast` (0.5–2), `brightness` (−0.5–0.5), `saturation` (0–2), `gamma` (0.5–2), `temperature` (2000–12000 K; lower = warmer), `grain` (0–40). Applied in `vg edit final` and in the animatic. Part of the visual review: changing it (or the LUT file) voids `vg approve visuals`. Example: `{"contrast": 1.04, "saturation": 0.95, "temperature": 5600, "grain": 4}` |
| `narration` | `{"file": "file:6_Edit/1_Audio/<take>.wav", "text": "...", "start": 0, "volume": 1.0, "min_silence": 0.15}` — one voice-over track for the whole reel. Captions come from `text`: each phrase (split after `. ? ! :`; commas don't split, narrators run through lists) is placed on its own stretch of speech, and the shortest pauses are joined when the voice pauses more often than the text has phrases. Music and clip sound duck under it. Its text and audio are part of the visual review (they time the captions). Give segments that already show it `"captions": false` if they would caption their own line too |
| `music` | `{"file": "file:6_Edit/1_Audio/<track>", "volume": 0.22, "duck": 0.4, "at": 0, "start": 0, "fade_in": 0.3, "fade_out": 1.5}` — a bed under everything, ducked while anyone speaks. `start` is the offset into the track; `at` the second of the reel where it comes in. To land a drop on a reveal: `at = reveal time − drop time in the track` (find the drop in the track's loudness curve) |
| `sfx[]` | `{"file": "file:...", "at": 0.1, "segment": "S03", "volume": 0.8}` — a sound effect `at` seconds into `segment` (negative is fine: a whoosh starts ~0.28 s before its cut), or into the reel when `segment` is left out. Not part of the visual review |

## Segments

| Kind | Fields | Notes |
|---|---|---|
| clip | `clip: "S01"`, `in` (s), `out` (s or `"speech+0.4"`), `fallback: "still"`, `fallback_duration` | uses the selected clip version; `speech+N` ends N s after the last detected speech |
| card | `background` (see below) or `card: "#0E1A2B"`, `duration` (s or `"vo+0.7"`) | a background for graphics; `vo+N` = VO start + VO length + N |
| placeholder | `placeholder: "FOOTAGE ASLI\n..."`, `background`, `duration` | marks footage the client still has to supply, as a corner tag |
| still | `still: "S02"` or a target (`"asset:Loc_X"`), `duration`, `zoom: [1.0, 1.14]`, `pan` | an image with a visible push |

Any segment after the first may set `"transition_in"`: `"cut"` (default), `"flash"` (the shot fades up
from white over 0.2 s: the reveal) or `"whip"` (a horizontal motion blur on both sides of the cut; add
a whoosh in `sfx`). Hard cuts on phrase starts are the default; save flash for one reveal and whip for
changes of place.

**Never leave a flat card on screen.** Give `card` and `placeholder` segments an image
`"background": {"image": "storyboard:S02" | "asset:Loc_X", "blur": 12, "dim": 0.4, "zoom": [1.06, 1.16], "pan": 0.04}`
(blur 8–14 and dim 0.3–0.45 keep the scene readable behind graphics; heavier values turn it to mud).
A `placeholder` is shown as a small corner tag (first line) plus a short note (the rest), so the
frame still looks designed. Stills get a visible push by default (`zoom [1.0, 1.14]`, `pan -0.05`);
a clip that falls back to its panel still shows its dialogue as captions.

Any segment may add `"vo": {"text": "...", "at": 0.3, "speak": false}`: a voice-over line starting
0.3 s into the segment, which may run on into later segments. `speak: false` shows it as timed
on-screen text with no audio; use that until a real voice exists (the macOS voice sounds cheap).
`"captions": false` turns captions off for a segment's speech.

## Graphics

Common fields: `segment`, `type`, `at` (default 0), `until` (seconds or `"end"`, default end),
`through` (segment id: keep showing until that segment ends).

| Type | Fields |
|---|---|
| `title` | `text` (`\n` for two lines), `x`, `y` (0–1), `size`, `color`, `bg` — pops in with a pill background |
| `pin` | `x`, `y` (tip position), `size`, `color`, `label` — drops in with a bounce and pulses |
| `badge` | `text`, `corner` (`top-left`/`top-right`/`bottom-left`/`bottom-right`), `top`/`bottom` (px), `bg`, `border` |
| `counter` | `from`, `to`, `sep` (thousands separator, `"."` for Indonesian), `run` (s), `y`, `size`, `caption`, `sub`, `color` |
| `map` | `roads[]` (`points` [[x,y],...], `color`, `width`, `glow`, `at`, `draw` (s), `label`, `label_at`), `places[]` (`at_xy`, `label`, `color`, `at`, `size`, `label_dy`), `distance` (`points` [a,b], `at`, `label`, `label_at`, `size`, `bg`, `color`) — lines draw on, places pop in |
| `callouts` | `items[]` (`text`, `at`), `y`, `size`, `bg`, `accent` — slide in one after another |
| `card_text` | `text`, `y`, `size`, `color`, `opacity`, `font` — plain centred text (footnotes, disclaimers) |
| `endcard` | `brand`, `tagline`, `cta`, `phone`, `disclaimer`, `bg`, `bg_alpha` (0.6–0.8 lets the segment's image show), `accent` — closing card |

Coordinates are fractions of the 1080×1920 frame, `(0, 0)` top-left. Keep text out of the top
~8% and bottom ~12% where platform UI sits, and away from the caption line (`caption_y`).

## Example (property short, trimmed)

```json
{
  "output": "Harbor_Homes_Tour_v1.0.mp4",
  "voice": { "voice": "Damayanti", "rate": 180 },
  "style": { "caption_y": 0.74, "caption_size": 74, "caption_chunk": 3, "highlight": "#FFD23F" },
  "segments": [
    { "id": "S01", "clip": "S01", "out": "speech+0.4", "fallback": "still", "fallback_duration": 6.5 },
    { "id": "S02", "clip": "S02", "fallback": "still" },
    { "id": "S03", "background": { "image": "storyboard:S02", "blur": 12, "dim": 0.42 }, "duration": "vo+0.7",
      "vo": { "text": "Keluar cluster, langsung tol.", "at": 0.3, "speak": false } },
    { "id": "S06", "placeholder": "FOOTAGE ASLI · SHOW UNIT\nSmart lock → solar heater → CCTV",
      "background": { "image": "asset:Loc_Street", "blur": 8, "dim": 0.3 }, "duration": 4.4 },
    { "id": "S07", "background": { "image": "storyboard:S02", "blur": 10, "dim": 0.4 }, "duration": 3.4 },
    { "id": "END", "background": { "image": "storyboard:S08", "blur": 18, "dim": 0.35 }, "duration": 3.4 }
  ],
  "graphics": [
    { "segment": "S02", "type": "title", "text": "ACROSS FROM\nTHE MALL", "at": 0.2, "y": 0.16, "size": 64 },
    { "segment": "S02", "type": "pin", "at": 1.6, "x": 0.5, "y": 0.4, "label": "HARBOR HOMES" },
    { "segment": "S03", "type": "map", "roads": [
        { "points": [[-0.05, 0.40], [0.7, 0.375], [1.05, 0.35]], "color": "#FFD23F", "glow": true,
          "label": "TOLL ROAD", "label_at": [0.22, 0.365] } ],
      "places": [ { "at_xy": [0.3, 0.53], "label": "HARBOR HOMES", "color": "#FF5A1F", "label_dy": -58 } ],
      "distance": { "points": [[0.3, 0.53], [0.5, 0.39]], "label": "1,5 KM", "label_at": [0.5, 0.6] } },
    { "segment": "S03", "type": "card_text", "text": "Schematic map, not to scale.", "y": 0.955, "size": 24, "opacity": 0.55 },
    { "segment": "S06", "type": "callouts", "y": 0.6, "items": [ { "text": "SMART LOCK" }, { "text": "3 CCTV", "at": 1.2 } ] },
    { "segment": "S07", "type": "counter", "to": 1000, "sep": ".", "caption": "UNITS SOLD" },
    { "segment": "END", "type": "endcard", "brand": "HARBOR HOMES", "cta": "DM FOR THE LATEST PROMO",
      "phone": "0800-000-000", "disclaimer": "*Terms apply, subject to change", "bg_alpha": 0.72 }
  ]
}
```
