import codecs
import json
import logging
import os
import shutil
import string
from collections import OrderedDict
from copy import deepcopy
from dataclasses import asdict
from dataclasses import dataclass
from urllib.parse import urlparse

from dulwich.client import get_transport_and_path_from_url
from jinja2 import Environment, PackageLoader, select_autoescape
import jsonschema


logger = logging.getLogger(__name__)


def get_html_app_fname(app_name):
    valid_characters = set(string.ascii_letters + string.digits + "_-")

    simple_string = "".join(c for c in app_name if c in valid_characters)

    return f"{simple_string}.html"


def get_hosted_on(url):
    netloc = urlparse(url).netloc

    # Remove port (if any)
    netloc = netloc.partition(":")[0]

    # Remove subdomains (this only works for domain suffixes of length 1!)
    # TODO: fix it for domains like yyy.co.uk
    netloc = ".".join(netloc.split(".")[-2:])

    return netloc


def get_git_branches(git_url):
    t, p = get_transport_and_path_from_url(git_url)
    branches = t.get_refs(p)
    res = {}
    for key, value in branches.items():
        res[key.decode("utf-8")] = value.decode("utf-8")
    return res


def get_git_author(git_url):
    return urlparse(git_url).path.split("/")[1]


def complete_metadata(app_name, metadata, git_url):
    metadata.setdefault("state", "registered")
    metadata.setdefault("title", app_name)
    if git_url:
        metadata.setdefault("authors", get_git_author(git_url))
    return metadata


def fetch_app_data(app_data, app_name):
    # Get Git URL, fail build if git_url is not found or wrong
    git_url = app_data.get("git_url", "")
    hosted_on = get_hosted_on(git_url) if git_url else None

    # Check if categories are specified, warn if not
    if "categories" not in app_data:
        logger.info("  >> WARNING: No categories specified.")

    app_data["metadata"] = complete_metadata(app_name, app_data["metadata"], git_url)
    if git_url:
        app_data["gitinfo"] = get_git_branches(git_url)
    if hosted_on:
        app_data["hosted_on"] = hosted_on

    # Get logo URL, if it has been specified
    if "logo" in app_data["metadata"]:
        app_data["logo"] = app_data["metadata"]["logo"]

    return app_data


def validate_apps_meta(apps_meta, apps_meta_schema):
    jsonschema.validate(instance=apps_meta, schema=apps_meta_schema)

    for app, appdata in apps_meta["apps"].items():
        for category in appdata["categories"]:
            assert category in apps_meta["categories"]


def generate_apps_meta(data, schema):
    apps_meta = {
        "apps": OrderedDict(),
        "categories": data.categories,
    }
    logger.info("Fetching app data...")
    for app_name in sorted(data.apps.keys()):
        logger.info(f"  - {app_name}")
        app_data = fetch_app_data(data.apps[app_name], app_name)
        app_data["name"] = app_name
        app_data["subpage"] = os.path.join("apps", get_html_app_fname(app_name))
        apps_meta["apps"][app_name] = app_data

    validate_apps_meta(apps_meta, schema)
    return apps_meta


def build_html(apps_meta, dest, static_src):
    # Create output folder, copy static files
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(static_src, dest / "static")

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


@dataclass
class AppStoreSchemas:

    apps: dict
    categories: dict
    apps_meta: dict


@dataclass
class AppStoreData:

    apps: dict
    categories: dict

    def validate(self, schemas: AppStoreSchemas):
        jsonschema.validate(instance=self.apps, schema=schemas.apps)
        jsonschema.validate(instance=self.categories, schema=schemas.categories)


class AppStore:
    def __init__(self, data: AppStoreData, schemas: AppStoreSchemas):
        self.data = data
        self.schemas = schemas
        self.data.validate(self.schemas)

    @classmethod
    def from_directory(cls, root):
        raise NotImplementedError()

    def build_html(self, out, static, apps_meta=None):
        raise NotImplementedError()
