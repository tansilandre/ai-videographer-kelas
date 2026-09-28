# Beat Sheets for Short-Form Social

Pick the structure that matches the brief, then fill it with the brief's actual claim, proof, and
characters. A beat is a change in information or emotion — a beat that repeats the previous one
is padding.

## Hook → Problem → Proof → CTA

The default for a straightforward pitch (product, service, offer).

```
0-2s   HOOK     the claim or the tension, already in motion
2-8s   PROBLEM  what's wrong today / what the viewer recognises
8-20s  PROOF    one demonstration or one piece of evidence
20-25s CTA      the next step
```

Worked example (generic product demo, 25s):

| Time | Beat | Line |
|---|---|---|
| 0–2 | Hook | "I almost returned this." |
| 2–6 | Problem | "Every one I'd tried before broke in a week." |
| 6–8 | Problem | (cut to the broken old one, no line) |
| 8–16 | Proof | "This one's on day thirty." (demonstration) |
| 16–20 | Proof | (result shot, no line) |
| 20–25 | CTA | "Link's in bio if you want to try it." |

## Listicle

For "N reasons / N things" content — the structure the hook itself promises.

```
0-3s     HOOK  states the count: "3 things nobody tells you about X"
per item 3-6s  one reason, one shot, one on-screen number
close    2-3s  wrap line, CTA
```

State the count in the hook — it sets viewer expectations and gives them a reason to stay
(counting down). Keep each item to one idea; don't let an item run long enough to need its own
sub-beats.

## Guess / Reveal

Strong for pricing, specs, or any fact the viewer would want to guess before being told.

```
0-3s    HOOK     pose the question directly to camera: "guess how much this costs"
3-8s    BUILD    a beat of visual evidence without the answer (walkthrough, close-ups)
8-12s   REVEAL   the answer, on screen and spoken together
12-15s  CLOSE    reaction + CTA
```

The reveal must land as text and voice at the same moment — a number spoken half a second before
it appears on screen reads as sloppy, not suspenseful.

## Before / After

```
0-3s    HOOK        "two weeks ago" / "before I found this"
3-10s   BEFORE      the problem state, one fixed framing
10-15s  TURN        what changed
15-22s  AFTER       the result, in the SAME framing as BEFORE
22-25s  CLOSE       conclusion, CTA
```

BEFORE and AFTER must share camera position, framing, and light direction or the comparison
doesn't read. If both are AI shots, generate AFTER as image-to-image from the BEFORE plate/frame
so the composition matches exactly, and describe only what changed.

## POV

```
0-2s    HOOK        drop straight into the scenario, no setup, no "hey guys"
2-N     SCENE       lived-in moments in the scenario, each one a small beat
close   2-3s        the punchline or the turn
```

POV skips exposition entirely — if a POV beat sheet needs a sentence explaining the premise
before the action starts, the premise belongs in the hook line, not a separate beat.

## Duration budget

| Target | Beats | Notes |
|---|---|---|
| 15s | 4–5 | tightest form; no setup beat |
| 30s | 6–8 | one recognisable turn, one proof beat |
| 60s | 10–14 | needs a second hook/turn near the 40% mark or mid-video drop-off spikes |

If a beat runs longer than ~6s of edit time, it is probably two beats, or it is padding. Remember
that any beat routed to an AI `character`/`frames` shot still costs a minimum 4s generated clip
(see `SKILL.md`'s duration note) regardless of how short its `time` window is in the edit — and
`vg edit roughcut` does not trim it down to that window; the full 4s clip goes into the rough cut.
If the beat genuinely needs to be shorter on screen, trim it later in the edit stage, or plan the
edit's pacing around the clip's real length instead of assuming the tool will shorten it.

## The "one message" test

Before finalising the beat sheet, write the single sentence a viewer should be able to repeat
afterward. If it needs "and" to hold both halves, it's two videos — cut one.
