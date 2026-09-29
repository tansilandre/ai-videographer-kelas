# Shot categories: recipes

Every shot in a reel belongs to one category. The category decides the model, framing, move,
length, sound and risks, so the choice is made once and checked, instead of improvised per prompt.
(Higgsfield sells the same idea as named modes and presets; these recipes are ours.)

Set it on the shot: `"category"`, plus `"camera"` (a move from `camera-moves.md`: static, handheld,
selfie_follow, friend_follow, push_in, pull_out, lateral_glide, pan, tilt_up, arc, crane_up,
threshold_walk, window_approach, drone_approach, drone_rise, top_down, hyperlapse, focus_pull) and
`"size"` (ecu, cu, mcu, ms, mws, ws, ews). A hook sets `"promise"` (what it promises, in words) and
the shot that delivers it sets `"pays_off": "<hook id>"`. `format.product_share_min` (e.g. 0.4) sets
the product's minimum share of screen time. `vg validate` then warns about unknown names, an unpaid
promise, too little product time, and three cuts in a row with the same size and move.

| Category | Job in the reel | Model / mode | Frame | Camera | Length | Sound | Watch out |
|---|---|---|---|---|---|---|---|
| `hook_talking` | stop the scroll with a line | Kling AI Avatar Pro · lipsync (the reel's own narration, eye-contact first frame); or Veo 3.1 Lite · frames when the clip makes its own voice | selfie or friend-held, MCU | handheld texture, static framing | 6–8 s; first word before ~0.8 s | her line only | line fit and floor; one face |
| `hook_visual` | stop the scroll with an image | Veo 3.1 Lite · frames | the reveal's start | door opens / window approach / pull-out from a detail | 4–6 s (cut to 1.5–3 s) | one sound (door, footsteps) | the payoff must be visible in 2 s |
| `talking_cta` | the offer and the call to action | Kling AI Avatar Pro · lipsync, or Veo 3.1 Lite · frames | MCU, steady | static or very slow push-in | 6–8 s | her line only | settle to a steady frame at the end |
| `walk_talk` | move through the place while talking | Veo 3.1 Lite · frames | chest-up, friend-follow | friend-follow at walking pace | 8 s | her line + footsteps | gait physics; same pace in every clip |
| `lifestyle_broll` | the life the place offers, under voice-over | Veo 3.1 Lite · frames | presenter in the world | slow glide or static | 4–8 s (cut to 2–3 s) | ambience, mouth closed | no lips moving |
| `room_reveal` | show a real room | Veo 3.1 Lite · frames, **first frame = real photo** (`"first_frame": {"file": …, "crop_x": …}`) | the real photo | push-in / glide / arc (room → move map) | 6 s (cut to 2–3 s) | room tone, one sound | prompt names only camera and light |
| `threshold_reveal` | move between two spaces | Veo 3.1 Lite · first + last frame | doorway | threshold walk | 8 s | footsteps changing surface | door geometry; 8 s with two frames |
| `view_reveal` | the view from the window | Veo 3.1 Lite · frames | inside, window in frame | window approach | 6 s | birds / street outside | the view must stay the same |
| `detail_insert` | prove a feature (smart lock, material) | Seedance 1.5 Pro silent or Veo · frames | macro, raking light | static, or pull-out with focus shift | 4 s (cut to 1.5–2 s) | one tactile sound | hands; no text |
| `aerial_establish` | where it is | Veo 3.1 Lite · frames | drone plate or real photo | drone approach / pullback | 8 s (cut to 3–4 s) | wind, distant traffic | invented geography; use a real photo as the first frame |
| `concept_render` | planned infrastructure | Veo 3.1 Lite · frames (+ last) | render still | slow push-in | 8 s | city hum | label ILUSTRASI RENCANA in the edit |
| `transition` | bridge two looks or places | Veo · first + last frame | both endpoints | one continuous move | 4–8 s | a whoosh-free natural sound | the two frames must share light |
| `photo_move` | a real photo that must not be AI-animated | — (edit stage) | the photo | slow push or pan in `vg edit` | 2–4 s | music / VO | none: free and safe |
| `graphic` | numbers, maps, text | — (edit stage) | card or blurred plate | animated graphic | 2–4 s | VO | one element at a time |

## Formats (sequences of categories)

**Property tour 30–40 s:** `hook_visual` or `hook_talking` → `aerial_establish` → `room_reveal` ×3–5
(order: entry, living, kitchen, bedroom, view) with a `detail_insert` or two → `lifestyle_broll` →
`talking_cta`. The product (the house) should hold at least 40% of screen time.

**UGC review 20–30 s:** `hook_talking` → `walk_talk` or `lifestyle_broll` (claim) →
`room_reveal`/`detail_insert` (proof) → `talking_cta`.

**Before / after:** `photo_move` or `room_reveal` (before) → `transition` → the after shot, same
framing, locked camera.

Every hook makes a promise; name the shot that pays it off. A "let me check it myself" hook needs
her on camera at the place.
