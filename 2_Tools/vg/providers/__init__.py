"""Providers: one module per API shape. The registry's "provider" field picks the module."""
from vglib.errors import UsageError


def get_provider(name):
    if name == "kie":
        from vglib import config
        from providers.kie import KieProvider
        return KieProvider(config.api_key("kie"))
    if name == "kie-veo":
        from vglib import config
        from providers.kie_veo import KieVeoProvider
        return KieVeoProvider(config.api_key("kie"))
    raise UsageError("Unknown provider %r. Add providers/%s.py and register it here." % (name, name))
