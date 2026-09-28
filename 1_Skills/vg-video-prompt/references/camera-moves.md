# Camera moves: the library

One move per clip. Each entry gives the wording, the speed, the end frame, what must not happen,
and where it fits. Names follow Higgsfield's camera-control catalogue so shots can be tagged and
compared; the wording is ours. Speeds are starting points for a 6–8 s clip.

## How to write any move

`<move> <direction>, <distance or duration>, <easing>, ending <end frame>; hold <1.5–2 s>.
<What stays still>.`

- The **end frame** is what the viewer sees when the move stops. Without it the model drifts,
  overshoots or plays the move back.
- The **hold** gives the editor a clean cut point and reads as intentional.
- Say what does *not* move when it matters ("no pan, no tilt", "horizon stays level").

## The moves

| Move | Wording (example) | Speed | Fits | Must not |
|---|---|---|---|---|
| **Static** | locked-off tripod, no camera movement | — | detail inserts, lip-sync lines, before/after | drift, zoom |
| **Handheld** (texture) | handheld, slight natural sway, framing never changes | — | UGC talking, selfie | chaotic shake, reframing |
| **Selfie follow** | selfie at arm's length while walking, arm sways with each step | walking pace | UGC hook, vlog | the phone becoming visible |
| **Friend-follow** | friend-held phone walking backwards in front of her, keeps her chest-up | walking pace | walk-and-talk, lifestyle | speed changes between clips |
| **Push-in (dolly in)** | slow push-in of about one metre over 6 s, eases out, ends with <X> centred | 0.15–0.2 m/s | reveals, emphasis, property rooms | zoom look, warping walls |
| **Pull-out (dolly out)** | slow pull back from <detail> over 6 s, ends showing the whole <room> | 0.15–0.2 m/s | detail → room reveal | new objects appearing at the edges |
| **Lateral glide (truck)** | gimbal glides left parallel to the counter over 6 s, ends with <X> centred | slow | kitchens, facades, bedrooms | parallax errors, bending lines |
| **Pan** | pans right about 30° over 5 s, stops on <X> | ~6°/s | following a view, scanning a room | whip, overshoot |
| **Tilt up** | tilts up from the floor to the ceiling over 5 s, stops on the skylight | ~10°/s | tall ceilings, stairs, facades | pan mixed in |
| **Arc (orbit segment)** | arcs 20° right around the island at 2 m distance over 6 s | slow | islands, products, a standing presenter | a full 360°, speed changes |
| **Crane up / jib** | rises from 1 m to 3 m over 6 s, revealing the garden behind the wall | slow | gardens, reveals over an obstacle | tilt mixed in |
| **Threshold walk** | walks through the doorway at walking pace, crosses the threshold at 3 s, eases to a stop | walking pace | room-to-room, entry reveal | doors bending, door opening itself |
| **Window approach** | moves slowly toward the window until the view fills the frame | slow | view reveal | the view changing |
| **Drone approach** | aerial, 120 m, tilted 40° down, glides forward over <X>, stops with <Y> centred | constant | establishing, location | rotation, tilted horizon |
| **Drone rise / pullback** | rises and pulls back from the facade to reveal the neighbourhood | constant | endings, context | spinning |
| **Top-down** | overhead, looking straight down, slow drift across <X> | slow | layouts, food, desks | perspective change |
| **Hyperlapse** | hyperlapse forward along the boulevard, dawn light turning to morning | — | transitions, time passing | people morphing |
| **Focus pull** | focus shifts from the foreground detail to the room behind | — | details, depth | the camera moving |

Moves that rarely work and read as "AI demo": crash zoom, 360° orbit, bullet time, whip pan,
dolly zoom, FPV weaving through interiors. Use them only when a shot is designed around them.

## Room → move map (property tours)

| Space | Move | Note |
|---|---|---|
| Exterior / facade | drone approach, or lateral glide along the facade | end on the entrance |
| Entry | threshold walk | cross the doorway at ~3 s |
| Living room | slow arc or lateral glide | end on the best view |
| Kitchen | lateral glide along the counter, or short arc around the island | end with the island centred |
| Bedroom | slow push-in toward the bed or window | short move |
| Bathroom | threshold, then a short push-in | reflections are risky: keep mirrors out of the move |
| Window / view | window approach | the view is the payoff |
| Tall ceiling / stairs | tilt up | |
| Garden / terrace | crane up, or pull-out | |
| Details (lock, tap, material) | static macro, or pull-out with focus shift | raking light shows texture |

**Anti-warp ladder** (architecture bends when the model fills too much motion):
1. One slow move, about 5–6 s, eases in and out.
2. Furniture melting → shorten the push-in.
3. Doorway or wall bending → switch to a lateral glide.
4. Still bending → static with light change only, or skip the room.

## Genre defaults

| Register | Moves | Avoid |
|---|---|---|
| UGC / vlog | handheld, selfie follow, friend-follow, static | dolly, crane, drone inside the same shot |
| Property tour | push-in, glide, arc, threshold, tilt, crane, drone | handheld shake, fast moves |
| Product / detail | static macro, slow arc, push-in | handheld |
| Landscape / area | drone approach, pullback, hyperlapse | tight shots |

Consecutive shots should not repeat both the shot size and the move; vary one of them at each cut.

## Model notes

- **Veo 3.1 Lite:** holds architecture and light well; name the move in plain words. With first +
  last frame, describe the transition only (the frames define the endpoints).
- **Seedance 1.5 Pro:** picks moves on its own when the prompt is vague; always name one. The model
  has a `fixed_lens` setting (currently always off in our registry) for locked shots.
- **Gemini Omni Flash:** motion rated weaker; keep moves small and slow.
