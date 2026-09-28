---
name: vg-edit
description: Use when running the edit stage after clips are generated — "edit the video", "make a rough cut", "add captions", "subtitles", "add the disclaimer", "final export". Covers the roughcut timing pass and the captions/motion-graphics pass, ending in the final mixed export.
---

# vg-edit

Pipeline: vg-setup → vg-scene → vg-reference-sheets → vg-storyboard → vg-video-prompt → vg-video →
**vg-edit**, orchestrated by vg-director. This is the last stage — its output is the deliverable in
`99_Output/`. It runs after `vg-video` has produced approved clips for every `source: ai` shot;
`source: real` and `source: mg` shots are folded in here from footage and motion graphics, not from
`vg-video`. This stage spends no kie.ai credits — everything here is local.

**The edit plan is written earlier than the edit.** `6_Edit/Edit_Spec.json` is drafted at the
storyboard stage, because its timing, text, map, photos and captions are part of the sequence review
the human approves before any video (`vg edit animatic`, then `vg approve visuals`; see
`vg-storyboard`). Changing its text, graphics, images, timing or narration after that approval voids
it; the other sound fields (`output`, `voice`, `music`, `sfx`, a segment's `audio`/`clip_volume`) do not.

`vg edit animatic -p P` renders `6_Edit/Animatic_<Project>_v<N>.mp4`: every segment as a still (a
clip segment shows its shot's first frame or panel; a `cover` segment shows its cover image) at the
edit plan's timing (`in`/`out` when numeric, else `fallback_duration`, else reading time), with
captions, graphics, transitions and the planned narration, music and sound effects (never the macOS
stand-in voice). It is the version the human judges; re-render after every fix.

## Audio first (before the sequence review)

The sound decides the timing, so it is made before the reel is cut, and the pictures are cut to it.

1. **Narration.** One voice for the whole reel, as voice-over: people on screen keep their mouths
   closed (lip-sync is fragile, and a different voice dubbed over lips reads as fake). Write it
   short and spoken, one sentence or clue per phrase, and put a colon or full stop where a cut should
   land. Generate several takes (a TTS model, voices side by side), have them judged, then let the
   human pick by ear. Save to `6_Edit/1_Audio/`.
2. **Cut to the phrases.** Find where each phrase starts (`narration` places the captions on them;
   the tool's pause detection or a loudness curve gives the times) and set each segment's length so
   the cut lands just before its phrase. One beat per phrase; a list phrase can hold one shot with
   callouts popping on its words.
3. **Music.** An instrumental bed with a structure: quiet under the voice, a short build, half a beat
   of silence, a drop on the reveal. Generate 2–3 takes, reject any with a dead stretch, find the drop
   in the loudness curve and set `music.at` so it lands on the reveal. End the reel on a musical stop
   rather than a fade into silence.
4. **Sound effects and transitions.** A whoosh under each whip, a soft tick or tap when a title or
   callout appears, one bright hit on the reveal (with `"transition_in": "flash"`). Keep them under
   the voice; a judge calling them cartoonish or loud means lower and softer.
5. Render the animatic and listen through it as a viewer before sending it: the drop on the reveal,
   no caption showing a word before it is said, no dead air at the end.

After the clips exist, two steps: a rough cut for timing review, then captions and motion graphics
for the final export.
There is no `vg` on PATH — every command below runs as `python3 2_Tools/vg/vg.py <command>`; `vg
<command>` is this skill's shorthand for that full path, not a literal command.

## Step 1 — rough cut

```bash
python3 2_Tools/vg/vg.py edit roughcut -p <project>
```

`vg edit roughcut` normalises the selected clips to 1080×1920/30fps and concatenates them in shot
order. A beat with no clip yet shows its storyboard panel instead, if one was generated — including
an AI shot that hasn't been sent to video yet — so the timeline reads as intended footage wherever
possible. A `source: real` or `source: mg` beat with no panel falls back to a flat placeholder
colour instead: dark green for `real`, dark purple for `mg`. (An AI shot with neither a clip nor a
panel falls back to plain grey — it isn't `real`/`mg`, so neither colour applies; generate at least
the storyboard panel first.) Output: `6_Edit/Roughcut_<Project>_v<N>.mp4`. It does not trim — an AI
clip goes in at its full generated length, not its `Shotlist.json` `time` window (see `vg-scene`'s
duration note); trimming, if still wanted, is manual work in this step.

Use the roughcut to check **timing**, not polish: does each shot's actual duration match its
`Shotlist.json` `time` slot, do the cuts land where the script expects, is anything obviously the
wrong length. Flag problems to the human before moving on to captions — captioning a cut that's
about to change is wasted effort.

## Step 2 — captions, motion graphics and final export (`vg edit final`)

Proven on a real project (2026-09-24). Write `6_Edit/Edit_Spec.json` (format and a full example in
`references/edit-spec.md`), then:

```bash
python3 2_Tools/vg/vg.py edit final -p <project> --draft   # numbered draft in 6_Edit/, repeat freely
python3 2_Tools/vg/vg.py edit final -p <project>           # the deliverable in 99_Output/ (+ .srt)
```

What it does, all locally and free:

- **Segments** in timeline order: an AI `clip` (trim with `"out": "speech+0.4"` to cut the silence
  after the spoken line), a `card` (solid colour), a `placeholder` (card with a label for footage
  the client still has to shoot), or a `still` (slow zoom on a storyboard panel). A clip segment with
  `"fallback": "still"` uses its panel until the clip exists, so drafts work before video is done.
- **Voice-over**: a segment's `vo.text` is spoken with macOS `say` (Indonesian: voice `Damayanti`).
  This is a **temporary voice** for timing and review; replace it with a real VO before publishing.
- **Word-by-word captions** for every on-camera `dialogue` line and every VO. Word timings come from
  the detected speech span (FFmpeg `silencedetect`) spread by word length: close, not frame-exact.
- **Motion graphics** from `graphics[]`: `title`, `pin`, `badge`, `counter`, `map`, `callouts`,
  `card_text`, `endcard`, placed by segment and seconds (`"at"`, `"until"`). Rendered by
  `2_Tools/vg/render/overlay.swift` (built automatically with `swiftc`; macOS only).
- **Mix**: clip audio kept, ducked under voice-over, loudness normalised to −14 LUFS; H.264 + AAC,
  1080×1920. Never overwrites a delivered file: change `output` for a new version.

**Check every draft by sampling frames** (see pitfalls below): captions readable and gone when the
line ends, labels not overlapping, disclaimers present, nothing covering faces.

**Client rules to carry into graphics**: every `rules` entry in `Shotlist.json` (e.g. a mandatory
"ILUSTRASI RENCANA" label on planned infrastructure, `*` plus a disclaimer on any price) and each
shot's `on_screen_text`. A map where distances must be exact is **not** something to invent: mark
a schematic map as such on screen and swap in the client's real map before publishing.

### Alternative: HyperFrames (not exercised in this harness)

For non-Mac machines or richer animation, HyperFrames (`github.com/heygen-com/hyperframes`,
Apache-2.0, Node ≥22, downloads ~40 MB plus a browser on first use: ask the human before
installing) renders HTML/CSS/GSAP compositions with word-level captions. Treat it as untested here.

## Pacing, grade, text and sound (what makes it read as one film)

Background: `4_Docs/Research/2026-09-28_Higgsfield_Learnings_v1.0.md` §9.

- **Cut length:** 1.5–3 s for b-roll, property and product; longer only while someone speaks on
  camera. Use `in`/`out` to take 2–3 cuts from one 6–8 s clip. No three consecutive cuts with the
  same shot size and camera move. The animatic should already show this rhythm.
- **Grade:** every clip gets the same colour treatment: set `grade` in `Edit_Spec.json` (a LUT
  and/or contrast, saturation, colour temperature and a little grain; `references/edit-spec.md`).
  It unifies clips from different generations, but it cannot fix a clip whose light is wrong: keep
  the look in the frames too, and reject clips that break it. Match neighbouring shots first.
- **Text:** 2–4 words per card, bold sans, high contrast; the first text within ~0.5 s; keep it out
  of the top and bottom 10% (platform buttons) and off faces; one graphic animates at a time; each
  graphic starts on the spoken word it belongs to; one type family and one accent colour for the
  whole reel. Keep a "forbidden" list for the project (e.g. no neon, no teal-orange, no stock
  icons) in `look.graphics`.
- **Sound:** a continuous room tone and one music bed under the cuts; J/L cuts so a clip's own
  audio does not jump; foley for what is visible (footsteps on the right floor, a door latch).
  Never lay a different voice over a clip whose lips were generated for its own audio.
- **Endings:** design the last frame (a hold, the presenter settling, the CTA card), never a generic fade.

## Known FFmpeg pitfalls worth checking before relying on any of this

- **Homebrew's default ffmpeg has no `drawtext`/`libass`.** `vg edit final` does not need them (the
  Swift renderer draws all text), but if a raw-FFmpeg caption fallback is ever needed,
  check the filter set first (`ffmpeg -hide_banner -filters | grep -E 'drawtext|subtitles|ass'`)
  before assuming it exists. If it's needed, `brew tap homebrew-ffmpeg/ffmpeg && brew install
  homebrew-ffmpeg/ffmpeg/ffmpeg` adds a build with `libass`. Full detail and a Pillow-based
  workaround in `references/edit-stack.md`.
- **A looped still image (an end card, a title card) as an FFmpeg input needs an explicit bound.**
  `-loop 1` on an image input is infinite; without `-t` on the output the process never reaches
  EOF and produces a runaway file. Always bound the output duration explicitly when a static image
  is in the filter graph.
- **Verify by sampling, not by watching the whole thing frame by frame.** Pull stills at a handful
  of timestamps (`ffmpeg -i final.mp4 -ss <t> -frames:v 1 ...` — `-ss` **after** `-i` for an
  accurate, non-keyframe-snapped seek) and confirm the authored duration table matches `ffprobe` on
  the final file.

## References

- `references/edit-spec.md` — Edit_Spec.json fields, every graphic type, and a complete example
- `references/edit-stack.md` — tool comparison (HyperFrames vs. Hyper-Motion vs. Remotion vs.
  FFmpeg) and why Hyper-Motion specifically is not used here
