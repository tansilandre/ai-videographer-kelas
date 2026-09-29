"""Model registry: loads models/*.json, validates parameters, prices requests."""
import json
import math

from vglib import config
from vglib.errors import UsageError

_models = None


def load_models():
    global _models
    if _models is None:
        _models = {}
        for path in sorted(config.MODELS_DIR.glob("*.json")):
            spec = json.loads(path.read_text(encoding="utf-8"))
            _models[spec["id"]] = spec
    return _models


def get(model_id, kind=None, allow_untested=False):
    models = load_models()
    if model_id not in models:
        raise UsageError("Unknown model %r. Known: %s" % (model_id, ", ".join(sorted(models))))
    spec = models[model_id]
    if kind and spec["kind"] != kind:
        raise UsageError("Model %r is a %s model, not %s" % (model_id, spec["kind"], kind))
    if spec.get("status") != "live-tested" and not allow_untested:
        raise UsageError(
            "Model %r is marked %r. Pass --allow-untested to use it, and check the first result "
            "carefully." % (model_id, spec.get("status"))
        )
    return spec


def default_param(spec, name):
    return (spec.get("params", {}).get(name) or {}).get("default")


def cast_param(spec, name, value):
    rule = spec.get("params", {}).get(name)
    if rule is None or value is None:
        return value
    if rule.get("type") == "integer":
        try:
            return int(value)
        except (TypeError, ValueError):
            raise UsageError("%s must be an integer for %s, got %r" % (name, spec["id"], value))
    return str(value)


def check_params(spec, params):
    """Return a list of problems with the given parameter values."""
    problems = []
    for name, value in params.items():
        rule = spec.get("params", {}).get(name)
        if rule is None or value is None:
            continue
        if "enum" in rule and value not in rule["enum"]:
            problems.append("%s=%r is not allowed for %s (allowed: %s)"
                            % (name, value, spec["id"], ", ".join(str(v) for v in rule["enum"])))
        if "min" in rule and isinstance(value, int) and value < rule["min"]:
            problems.append("%s=%r is below %s" % (name, value, rule["min"]))
        if "max" in rule and isinstance(value, int) and value > rule["max"]:
            problems.append("%s=%r is above %s" % (name, value, rule["max"]))
    for constraint in spec.get("constraints", []):
        when = constraint.get("when", {})
        if all(str(params.get(k)) == str(v) for k, v in when.items()):
            for name, bad in constraint.get("forbid", {}).items():
                if str(params.get(name)) in [str(b) for b in bad]:
                    problems.append("%s=%s cannot be combined with %s on %s"
                                    % (name, params.get(name),
                                       ", ".join("%s=%s" % kv for kv in when.items()), spec["id"]))
    return problems


def price(spec, params):
    pricing = spec.get("pricing")
    if not pricing:
        raise UsageError("Model %r has no pricing table" % spec["id"])
    node = pricing["table"]
    for key in pricing.get("keys", []):
        value = str(params.get(key))
        value = pricing.get("aliases", {}).get(key, {}).get(value, value)
        if not isinstance(node, dict) or value not in node:
            raise UsageError("No price for %s=%s on %s" % (key, value, spec["id"]))
        node = node[value]
    price = float(node)
    if pricing.get("per_second"):
        seconds = float(params.get("duration") or 0)
        if pricing.get("round_up"):  # billed per started second
            seconds = math.ceil(seconds - 1e-9)
        price *= seconds
    return round(price, 2)


def allowed_durations(spec):
    rule = spec.get("params", {}).get("duration") or {}
    return sorted(int(v) for v in rule.get("enum", []))


def dialogue_fits(spec, dialogue, duration):
    fit = spec.get("dialogue_fit")
    if not fit or not dialogue:
        return True
    return len(dialogue) <= (float(duration) - fit["lead_s"]) * fit["chars_per_second"]


def fit_duration(spec, dialogue):
    """Shortest allowed duration that holds the dialogue, or None when nothing fits."""
    for duration in allowed_durations(spec):
        if dialogue_fits(spec, dialogue, duration):
            return duration
    return None
