# Edit stack — tool comparison and rejections

Why the edit stage is built on HyperFrames + FFmpeg, and what was ruled out.

## The comparison

| Tool | Role | License | Verdict |
|---|---|---|---|
| **HyperFrames** | captions, titles, callouts, transitions, audio ducking | Apache-2.0 | **used** — designed to be agent-driven (`npx hyperframes`), word-level caption support out of the box |
| **FFmpeg** | normalise, concatenate, mix, loudness, final encode | LGPL/GPL (Homebrew build) | **used** — already the tool behind `vg edit roughcut`; also handles the final mix |
| **Hyper-Motion** (`vivoCameraResearch`) | pose-guided human video re-animation | CC BY-NC-SA | **rejected** — see below |
| **Remotion** | React-based programmatic video | commercial license for some uses | **rejected for this repo** — its license terms are a problem for a project meant to be copyable/publishable; not evaluated further |

## Why Hyper-Motion is rejected

Hyper-Motion is research code (built on Wan2.1-14B) that animates a person from a driving pose
video — it is not an editor and does nothing with captions, cuts, or audio, so it doesn't actually
compete with HyperFrames for this stage's job. Independently of that mismatch, three things rule it
out on their own:

- **License: CC BY-NC-SA — non-commercial only.** A client-facing video harness cannot ship on a
  non-commercial license.
- **Requires an NVIDIA CUDA GPU.** This harness runs on an Apple Silicon Mac (M1 Pro) with no
  discrete NVIDIA GPU — it would not run here regardless of the license.
- **Wrong job.** Even where it does run, it re-animates an existing person's motion from a driving
  video — it is not a caption/motion-graphics/mixing tool, so it wouldn't replace this stage even if
  the first two problems didn't exist.

## Why Remotion is rejected

Remotion's license restricts certain commercial and company uses; since this harness is meant to be
copyable to a new workspace and potentially published, an editor whose license terms depend on the
user's company situation is a liability worth avoiding rather than resolving case by case.

## FFmpeg — the caption-rendering gap this stack works around

Homebrew's default FFmpeg build on macOS is commonly compiled **without `libfreetype`**, so
`drawtext` (and often `subtitles`/`ass`) are unavailable — `ffmpeg -hide_banner -filters | grep -E
'drawtext|subtitles|ass'` comes back empty. `overlay`, `fade`, `xfade`, `zoompan`, and `concat`
are typically present even on that build.

This is exactly why the caption/motion-graphics job is handed to HyperFrames instead of raw FFmpeg
`drawtext`: HyperFrames renders text as HTML/CSS through a browser engine and composites the result
as video, sidestepping the missing filter entirely.

**If HyperFrames is ever unavailable and a raw-FFmpeg fallback is genuinely needed:**

1. Confirm the gap first (the grep above) rather than assuming.
2. Either install a `libass`-enabled build (`brew tap homebrew-ffmpeg/ffmpeg && brew install
   homebrew-ffmpeg/ffmpeg/ffmpeg`), or
3. Rasterise text with Pillow into an RGBA PNG per card/caption, then composite with FFmpeg's
   `overlay` + `fade` filters — this is a known-working pattern on a `drawtext`-less build, but it
   is manual work HyperFrames is meant to remove.

Two FFmpeg mistakes worth knowing before touching a fallback path:

- **A looped still (`-loop 1`) is an infinite input.** Without an explicit `-t` on the output, the
  filtered stream never reaches EOF and the process runs away instead of finishing.
  `-shortest` does not reliably fix this — bound the output duration explicitly.
- **`-ss` placement changes what you get.** `-ss` **before** `-i` is a fast keyframe seek and can
  land on the wrong frame; put it **after** `-i` when pulling an exact verification still.

## Word timings, summarised

- If the dialogue/VO came from a TTS step that returns its own timings, use those — they're already
  exact.
- Otherwise, `npx hyperframes transcribe` is the native path for word-level timestamps.
- A local fallback on macOS (no cloud call): `mlx-whisper` or `whisper.cpp`.

## Loudness target

**−14 LUFS** is the target for the final mixed export (`vg-edit/SKILL.md` Step 3) — this is a
common short-form delivery norm, not a kie.ai or HyperFrames requirement. AI-generated talking-shot
audio has been observed peaking near full scale (0 dBFS) with RMS around −16 to −17 dBFS before
normalisation — expect to pull it down, not just pass it through.
