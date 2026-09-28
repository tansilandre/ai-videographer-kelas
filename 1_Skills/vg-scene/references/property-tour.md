# Property tour playbook

For reels that sell a house, unit or cluster. The product is the property: it must be real and it
must get screen time. Background: `4_Docs/Research/2026-09-28_Higgsfield_Learnings_v1.0.md` §7.

## 1. Ask the client one question first

> "May we animate a slow camera move from your real photos, without changing anything in the
> picture? It stays your real house; only the camera moves."

- **Yes** → rooms become `room_reveal` shots: `"first_frame": {"file": "0_Source/<photo>", "crop_x": 0.5}`
  (the tool crops the real photo to 9:16 and records it as the frame, 0 credits), Veo 3.1 Lite, and
  the prompt names only the camera move and the light.
- **No** → rooms become `photo_move` segments in the edit (a slow push or pan on the still). Free,
  safe, still better than a placeholder or a blurred background.
- Either way: **the AI never invents the building for sale.** Record the answer in `rules`.

## 2. Curate the photos

- Drop any photo with a watermark, agent badge, "for sale" banner, price stamp or floor plan.
- One best photo per space; 6–10 hero spaces for a 30–40 s reel.
- Prefer photos with good light and a clear depth line (a doorway, a corridor, a window).
- Portrait (9:16) crops: check that the key feature survives the crop before planning a move.
- Keep the sources in `0_Source/` with a sources note.

## 3. Order and pacing

Exterior → entry → living → dining → kitchen → bedroom → bathroom → outdoor / view. Open on the
strongest image (often the exterior or the view), close on outdoor or the presenter's CTA.

Generate 6–8 s per room; cut to 2–3 s in the edit. Hard cuts; crossfades only on request and at
most 0.5 s. The house should hold at least 40% of the reel.

## 4. Camera per room

See the room → move map and the anti-warp ladder in
`1_Skills/vg-video-prompt/references/camera-moves.md`. One slow move per clip (~5–6 s), eases in and
out, holds at the end. Interiors: 107° rectilinear, eye height ~1.5 m, verticals straight.

## 5. Prompt for a room from a real photo

```
Slow push-in of about one metre over 6 seconds toward the window, eye height 1.5 m, 107°
rectilinear view, verticals stay straight; eases out and holds for 2 seconds. Soft afternoon
daylight from the window.
AUDIO: quiet room tone. Nobody speaks. No music, no subtitles.
LOCKS: every wall, door, furniture piece and material stays exactly as in the first frame; nothing
is added or removed.
```

Never describe the room's contents.

## 6. Presenter and property together

The presenter (UGC) lives in the same world and light as the property photos: same time of day,
same sun direction, same grade (write it in the style prefix). She appears in the hook, in one or
two `walk_talk` / `lifestyle_broll` shots near the property (never inside an invented interior of
the product), and in the CTA. If the hook promises "I'll check it myself", a shot must show her at
the place.

## 7. Text, sound and honesty

- On-screen text: 2–4 words per card, added in the edit, out of the top and bottom 10% of the frame.
  Feature callouts point at the feature when it is visible.
- Sound: room tone per space, footsteps matched to the floor (tile, wood), one door or tap sound
  where it happens; music bed in the edit.
- Call it a walkthrough or a reel, never a "3D tour". Label planned infrastructure "ILUSTRASI
  RENCANA" and any AI illustration as such. Prices carry the disclaimer.
