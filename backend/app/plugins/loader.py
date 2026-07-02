from __future__ import annotations

import importlib.util
from pathlib import Path

from app.core.logging import app_logger
from app.modules.base import SecurityModule
from app.plugins.registry import ModuleRegistry


def load_local_plugins(plugins_dir: Path, registry: ModuleRegistry) -> list[str]:
    """Load local plugin modules from disk after basic validation.

    Plugins must be local Python files defining a `register(registry)` function.
    Exodia never downloads or executes plugin code from remote locations.
    """

    loaded: list[str] = []
    if not plugins_dir.exists():
        return loaded

    for plugin_file in plugins_dir.glob("*/plugin.py"):
        if plugin_file.is_symlink():
            app_logger.warning("Skipping symlinked plugin file: {}", plugin_file)
            continue
        spec = importlib.util.spec_from_file_location(f"exodia_plugin_{plugin_file.parent.name}", plugin_file)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        register = getattr(module, "register", None)
        if not callable(register):
            app_logger.warning("Plugin {} has no register function", plugin_file)
            continue
        before = registry.ids()
        register(registry)
        after = registry.ids()
        for module_id in after - before:
            candidate = registry.require(module_id)
            if not isinstance(candidate, SecurityModule):
                raise TypeError(f"Plugin {plugin_file} registered an invalid module")
        loaded.append(plugin_file.parent.name)
    return loaded

