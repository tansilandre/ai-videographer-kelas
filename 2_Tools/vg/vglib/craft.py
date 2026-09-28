"""Craft checks on the shot plan: every shot can carry a category, a camera move and a shot size from
fixed lists (1_Skills/vg-video-prompt/references/shot-categories.md and camera-moves.md), and a hook
can make a promise that a later shot pays off. `vg validate` warns about the patterns that made the
first test reel read as stitched AI clips. Warnings, not errors: taste stays with the human."""
import re

CATEGORIES = ("hook_talking", "hook_visual", "talking_cta", "walk_talk", "lifestyle_broll", "room_reveal",
              "threshold_reveal", "view_reveal", "detail_insert", "aerial_establish", "concept_render",
              "transition", "photo_move", "graphic")
PRODUCT_CATEGORIES = ("room_reveal", "threshold_reveal", "view_reveal", "detail_insert", "photo_move")
CAMERAS = ("static", "handheld", "selfie_follow", "friend_follow", "push_in", "pull_out", "lateral_glide", "pan",
           "tilt_up", "arc", "crane_up", "threshold_walk", "window_approach", "drone_approach", "drone_rise",
           "top_down", "hyperlapse", "focus_pull")
SIZES = ("ecu", "cu", "mcu", "ms", "mws", "ws", "ews")


def seconds(time_label):
    """Length of a `time` window such as "3-8s" (None when it can't be read)."""
    m = re.match(r"^\s*([\d.]+)\s*-\s*([\d.]+)\s*s?\s*$", str(time_label or ""))
    return max(0.0, float(m.group(2)) - float(m.group(1))) if m else None


def check(data):
    """(warnings, todos) for the shot list `data`."""
    shots = [s for s in data.get("shots", []) if isinstance(s, dict) and s.get("id")]
    warnings, todos = [], []
    for shot in shots:
        where = "shots.%s" % shot["id"]
        for field, allowed, what in (("category", CATEGORIES, "category"), ("camera", CAMERAS, "camera move"),
                                     ("size", SIZES, "shot size")):
            value = shot.get(field)
            if value is not None and value not in allowed:
                warnings.append("%s.%s: %r is not a known %s (%s)" % (where, field, value, what, ", ".join(allowed)))
    if any(s.get("source") == "ai" and not s.get("category") for s in shots):
        todos.append("shots: give every shot a category, camera and size (vg-video-prompt/references/"
                     "shot-categories.md) so vg validate can check pacing, payoff and screen time")

    by_id = {s["id"]: s for s in shots}
    paid = {s.get("pays_off") for s in shots if s.get("pays_off")}
    for shot in shots:
        if (shot.get("promise") or "").strip() and shot["id"] not in paid:
            warnings.append("shots.%s.promise: no shot pays it off; add \"pays_off\": \"%s\" to the shot that "
                            "shows it" % (shot["id"], shot["id"]))
        target = shot.get("pays_off")
        if target and not (by_id.get(target) or {}).get("promise"):
            warnings.append("shots.%s.pays_off: %s has no promise (or is not a shot)" % (shot["id"], target))

    target_share = (data.get("format") or {}).get("product_share_min")
    if target_share and any(s.get("category") for s in shots):
        total = sum(seconds(s.get("time")) or 0 for s in shots)
        product = sum(seconds(s.get("time")) or 0 for s in shots if s.get("category") in PRODUCT_CATEGORIES)
        if total and product / total < float(target_share):
            warnings.append("the product holds %d%% of screen time (target %d%%): give the property more shots or "
                            "longer ones" % (round(100 * product / total), round(100 * float(target_share))))

    for i in range(len(shots) - 2):
        run = shots[i:i + 3]
        keys = [(s.get("size"), s.get("camera")) for s in run]
        if all(k[0] and k[1] for k in keys) and keys[0] == keys[1] == keys[2]:
            warnings.append("%s: three cuts in a row with the same size and camera move (%s, %s); vary one of them"
                            % (", ".join(s["id"] for s in run), keys[0][0], keys[0][1]))
    return warnings, todos
