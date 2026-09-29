# Diagnosing a clip: symptom → cause → fix

Watch every clip yourself (sampled frames plus the audio) before showing it. Judge it as a viewer
first ("does this look filmed?"), then against this table. For API errors, 422/402 and truncated
speech checks, see `1_Skills/vg-video/references/troubleshooting.md`.

## The stop rule

1. Change **one thing** per retry and write down what changed.
2. **Two identical failures** → the prompt or the still is wrong. Rewrite, or regenerate the frame.
   Never a third identical attempt.
3. Still failing after a rewrite → **simplify the shot** (shorter, one move, one action, a different
   angle), not the wording.
4. Every retry of a video needs its own approval (`vg-video`). Salvage first: a "failed" take often
   has 1–3 good seconds the edit can use.

## Table

| Symptom | Likely cause | Fix |
|---|---|---|
| A sign, logo or tree appears that is not in the real photo (Tebak Harga S02: a purple fake-brand sign; S08: a frangipani tree) | the prompt asked for foreground parallax ("the tree and the sign in front slide past") and the model invented objects to supply it | on a real-photo first frame never ask for foreground elements; write "nothing new enters the frame" and lock signs, trees and people; use the clean stretch of the clip in the edit meanwhile |
| A push-in comes back as a sideways glide (Tebak Harga S05) | Veo Lite read the composition (door off-centre) as a truck | name the end frame ("until the door fills the centre third"); or keep the glide if it reads as real footage |
| The provider fails with "unable to generate audio for this request" (Tebak Harga S09) | the audio line was only negations ("Nobody speaks. No music, no subtitles.") | give an audio line to generate: "AUDIO: soft outdoor ambience, a light breeze, distant birds"; keep "mouth closed" under PERFORMANCE; mute clips in the edit when the reel's sound is made first |
| A loud invented sound (a glass crash under a selfie, Tebak Harga S01) | the model fills the audio track with whatever it guesses | listen to every clip; `"clip_volume": 0` in the edit when the reel has its own narration and music |
| Looks like a staged AI ad | glossy still; ad words; no micro-life | film-photography still (`vg-image-prompt`); real camera situation in the prompt; micro-events; delete slop words |
| Plastic, airbrushed skin | the still was beautified or edited twice | regenerate the still with "matte skin, visible pores, no retouching"; never re-edit a face twice |
| Clips don't look like one film | different light and grade per shot | same style prefix; stills chosen by light; one grade pass in the edit |
| Stiff or floaty motion | emotion words, no physics | physics verbs, completed state, blink/breath/weight shift |
| Action plays forward then backward | clip longer than the action | chain same-direction actions; end state; shorter clip |
| Camera drifts, overshoots or reverses | no end frame | name the end frame, add a hold |
| Jitter, morphing | two moves or too many beats | one move; one beat per 4–6 s |
| Walls, doorways or furniture bend | move too long or fast for architecture | anti-warp ladder (`camera-moves.md`) |
| Room grows, objects appear | the prompt described the room; the model invents | describe only motion; lock "nothing added or removed"; use the real photo |
| Gliding walk, sliding feet | walking written as a verb | heel strike, alternation, one foot down; same pace across clips |
| Extra fingers, orphan hands | hands in a busy action | waist-up framing, or hand count and owner; one simple hand action |
| Extra mumbled words, line said twice | line too short for the clip | shorter clip, scripted pause or silent action, "only this line" |
| Speech cut off | line too long | the fit rule; split the line or lengthen the clip |
| Lips out of sync | head motion, wide framing, long line | MCU, locked camera, no head words, 3–8 s line |
| Voice differs between clips | no voice lock (Veo) | same descriptor verbatim; move longer speech to voice-over |
| Music or subtitles appeared | default behaviour | "No music, no subtitles." |
| Garbled text in frame | text asked of the video model | remove it; add text in the edit |
| Fast rejection (under ~10 s) | content filter | reword; no age words; describe role, clothes and action |
| Same defect in every take | the still or the prompt | fix the still; rewrite |
