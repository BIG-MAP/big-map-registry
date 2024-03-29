# -*- coding: utf-8 -*-
"""Manage a registry of applications."""

from .core import AppRegistryData
from .core import AppRegistrySchemas
from .metadata import generate_apps_meta
from .version import __version__
from .web import build_from_config
from .web import build_html
from .web import write_schemas


__all__ = [
    "AppRegistryData",
    "AppRegistrySchemas",
    "__version__",
    "build_from_config",
    "build_html",
    "generate_apps_meta",
    "write_schemas",
]
