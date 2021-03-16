#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
from pathlib import Path

from app_registry import yaml
from app_registry import AppStoreData
from app_registry import AppStoreSchemas
from app_registry import generate_apps_meta
from app_registry import build_pages
from app_registry import write_schemas

logging.basicConfig(level=logging.INFO)

# paths
ROOT = Path(__file__).parent.parent.resolve()
STATIC_SRC = ROOT / "src" / "static"
BUILD_PATH = ROOT / "src" / "build/html"

app_store_data = AppStoreData(
    apps=yaml.load(ROOT.joinpath("apps.yaml")),
    categories=yaml.load(ROOT.joinpath("categories.yaml")),
)

app_store_schemas = AppStoreSchemas(
    apps=json.loads(ROOT.joinpath("schemas/apps.schema.json").read_text()),
    categories=json.loads(ROOT.joinpath("schemas/categories.schema.json").read_text()),
    apps_meta=json.loads(ROOT.joinpath("schemas/apps_meta.schema.json").read_text()),
)

app_store_data.validate(app_store_schemas)

# god class
# app_store = AppStore(data=app_store_data, schemas=app_store_schemas)

# god class from assumed file layout:
# The root argument defaults to `Path.cwd()`.
# app_store = AppStore.from_directory(root=ROOT)

# Generate the apps_meta data
apps_meta = generate_apps_meta(data=app_store_data, schema=app_store_schemas.apps_meta)

# Build the HTML pages (the apps_meta argument is optional)
build_pages(apps_meta, dest=BUILD_PATH, static_src=STATIC_SRC)
write_schemas(app_store_schemas, dest=BUILD_PATH / "schemas" / "v1")
