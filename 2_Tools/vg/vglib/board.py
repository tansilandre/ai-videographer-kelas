"""Static HTML review board. One self-contained file in the project root, relative image paths,
no server. Regenerate with `vg board` after every stage."""
import html
import urllib.parse

from vglib import config, registry, review
from vglib.errors import UsageError
from vglib.generate import _done, _in_flight, build_video_job, load, video_params
from vglib.project import Project, now_iso

CSS = """
:root{--bg:#f6f5f2;--panel:#fff;--ink:#1d1d1b;--muted:#6b6a66;--line:#e2e0da;--accent:#c2410c;
--ai:#1d4ed8;--real:#15803d;--mg:#7c3aed;--warn:#b45309;--ok:#15803d;--chip:#f0eee9}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#141413;--panel:#1d1d1b;--ink:#ecebe7;
--muted:#9c9a94;--line:#2e2d2a;--accent:#fb923c;--ai:#93b4ff;--real:#6ee7a0;--mg:#c4a5ff;--warn:#fbbf24;
--ok:#6ee7a0;--chip:#262523}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif}
main{max-width:1280px;margin:0 auto;padding:28px 16px 80px}
h1{font-size:28px;margin:0 0 4px}h2{font-size:18px;margin:40px 0 12px;padding-bottom:6px;border-bottom:1px solid var(--line)}
.sub{color:var(--muted);margin:0 0 20px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.stat b{display:block;font-size:22px}.stat span{color:var(--muted);font-size:13px}
.gate{margin-top:12px;padding:12px 14px;border-radius:10px;border:1px solid var(--warn);color:var(--warn);background:var(--panel)}
.gate.ok{border-color:var(--ok);color:var(--ok)}
ul.rules{margin:0;padding-left:20px;color:var(--muted)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:12px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden}
.card .body{padding:10px 12px}.card img,.card video{display:block;width:100%;background:var(--chip)}
.ph{display:flex;align-items:center;justify-content:center;aspect-ratio:9/16;background:var(--chip);
color:var(--muted);font-size:13px;text-align:center;padding:12px}
.id{font-weight:600;font-size:13px;word-break:break-all}.muted{color:var(--muted);font-size:13px}
details{margin-top:6px}summary{cursor:pointer;color:var(--muted);font-size:12px}
details p{font-size:12px;white-space:pre-wrap;margin:6px 0 0}
.shot{display:grid;grid-template-columns:170px 1fr;gap:16px;background:var(--panel);border:1px solid var(--line);
border-radius:12px;padding:14px;margin-bottom:12px}
.shot h3{margin:0;font-size:16px}.meta{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0 8px}
.chip{background:var(--chip);border-radius:999px;padding:2px 9px;font-size:12px}
.src-ai{color:var(--ai)}.src-real{color:var(--real)}.src-mg{color:var(--mg)}
.frames{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,160px));gap:8px;margin-top:10px}
.frames figure{margin:0}.frames figcaption{font-size:11px;color:var(--muted);margin-top:3px}
.frames img,.frames video{width:100%;border-radius:6px;display:block;background:var(--chip)}
.line{margin:2px 0}.line b{font-weight:600}
.thumb img{display:block;width:100%;height:auto;border-radius:8px;background:var(--chip)}
.thumb .ph{border-radius:8px}.card img{height:auto}
.strip{display:flex;gap:8px;overflow-x:auto;padding-bottom:8px}
.strip figure{flex:0 0 118px;margin:0}.strip img,.strip .ph{width:100%;aspect-ratio:9/16;object-fit:cover;
border-radius:6px;display:block;background:var(--chip)}.strip .ph{font-size:11px;padding:6px}
.strip figcaption{font-size:11px;color:var(--muted);margin-top:3px;line-height:1.3}
.lookgrid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,2fr);gap:16px}
.lookgrid dl{margin:0}.lookgrid dt{font-weight:600;font-size:13px}.lookgrid dd{margin:0 0 8px;color:var(--muted);font-size:13px}
.animatic video{max-width:260px;width:100%;border-radius:8px;display:block;background:var(--chip)}
@media (max-width:640px){.shot{grid-template-columns:1fr}.shot>.thumb{max-width:220px}.lookgrid{grid-template-columns:1fr}}
"""


def _src(project, path):
    return urllib.parse.quote(project.rel(path)) if path else None


def _img(project, path, alt, placeholder):
    src = _src(project, path)
    if not src:
        return '<div class="ph">%s</div>' % html.escape(placeholder)
    return '<a href="%s"><img loading="lazy" src="%s" alt="%s"></a>' % (src, src, html.escape(alt))


def _details(label, text):
    if not text:
        return ""
    return "<details><summary>%s</summary><p>%s</p></details>" % (html.escape(label), html.escape(text))


def _look_section(project, sl, state):
    look = sl.look()
    out = ["<h2>Look</h2>"]
    if not look:
        out.append("<p class='muted'>No look block yet. The scene stage writes the reel's world, light, grade, "
                   "graphics and 1-3 style frames; storyboard images wait until the human approves the look.</p>")
        return out
    out.append("<div class='lookgrid'><dl>")
    for key in ("world", "light", "grade", "graphics"):
        out.append("<dt>%s</dt><dd>%s</dd>" % (key.title(), html.escape(look.get(key) or "not written")))
    out.append("</dl><div class='grid'>")
    for frame in sl.look_frames():
        target = "look:" + frame["id"]
        entry = project.selected_entry(target, state)
        out.append("<div class='card'>%s<div class='body'><div class='id'>%s</div><div class='muted'>%s</div>%s"
                   "</div></div>" % (_img(project, project.selected(target, state), frame["id"], "not generated"),
                                     html.escape(frame["id"]), html.escape("v%d" % entry["v"] if entry else "missing"),
                                     _details("prompt", frame.get("prompt"))))
    out.append("</div></div>")
    return out


def _filmstrip(project, sl, state):
    """Every beat in timeline order: the edit plan's segments when it exists, else the shot list."""
    out = ["<h2>Filmstrip</h2>"]
    try:
        spec = review.edit_spec(project)
    except UsageError as exc:  # the board reports a broken edit plan, it never refuses
        out.append("<div class='gate'>Edit plan cannot be read: %s</div>" % html.escape(str(exc)))
        spec = None
    if not spec:
        out.append("<p class='muted'>No 6_Edit/Edit_Spec.json yet: showing the shot list. The sequence review "
                   "needs the edit plan (text, map, photos, captions) and an animatic.</p>")
    out.append("<div class='strip'>")
    for beat in review.reel_beats(project, sl, state, spec):
        out.append("<figure>%s<figcaption><b>%s</b> %s</figcaption></figure>" % (
            _img(project, beat["image"], beat["id"], beat["placeholder"]), html.escape(beat["id"]),
            html.escape((beat["text"] or "")[:90])))
    out.append("</div>")
    latest = (state.get("animatics") or [None])[-1]
    if latest and (project.path / latest["path"]).is_file():
        out.append("<div class='animatic'><p class='muted'>Latest animatic: %s (%s)</p>"
                   "<video controls preload='metadata' src='%s'></video></div>"
                   % (html.escape(latest["path"]), html.escape(latest["at"]),
                      urllib.parse.quote(latest["path"])))
    else:
        out.append("<p class='muted'>No animatic yet: run vg edit animatic.</p>")
    return out


def build(project):
    sl = load(project, allow_errors=True)
    data = sl.data
    state = project.read_state()
    errors, warnings = sl.validate()
    video_spec = None
    try:
        video_spec = registry.get(sl.model_id("video"), "video", allow_untested=True)
    except UsageError:
        pass

    # video estimate and gate state per AI shot
    shot_video = {}
    remaining_video = 0.0
    for shot in sl.ai_shots():
        info = {"cost": None, "duration": None, "gate": "not approved", "note": ""}
        try:
            video_spec = registry.get(sl.video_model_id(shot), "video", allow_untested=True)
        except UsageError:
            video_spec = None
        if video_spec:
            try:
                job = build_video_job(project, sl, shot, state, video_spec)
                info.update(cost=job["cost"], duration=job["params"]["duration"])
                done = _done(project, state, job["key"], job["target"])
                approval = state["approvals"]["video"].get(shot["id"])
                if _in_flight(state, job["target"]):
                    info["gate"] = "in flight"
                elif done:
                    info["gate"] = "generated"
                elif approval and approval["snapshot"] == job["key"] and not approval.get("used"):
                    info["gate"] = "approved"
                elif approval and approval["snapshot"] != job["key"]:
                    info["gate"] = "changed since approval"
                if not done and info["gate"] != "in flight":
                    remaining_video += job["cost"]
            except UsageError as exc:
                try:
                    params = video_params(sl, shot, video_spec)
                    info.update(cost=registry.price(video_spec, params), duration=params["duration"])
                    remaining_video += info["cost"]
                except UsageError:
                    pass
                info["note"] = str(exc)
        shot_video[shot["id"]] = info

    spent = Project.spent(state)
    balance = (state.get("balance") or {}).get("credits")
    n_ai = len(sl.ai_shots())
    n_ready = sum(1 for v in shot_video.values() if not v["note"])
    approved = [k for k, v in shot_video.items() if v["gate"] in ("approved", "generated", "in flight")]

    out = []
    out.append("<!doctype html><html lang='en'><head><meta charset='utf-8'>"
               "<meta name='viewport' content='width=device-width,initial-scale=1'>")
    out.append("<title>%s Board</title><style>%s</style></head><body><main>"
               % (html.escape(data.get("project", project.name)), CSS))
    out.append("<h1>%s</h1>" % html.escape(data.get("title") or data.get("project") or project.name))
    out.append("<p class='sub'>%s · %s · %s · %s · board built %s</p>" % (
        html.escape(data.get("client", "")), html.escape(project.name),
        html.escape((data.get("format") or {}).get("aspect_ratio", "")),
        html.escape("language: %s" % (data.get("format") or {}).get("language", "")), now_iso()))

    out.append("<div class='stats'>")
    for value, label in (
        ("%g" % spent, "credits committed"),
        ("%g" % config.number("VG_BUDGET_PROJECT"), "project budget"),
        ("%s" % ("%g" % balance if balance is not None else "?"), "last known balance"),
        ("%g" % remaining_video, "video still to spend"),
        ("%d / %d" % (n_ready, n_ai), "AI shots ready for video"),
    ):
        out.append("<div class='stat'><b>%s</b><span>%s</span></div>" % (html.escape(value), html.escape(label)))
    out.append("</div>")
    for name, ok, text in review.gate_status(project, sl, state):
        hint = {"look": "the style frames below", "visuals": "the filmstrip and animatic below"}[name]
        out.append("<div class='gate%s'>%s review: %s%s</div>" % (
            " ok" if ok else "", name.title(), html.escape(text),
            "" if ok else html.escape(". The human approves %s in chat before any video." % hint)))
    if n_ai and len(approved) == n_ai:
        out.append("<div class='gate ok'>Video gate: all %d AI shots approved or generated.</div>" % n_ai)
    else:
        out.append("<div class='gate'>Video gate: %d of %d AI shots approved. Nothing is spent on video until the "
                   "human approves it (cost per shot below).</div>" % (len(approved), n_ai))
    if errors:
        out.append("<div class='gate'>Shotlist has %d validation error(s): %s</div>"
                   % (len(errors), html.escape("; ".join(errors[:5]))))

    if data.get("rules"):
        out.append("<h2>Rules</h2><ul class='rules'>%s</ul>"
                   % "".join("<li>%s</li>" % html.escape(r) for r in data["rules"]))

    out += _look_section(project, sl, state)
    out += _filmstrip(project, sl, state)

    # references
    out.append("<h2>References</h2>")
    for kind in ("character", "location", "product", "other"):
        assets = [a for a in data.get("assets", []) if a.get("kind") == kind]
        if not assets:
            continue
        out.append("<p class='muted'>%s</p><div class='grid'>" % html.escape(kind.title()))
        for asset in assets:
            target = "asset:" + asset["id"]
            entry = project.selected_entry(target, state)
            path = project.selected(target, state)
            out.append("<div class='card'>%s<div class='body'><div class='id'>%s</div>"
                       "<div class='muted'>%s</div>%s</div></div>" % (
                           _img(project, path, asset["id"], "not generated"),
                           html.escape(asset["id"]),
                           html.escape("v%d" % entry["v"] if entry else "missing"),
                           _details("prompt", asset.get("prompt"))))
        out.append("</div>")
    for char in data.get("characters", []):
        ident = state["identities"].get("character:" + char["name"])
        voice = state["identities"].get("voice:" + char["name"])
        out.append("<p class='muted'>Identity %s: character %s, voice %s</p>" % (
            html.escape(char["name"]), html.escape(ident["id"] if ident else "not created"),
            html.escape(voice["id"] if voice else ("not created" if char.get("voice") else "none"))))

    # timeline
    out.append("<h2>Timeline</h2>")
    for shot in data.get("shots", []):
        sid = shot.get("id", "?")
        src = shot.get("source", "?")
        panel = project.selected("storyboard:" + sid, state) if src == "ai" else None
        label = {"ai": "AI", "real": "REAL FOOTAGE", "mg": "MOTION GRAPHIC"}.get(src, src)
        ph = {"real": "Real footage (shot on location)", "mg": "Motion graphic (made in the edit)"}.get(
            src, "storyboard panel not generated")
        out.append("<div class='shot'><div class='thumb'>%s</div><div>" % _img(project, panel, sid, ph))
        out.append("<h3>%s · %s <span class='src-%s'>%s</span></h3>" % (
            html.escape(sid), html.escape(shot.get("beat", "")), html.escape(src), html.escape(label)))
        chips = [shot.get("time", "")]
        info = shot_video.get(sid)
        if src == "ai":
            chips.append("mode: %s" % shot.get("mode"))
            if info and info["duration"] is not None:
                chips.append("%ss clip" % info["duration"])
            if info and info["cost"] is not None:
                chips.append("%g credits" % info["cost"])
            if info:
                chips.append("gate: %s" % info["gate"])
            if shot.get("characters"):
                chips.append("cast: %s" % ", ".join(shot["characters"]))
        out.append("<div class='meta'>%s</div>" % "".join(
            "<span class='chip'>%s</span>" % html.escape(str(c)) for c in chips if c))
        out.append("<p class='line'>%s</p>" % html.escape(shot.get("summary", "")))
        if shot.get("vo"):
            out.append("<p class='line'><b>VO:</b> %s</p>" % html.escape(shot["vo"]))
        if shot.get("dialogue") and shot.get("dialogue") != shot.get("vo"):
            out.append("<p class='line'><b>On-camera line:</b> %s</p>" % html.escape(shot["dialogue"]))
        if shot.get("on_screen_text"):
            out.append("<p class='line'><b>On screen:</b> %s</p>" % html.escape(shot["on_screen_text"]))
        if shot.get("notes"):
            out.append("<p class='line muted'>%s</p>" % html.escape(shot["notes"]))
        if info and info["note"]:
            out.append("<p class='line muted'>Not ready for video: %s</p>" % html.escape(info["note"]))
        if src == "ai":
            figs = []
            first_target = sl.normalize_ref("first:" + sid)[1]
            first = project.selected(first_target, state)
            if first_target != "storyboard:" + sid or shot.get("mode") == "frames":
                figs.append(("first frame" + (" (= panel)" if first_target.startswith("storyboard") else ""), first))
            if shot.get("last_frame"):
                figs.append(("last frame", project.selected("last:" + sid, state)))
            clip = project.selected("clip:" + sid, state)
            if figs or clip:
                out.append("<div class='frames'>")
                for caption, path in figs:
                    out.append("<figure>%s<figcaption>%s</figcaption></figure>"
                               % (_img(project, path, caption, "missing"), html.escape(caption)))
                if clip:
                    out.append("<figure><video controls preload='metadata' src='%s'></video>"
                               "<figcaption>clip %s</figcaption></figure>"
                               % (_src(project, clip), html.escape(project.rel(clip))))
                out.append("</div>")
            out.append(_details("storyboard prompt", (shot.get("storyboard") or {}).get("prompt")))
            out.append(_details("video prompt", sl.video_prompt(shot)))
        out.append("</div></div>")

    if warnings:
        out.append("<h2>Warnings</h2><ul class='rules'>%s</ul>"
                   % "".join("<li>%s</li>" % html.escape(w) for w in warnings))
    out.append("</main></body></html>")

    name = "Board_%s.html" % (data.get("project") or project.name)
    path = project.path / name
    path.write_text("\n".join(out), encoding="utf-8")
    return path
