from __future__ import annotations

import importlib
import pkgutil

from .base import PluginBase


def discover_plugins() -> list[PluginBase]:
    plugins: list[PluginBase] = []
    package = importlib.import_module("tuda.plugins")
    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        if module_name in {"base", "manager"}:
            continue
        module = importlib.import_module(f"tuda.plugins.{module_name}")
        for attr in dir(module):
            obj = getattr(module, attr)
            if isinstance(obj, type) and issubclass(obj, PluginBase) and obj is not PluginBase:
                plugins.append(obj())
    return plugins
