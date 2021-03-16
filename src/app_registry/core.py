# -*- coding: utf-8 -*-
"""Core data classes for the app registry."""
from dataclasses import dataclass

import jsonschema


@dataclass
class AppRegistrySchemas:
    """The app registry JSON-schema objects."""

    apps: dict
    categories: dict
    apps_meta: dict


@dataclass
class AppRegistryData:
    """The app registry data objects (apps and categories)."""

    apps: dict
    categories: dict

    def validate(self, schemas: AppRegistrySchemas):
        """Validate the registry data against the provided registry schemas."""
        jsonschema.validate(instance=self.apps, schema=schemas.apps)
        jsonschema.validate(instance=self.categories, schema=schemas.categories)
