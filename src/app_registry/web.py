import codecs
import json
import logging
import shutil
from collections.abc import Mapping
from copy import deepcopy
from dataclasses import asdict
from functools import singledispatch
from pathlib import Path
from typing import Union

from jinja2 import Environment
from jinja2 import PackageLoader
from jinja2 import select_autoescape

from . import yaml
from .config import Config
from .core import AppRegistryData
from .core import AppRegistrySchemas
from .metadata import generate_apps_meta
from .util import load_json


logger = logging.getLogger(__name__)


def build_html(apps_meta, dest):
    # Create dest directory if needed
    dest.mkdir(parents=True, exist_ok=True)

    # Load template environment
    env = Environment(
        loader=PackageLoader("mod"),
        autoescape=select_autoescape(["html", "xml"]),
    )
    singlepage_template = env.get_template("singlepage.html")
    main_index_template = env.get_template("main_index.html")

    # Make single-entry page based on singlepage.html
    logger.info("[apps]")
    dest.joinpath("apps").mkdir()
    for app_name, app_data in apps_meta["apps"].items():
        subpage_name = app_data["subpage"]
        subpage_abspath = dest / subpage_name

        app_html = singlepage_template.render(
            category_map=apps_meta["categories"], **app_data
        )
        with codecs.open(subpage_abspath, "w", "utf-8") as f:
            f.write(app_html)
        logger.info(f"  - {subpage_name}")

    # Make index page based on main_index.html
    logger.info("[main index]")
    rendered = main_index_template.render(**apps_meta)
    outfile = dest / "index.html"
    outfile.write_text(rendered, encoding="utf-8")
    logger.info(f"  - {outfile.relative_to(dest)}")

    # Save json data for the app manager
    outfile = dest / "apps_meta.json"
    rendered = json.dumps(deepcopy(apps_meta), ensure_ascii=False, indent=2)
    outfile.write_text(rendered, encoding="utf-8")
    logger.info(f"  - {outfile.relative_to(dest)}")


def write_schemas(schemas, dest):
    """Serialize and write schemas to path."""
    logger.info("[schemas]")
    dest.mkdir(parents=True, exist_ok=True)
    for name, schema in asdict(schemas).items():
        schema_path = dest / f"{name}.schema.json"
        logger.info(f"  - {schema_path.relative_to(dest)}")
        schema_path.write_text(json.dumps(schema, indent=2))


@singledispatch
def build_from_config(config: Config):
    # Parse the apps and categories data from the paths given in the configuration.
    data = AppRegistryData(
        apps=yaml.load(Path(config.data.apps)),
        categories=yaml.load(Path(config.data.categories)),
    )
    # Parse the schemas from paths given in the configuration.
    schemas = AppRegistrySchemas(
        apps=load_json(Path(config.schemas.apps)),
        categories=load_json(Path(config.schemas.categories)),
        apps_meta=load_json(Path(config.schemas.apps_meta)),
    )

    # Generate the aggregated apps metadata registry.
    apps_meta = generate_apps_meta(data=data, schema=schemas.apps_meta)

    # Remove previous build (if present).

    shutil.rmtree(Path(config.build.html), ignore_errors=True)
    # Copy static data (if configured).
    if config.build.static_src:
        shutil.copytree(config.build.static_src, Path(config.build.html) / "static")

    # Build the html pages.
    build_html(apps_meta, dest=Path(config.build.html))

    # Write-out JSON-schema files.
    write_schemas(schemas=schemas, dest=Path(config.build.schemas))


@build_from_config.register
def _(config: Mapping):
    build_from_config(Config.from_mapping(config))


@build_from_config.register(str)
@build_from_config.register(Path)
def _(config: Union[str, Path]):
    build_from_config(Config.from_path(config))
