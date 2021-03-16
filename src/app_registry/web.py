import codecs
import json
import logging
import shutil
from copy import deepcopy
from dataclasses import asdict

from jinja2 import Environment
from jinja2 import PackageLoader
from jinja2 import select_autoescape


logger = logging.getLogger(__name__)


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
