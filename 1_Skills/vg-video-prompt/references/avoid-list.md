# Locks and the few bans worth writing

The words in a prompt summon things, including words inside a "no". A long `Avoid:` list of
failures (morphing face, extra fingers, flicker…) mostly adds noise and can pull the named failure
in. Research across Higgsfield-oriented production doctrine agrees: state what must stay true
(positive locks), and ban only what the model does by default when left alone.

## 1. Positive locks (write these)

One `LOCKS:` line at the end of the body, 1–3 clauses, specific to the shot:

| Shot | Lock |
|---|---|
| Person from a first frame | her face, hair and clothes stay identical to the first frame |
| Talking head | one face in frame; others: lips at rest, jaw closed |
| Hands | one hand (or: both hands, hers), five fingers each, the object stays in her hand |
| Property / interior | walls, doors, furniture and materials stay exactly as in the first frame; nothing is added or removed; verticals stay straight |
| Aerial / exterior | buildings and roads keep their shapes; cars stay in their lanes; level horizon |
| First + last frame | the space and light match both frames; one continuous move between them |
| Light | the light direction and colour stay constant |

## 2. Bans worth writing (the model's default is the failure)

Short, at the end of the AUDIO line or the LOCKS line:

- `No music, no subtitles.` (video models add both by default)
- `no on-screen text` (add text in the edit instead)
- `Nobody speaks.` / `Mouth closed, not speaking.` on shots without dialogue
- `real-time speed, no slow motion` on action
- `no cuts, one continuous shot` when a model tends to cut inside a clip

**Veo:** if you do add negatives, write them as plain nouns ("text, watermark, frame border"), not
instructions ("no walls").

## 3. Don't

- Don't paste a baseline list of 20 failure words into every prompt.
- Don't ban a colour ("no yellow"); give the colour one named source instead ("the only warm light
  is the lamp at frame right").
- Don't write "photorealistic", "8K", "high quality" as fixes; they are noise.
- Don't fix a bad still with prompt words: a drifted face, fused fingers or bad light usually comes
  from the first frame. Regenerate the frame (`vg-storyboard`, `vg-image`).

## When a shot keeps failing

1. Read the task's failure reason. A content-filter rejection needs different words (describe role,
   clothes and action; never age words like girl/boy/young), not more constraints.
2. Simplify: one move, one action, shorter clip.
3. Check the frame, not the prompt.
4. Two identical failures → rewrite the prompt or fix the still. Never a third identical try.
   (`diagnosing.md`)
