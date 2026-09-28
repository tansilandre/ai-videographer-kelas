"""Reading and validating Shotlist.json (schema: 1_Skills/vg-director/references/shotlist-schema.md)."""
import re

from vglib import config, craft, registry
from vglib.errors import UsageError

SOURCES = ("ai", "real", "mg")
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")  # ids become file names
MODES = ("frames", "character", "text")
ASSET_KINDS = ("character", "location", "product", "other")


class Shotlist:
    def __init__(self, data, project):
        self.data = data
        self.project = project
        self.assets = {a.get("id"): a for a in data.get("assets", [])}
        self.shots = {s.get("id"): s for s in data.get("shots", [])}
        self.characters = {c.get("name"): c for c in data.get("characters", [])}

    # ------------------------------------------------------------------ settings

    def model_id(self, kind):
        override = (self.data.get("models") or {}).get(kind)
        return override or config.setting("VG_IMAGE_MODEL" if kind == "image" else "VG_VIDEO_MODEL")

    def video_model_id(self, shot):
        """A shot may pick its own video model (`"model"`), e.g. to try a cheaper one on some shots."""
        return shot.get("model") or self.model_id("video")

    def aspect_ratio(self):
        return (self.data.get("format") or {}).get("aspect_ratio") or "9:16"

    def image_resolution(self):
        return (self.data.get("image_defaults") or {}).get("resolution") or "2K"

    def video_resolution(self):
        return (self.data.get("video_defaults") or {}).get("resolution") or "1080p"

    def style_lock(self, kind):
        return ((self.data.get("style_lock") or {}).get(kind) or "").strip()

    def ai_shots(self):
        return [s for s in self.data.get("shots", []) if s.get("source") == "ai"]

    def look(self):
        """The reel's visual direction: world, light, grade, graphics and 1-3 style frames."""
        look = self.data.get("look")
        return look if isinstance(look, dict) else {}

    def look_frames(self):
        frames = self.look().get("style_frames")
        return [f for f in frames if isinstance(f, dict) and f.get("id")] if isinstance(frames, list) else []

    def look_asset_deps(self):
        """asset:<id> targets the style frames are built from (they never get the look refs back)."""
        return self._asset_deps([r for f in self.look_frames() for r in (f.get("refs") or [])])

    # ------------------------------------------------------------------ refs and targets

    def normalize_ref(self, ref):
        """Return ('file', relpath) or ('target', 'kind:id') with first->storyboard aliasing applied."""
        if ref.startswith("file:"):
            return "file", ref[len("file:"):]
        if ":" in ref:
            kind, ident = ref.split(":", 1)
        else:
            kind, ident = "asset", ref
        if kind == "first":
            shot = self.shots.get(ident) or {}
            if (shot.get("first_frame") or {}).get("from") == "storyboard":
                kind = "storyboard"
        return "target", "%s:%s" % (kind, ident)

    def image_targets(self, stage="all"):
        targets = []
        if stage == "look":  # the style frames plus the reference sheets they are built from
            targets += self.look_asset_deps()
        if stage in ("look", "all"):
            targets += ["look:" + f["id"] for f in self.look_frames() if f.get("prompt")]
        if stage in ("refs", "all"):
            targets += ["asset:" + a["id"] for a in self.data.get("assets", [])]
        if stage in ("storyboard", "all"):
            targets += ["storyboard:" + s["id"] for s in self.ai_shots() if (s.get("storyboard") or {}).get("prompt")]
        if stage in ("frames", "all"):
            for shot in self.ai_shots():
                first = shot.get("first_frame") or {}
                if first.get("prompt") or first.get("file"):
                    targets.append("first:" + shot["id"])
                last = shot.get("last_frame") or {}
                if last.get("prompt") or last.get("file"):
                    targets.append("last:" + shot["id"])
        return targets

    def _asset_deps(self, refs, seen=None):
        """asset:<id> targets that these refs need, dependencies first."""
        seen = seen if seen is not None else []
        for ref in refs:
            kind, value = self.normalize_ref(ref) if isinstance(ref, str) else (None, None)
            if kind != "target" or not value.startswith("asset:") or value in seen:
                continue
            asset = self.assets.get(value.split(":", 1)[1])
            if asset:
                self._asset_deps(asset.get("refs") or [], seen)
                seen.append(value)
        return seen

    @staticmethod
    def _with_lock(prompt, lock):
        if not lock:
            return prompt.strip()
        marker = prompt.find("Avoid:")
        if marker > 0:
            return (prompt[:marker].rstrip() + " " + lock.rstrip(".") + ". " + prompt[marker:]).strip()
        return (prompt.rstrip() + " " + lock).strip()

    def image_request(self, target):
        """The generation request for one image target: prompt, refs, aspect ratio, resolution."""
        kind, ident = target.split(":", 1)
        if kind == "asset":
            asset = self.assets.get(ident)
            if not asset:
                raise UsageError("No asset %r in Shotlist.json" % ident)
            spec, prompt = asset, asset.get("prompt", "")
        elif kind == "look":
            spec = next((f for f in self.look_frames() if f["id"] == ident), None)
            if not spec or not spec.get("prompt"):
                raise UsageError("No style frame %r with a prompt in look.style_frames" % ident)
            spec = dict(spec, refs=spec.get("refs") or [])
            prompt = self._with_lock(spec["prompt"], self.style_lock("image"))
        else:
            shot = self.shots.get(ident)
            if not shot:
                raise UsageError("No shot %r in Shotlist.json" % ident)
            field = {"storyboard": "storyboard", "first": "first_frame", "last": "last_frame"}.get(kind)
            if not field:
                raise UsageError("%s is not an image target" % target)
            spec = shot.get(field) or {}
            if spec.get("from") == "storyboard":
                raise UsageError("%s reuses the storyboard panel; generate storyboard:%s instead" % (target, ident))
            if spec.get("file") and kind in ("first", "last"):  # a real photo, imported, never generated
                return {"target": target, "file": spec["file"], "crop_x": float(spec.get("crop_x", 0.5)),
                        "aspect_ratio": spec.get("aspect_ratio") or self.aspect_ratio(), "refs": []}
            if not spec.get("prompt"):
                raise UsageError("Shot %s has no %s.prompt" % (ident, field))
            prompt = self._with_lock(spec["prompt"], self.style_lock("image"))
        return {
            "target": target,
            "prompt": prompt.strip(),
            "refs": [self.normalize_ref(r) for r in spec.get("refs", [])],
            "aspect_ratio": spec.get("aspect_ratio") or self.aspect_ratio(),
            "resolution": spec.get("resolution") or self.image_resolution(),
        }

    def video_prompt(self, shot):
        if shot.get("style_lock", True) is False:
            return (shot.get("video_prompt") or "").strip()
        return self._with_lock(shot.get("video_prompt") or "", self.style_lock("video"))

    def duration(self, shot, spec):
        """Resolve a shot's duration against the video model (auto = shortest that fits the dialogue)."""
        raw = str(shot.get("duration") or "auto")
        dialogue = shot.get("dialogue") or ""
        if raw == "auto":
            fitted = registry.fit_duration(spec, dialogue)
            if fitted is None:
                raise UsageError("Shot %s: dialogue (%d chars) does not fit the longest clip; split it"
                                 % (shot["id"], len(dialogue)))
            return fitted
        return int(raw)

    # ------------------------------------------------------------------ validation

    def validate(self):
        """Return (errors, warnings). Fields that later stages fill in (storyboard, frames, video
        prompt) are not errors while missing; they are listed in self.todos instead."""
        errors, warnings = [], []
        self.todos = []
        data = self.data
        if not data.get("project"):
            errors.append("project: missing")
        fmt = data.get("format") or {}
        for key in ("aspect_ratio", "language"):
            if not fmt.get(key):
                errors.append("format.%s: missing" % key)

        try:
            video_spec = registry.get(self.model_id("video"), "video", allow_untested=True)
        except UsageError as exc:
            errors.append(str(exc))
            video_spec = None
        try:
            registry.get(self.model_id("image"), "image", allow_untested=True)
        except UsageError as exc:
            errors.append(str(exc))

        seen = set()
        for asset in data.get("assets", []):
            aid = asset.get("id")
            if not aid:
                errors.append("assets: an asset has no id")
                continue
            if not SAFE_ID.match(str(aid)):
                errors.append("assets.%s: id may use only letters, digits, _ and - (it becomes a file name)" % aid)
            if aid in seen:
                errors.append("assets.%s: duplicate id" % aid)
            seen.add(aid)
            if asset.get("kind") not in ASSET_KINDS:
                errors.append("assets.%s.kind: must be one of %s" % (aid, ", ".join(ASSET_KINDS)))
            if not (asset.get("prompt") or "").strip():
                errors.append("assets.%s.prompt: missing" % aid)
            errors += self._check_refs("assets.%s.refs" % aid, asset.get("refs", []))

        errors += self._validate_look()
        craft_warnings, craft_todos = craft.check(data)
        warnings += craft_warnings
        self.todos += craft_todos

        for char in data.get("characters", []):
            name = char.get("name")
            if not name:
                errors.append("characters: a character has no name")
                continue
            if not char.get("description"):
                errors.append("characters.%s.description: missing" % name)
            if char.get("portrait") not in self.assets:
                errors.append("characters.%s.portrait: %r is not an asset id" % (name, char.get("portrait")))
            if char.get("body") and char["body"] not in self.assets:
                errors.append("characters.%s.body: %r is not an asset id" % (name, char["body"]))
            voice = char.get("voice")
            if voice:
                if not voice.get("preset") or not voice.get("name"):
                    errors.append("characters.%s.voice: needs preset and name" % name)
                if len(voice.get("name", "")) > 210:
                    errors.append("characters.%s.voice.name: over 210 characters" % name)
                if len(voice.get("example", "")) > 120:
                    errors.append("characters.%s.voice.example: over 120 characters" % name)

        seen = set()
        for shot in data.get("shots", []):
            sid = shot.get("id")
            if not sid:
                errors.append("shots: a shot has no id")
                continue
            if not SAFE_ID.match(str(sid)):
                errors.append("shots.%s: id may use only letters, digits, _ and - (it becomes a file name)" % sid)
            if sid in seen:
                errors.append("shots.%s: duplicate id" % sid)
            seen.add(sid)
            where = "shots.%s" % sid
            if shot.get("source") not in SOURCES:
                errors.append("%s.source: must be one of %s" % (where, ", ".join(SOURCES)))
            for key in ("time", "summary"):
                if not shot.get(key):
                    errors.append("%s.%s: missing" % (where, key))
            if shot.get("source") != "ai":
                continue
            mode = shot.get("mode")
            shot_spec = video_spec
            if shot.get("model"):
                try:
                    shot_spec = registry.get(shot["model"], "video", allow_untested=True)
                except UsageError as exc:
                    errors.append("%s.model: %s" % (where, exc))
                    shot_spec = None
            if mode not in MODES:
                errors.append("%s.mode: must be one of %s" % (where, ", ".join(MODES)))
            elif shot_spec and mode not in shot_spec.get("modes", {}):
                errors.append("%s.mode: %s is not supported by %s" % (where, mode, shot_spec["id"]))
            if not (shot.get("storyboard") or {}).get("prompt") and not (shot.get("first_frame") or {}).get("file"):
                self.todos.append("%s.storyboard.prompt: not written yet (vg-storyboard)" % where)
            errors += self._check_refs(where + ".storyboard.refs", (shot.get("storyboard") or {}).get("refs", []))
            if not (shot.get("video_prompt") or "").strip():
                self.todos.append("%s.video_prompt: not written yet (vg-video-prompt)" % where)
            first = shot.get("first_frame")
            if mode == "frames" and not first:
                self.todos.append("%s.first_frame: needed before video in frames mode (vg-storyboard)" % where)
            if first and not first.get("prompt") and first.get("from") != "storyboard" and not first.get("file"):
                errors.append("%s.first_frame: needs a prompt, \"from\": \"storyboard\" or a real photo \"file\""
                              % where)
            if first and first.get("prompt") and first.get("from") == "storyboard":
                errors.append("%s.first_frame: has both a prompt and \"from\": \"storyboard\"; keep one" % where)
            if first and first.get("prompt"):
                errors += self._check_refs(where + ".first_frame.refs", first.get("refs", []))
            for key in ("first_frame", "last_frame"):
                errors += self._check_file_frame("%s.%s" % (where, key), shot.get(key))
            last = shot.get("last_frame")
            if last:
                if not last.get("prompt") and not last.get("file"):
                    errors.append("%s.last_frame.prompt: missing" % where)
                errors += self._check_refs(where + ".last_frame.refs", last.get("refs", []))
                if mode != "frames":
                    warnings.append("%s.last_frame: only frames mode sends a last frame; it will be unused" % where)
            if mode == "character":
                names = shot.get("characters") or []
                if not names:
                    errors.append("%s.characters: character mode needs at least one" % where)
                for name in names:
                    if name not in self.characters:
                        errors.append("%s.characters: %r is not in characters[]" % (where, name))
            errors += self._check_refs(where + ".video_refs", shot.get("video_refs", []))
            if shot_spec:
                try:
                    duration = self.duration(shot, shot_spec)
                    allowed = registry.allowed_durations(shot_spec)
                    if allowed and duration not in allowed:
                        errors.append("%s.duration: %s not allowed (%s)" % (where, duration, allowed))
                    elif not registry.dialogue_fits(shot_spec, shot.get("dialogue"), duration):
                        errors.append("%s.dialogue: %d chars do not fit %ss; use \"auto\" or a longer duration"
                                      % (where, len(shot.get("dialogue") or ""), duration))
                except (UsageError, ValueError) as exc:
                    errors.append("%s.duration: %s" % (where, exc))
            dialogue = (shot.get("dialogue") or "").strip()
            prompt_text = shot.get("video_prompt") or ""
            if dialogue and prompt_text.strip() and dialogue not in prompt_text:
                errors.append("%s.dialogue: the exact line must appear word for word in video_prompt "
                              "(the fit check measures the dialogue field)" % where)
            if not dialogue and re.search(r'"[^"]{20,}"', prompt_text) and re.search(r"\b(says|speaks|asks)\b", prompt_text):
                warnings.append("%s: video_prompt quotes speech but dialogue is empty, so its length "
                                "is not checked; copy the line into dialogue" % where)
            if shot.get("dialogue") and mode in ("frames", "text"):
                warnings.append("%s: dialogue outside character mode is spoken by an unlocked voice; "
                                "use character mode for a consistent voice" % where)
        # image parameters per target (e.g. 4:5 at 2K) and assets nothing uses
        try:
            image_spec = registry.get(self.model_id("image"), "image", allow_untested=True)
            for target in self.image_targets("all"):
                try:
                    request = self.image_request(target)
                except UsageError:
                    continue
                if request.get("file"):  # a real photo is imported, not generated: no model limits apply
                    continue
                for problem in registry.check_params(image_spec, {"aspect_ratio": request["aspect_ratio"],
                                                                  "resolution": request["resolution"]}):
                    errors.append("%s: %s" % (target, problem))
        except UsageError:
            pass
        used = set()
        for char in data.get("characters", []):
            used.update([char.get("portrait"), char.get("body")])
        for holder in list(data.get("assets", [])) + self.look_frames() + [
                part for s in data.get("shots", []) for part in
                (s.get("storyboard") or {}, s.get("first_frame") or {}, s.get("last_frame") or {})]:
            for ref in (holder.get("refs") or [] if isinstance(holder, dict) else []):
                kind, value = self.normalize_ref(ref)
                if kind == "target" and value.startswith("asset:"):
                    used.add(value.split(":", 1)[1])
        for shot in data.get("shots", []):
            for ref in shot.get("video_refs", []):
                kind, value = self.normalize_ref(ref)
                if kind == "target" and value.startswith("asset:"):
                    used.add(value.split(":", 1)[1])
        for aid in self.assets:
            if aid and aid not in used:
                warnings.append("assets.%s: no shot or character uses it (it still costs an image)" % aid)
        return errors, warnings

    def _check_file_frame(self, where, frame):
        """A frame given as a real photo: {"file": "0_Source/x.jpg", "crop_x": 0-1}, alone."""
        if not isinstance(frame, dict) or "file" not in frame:
            return []
        errors = []
        if frame.get("prompt") or frame.get("from"):
            errors.append("%s: a real photo \"file\" cannot be combined with a prompt or \"from\"" % where)
        root = self.project.path.resolve()
        path = (root / str(frame["file"])).resolve()
        if root not in path.parents:
            errors.append("%s.file: %s must be inside the project" % (where, frame["file"]))
        elif not path.is_file():
            errors.append("%s.file: %s not found" % (where, frame["file"]))
        crop = frame.get("crop_x", 0.5)
        if isinstance(crop, bool) or not isinstance(crop, (int, float)) or not 0 <= crop <= 1:
            errors.append("%s.crop_x: must be a number from 0 (left edge) to 1 (right edge)" % where)
        return errors

    def _validate_look(self):
        """The look block is planned in the scene stage; missing parts are todos, broken parts errors."""
        look = self.data.get("look")
        if look is None:
            self.todos.append("look: not written yet; the reel's world, light, grade, graphics and style frames "
                              "(vg-scene). Storyboard images and video are refused until the look is approved")
            return []
        if not isinstance(look, dict):
            return ["look: must be an object"]
        errors = []
        for key in ("world", "light", "grade", "graphics"):
            value = look.get(key)
            if value is not None and not isinstance(value, str):
                errors.append("look.%s: must be text (one or two sentences)" % key)
            elif not (value or "").strip():
                self.todos.append("look.%s: not written yet (vg-scene)" % key)
        frames = look.get("style_frames") or []
        if not isinstance(frames, list):
            return errors + ["look.style_frames: must be a list"]
        if not frames:
            self.todos.append("look.style_frames: add 1-3 style frames (vg-scene)")
        if len(frames) > 3:
            errors.append("look.style_frames: %d frames; use 1-3 so the look stays one look" % len(frames))
        seen = set()
        for i, frame in enumerate(frames):
            fid = frame.get("id") if isinstance(frame, dict) else None
            if not fid:
                errors.append("look.style_frames[%d]: needs an id, e.g. Look_A" % i)
                continue
            if not SAFE_ID.match(str(fid)):
                errors.append("look.style_frames.%s: id may use only letters, digits, _ and - (it becomes a "
                              "file name)" % fid)
                continue
            if fid in seen:
                errors.append("look.style_frames.%s: duplicate id" % fid)
            seen.add(fid)
            if not isinstance(frame.get("prompt") or "", str) or not (frame.get("prompt") or "").strip():
                errors.append("look.style_frames.%s.prompt: missing" % fid)
            refs = frame.get("refs", [])
            errors += self._check_refs("look.style_frames.%s.refs" % fid, refs)
            if isinstance(refs, list) and any(self.normalize_ref(r)[1].startswith("look:") for r in refs
                                              if isinstance(r, str)):
                errors.append("look.style_frames.%s.refs: a style frame may not ref another style frame" % fid)
        return errors

    def _check_refs(self, where, refs):
        errors = []
        if not isinstance(refs, list):
            return ["%s: must be a list" % where]
        for ref in refs:
            kind, value = self.normalize_ref(ref)
            if kind == "file":
                path = (self.project.path / value).resolve()
                try:
                    path.relative_to(self.project.path.resolve())
                except ValueError:
                    errors.append("%s: %s points outside the project folder" % (where, ref))
                    continue
                if not path.is_file():
                    errors.append("%s: file %s not found in the project" % (where, value))
                continue
            tkind, ident = value.split(":", 1)
            if tkind == "asset" and ident not in self.assets:
                errors.append("%s: %r is not an asset id" % (where, ref))
            elif tkind in ("storyboard", "first", "last") and ident not in self.shots:
                errors.append("%s: %r points to an unknown shot" % (where, ref))
            elif tkind == "look" and ident not in [f["id"] for f in self.look_frames()]:
                errors.append("%s: %r is not a style frame id" % (where, ref))
            elif tkind not in ("asset", "storyboard", "first", "last", "look"):
                errors.append("%s: %r is not a valid ref" % (where, ref))
        return errors
