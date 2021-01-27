#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import json
import os
import shutil
import string
from collections import OrderedDict
from copy import deepcopy
from pathlib import Path
from urllib.parse import urlparse

from dulwich.client import get_transport_and_path_from_url
from jinja2 import Environment, PackageLoader, select_autoescape
import jsonschema

import yaml

### BEGIN configuration

# paths
ROOT = Path(__file__).parent.parent.resolve()
STATIC_PATH = ROOT / 'make_ghpages' / 'static'
BUILD_PATH = ROOT / 'make_ghpages' / 'out'

# configuration
TIMEOUT_SECONDS = 30
### END configuration


def get_html_app_fname(app_name):
    valid_characters = set(string.ascii_letters + string.digits + '_-')

    simple_string = "".join(c for c in app_name if c in valid_characters)

    return f"{simple_string}.html"


def get_hosted_on(url):
    netloc = urlparse(url).netloc

    # Remove port (if any)
    netloc = netloc.partition(':')[0]

    # Remove subdomains (this only works for domain suffixes of length 1!)
    # TODO: fix it for domains like yyy.co.uk
    netloc = ".".join(netloc.split('.')[-2:])

    return netloc


def get_git_branches(git_url):
    t, p = get_transport_and_path_from_url(git_url)
    branches = t.get_refs(p)
    res = {}
    for key, value in branches.items():
        res[key.decode("utf-8")] = value.decode("utf-8")
    return res


def get_git_author(git_url):
    return urlparse(git_url).path.split('/')[1]


def complete_metadata(app_name, metadata, git_url):
    metadata.setdefault('state', 'registered')
    metadata.setdefault('title', app_name)
    if git_url:
        metadata.setdefault('authors', get_git_author(git_url))
    return metadata


def fetch_app_data(app_data, app_name):
    # Get Git URL, fail build if git_url is not found or wrong
    git_url = app_data.get('git_url', '')
    hosted_on = get_hosted_on(git_url) if git_url else None

    # Check if categories are specified, warn if not
    if 'categories' not in app_data:
        print("  >> WARNING: No categories specified.")

    app_data['metadata'] = complete_metadata(app_name, app_data['metadata'], git_url)
    if git_url:
        app_data['gitinfo'] = get_git_branches(git_url)
    if hosted_on:
        app_data['hosted_on'] = hosted_on

    # Get logo URL, if it has been specified
    if 'logo' in app_data['metadata']:
        app_data['logo'] = app_data['metadata']['logo']

    return app_data


def validate_apps_meta(apps_meta):
    apps_meta_schema = json.loads(ROOT.joinpath('schemas/apps_meta.schema.json').read_text())
    jsonschema.validate(instance=apps_meta, schema=apps_meta_schema)

    for app, appdata in apps_meta['apps'].items():
        for category in appdata['categories']:
            assert category in apps_meta['categories']


def generate_apps_meta(apps_data, categories_data):
    apps_meta = {
        'apps': OrderedDict(),
        'categories': categories_data,
    }
    print("Fetching app data...")
    for app_name in sorted(apps_data.keys()):
        print(f"  - {app_name}")
        app_data = fetch_app_data(apps_data[app_name], app_name)
        app_data['name'] = app_name
        app_data['subpage'] = os.path.join('apps', get_html_app_fname(app_name))
        apps_meta['apps'][app_name] = app_data

    validate_apps_meta(apps_meta)
    return apps_meta


def build_pages(apps_meta):
    # Validate input data
    validate_apps_meta(apps_meta)

    # Create output folder, copy static files
    if BUILD_PATH.exists():
        shutil.rmtree(BUILD_PATH)
    shutil.copytree(STATIC_PATH, BUILD_PATH / 'static')

    # Load template environment
    env = Environment(
        loader=PackageLoader('mod'),
        autoescape=select_autoescape(['html', 'xml']),
    )
    singlepage_template = env.get_template("singlepage.html")
    main_index_template = env.get_template("main_index.html")

    # Make single-entry page based on singlepage.html
    print("[apps]")
    BUILD_PATH.joinpath('apps').mkdir()
    for app_name, app_data in apps_meta['apps'].items():
        subpage_name = app_data['subpage']
        subpage_abspath = BUILD_PATH / subpage_name

        app_html = singlepage_template.render(category_map=apps_meta['categories'], **app_data)
        with codecs.open(subpage_abspath, 'w', 'utf-8') as f:
            f.write(app_html)
        print(f"  - {subpage_name}")

    # Make index page based on main_index.html
    print("[main index]")
    rendered = main_index_template.render(**apps_meta)
    outfile = BUILD_PATH / 'index.html'
    outfile.write_text(rendered, encoding='utf-8')
    print(f"  - {outfile.relative_to(BUILD_PATH)}")

    # Save json data for the app manager
    outfile = BUILD_PATH / 'apps_meta.json'
    rendered = json.dumps(deepcopy(apps_meta), ensure_ascii=False, indent=2)
    outfile.write_text(rendered, encoding='utf-8')
    print(f"  - {outfile.relative_to(BUILD_PATH)}")

    # Copy schemas
    print("[schemas/v1]")
    schemas_outdir = BUILD_PATH / 'schemas' / 'v1'
    schemas_outdir.mkdir(parents=True)
    for schemafile in ROOT.glob('schemas/*.schema.json'):
        shutil.copyfile(schemafile, schemas_outdir / schemafile.name)
        print(f"  - {schemas_outdir.relative_to(BUILD_PATH)}/{schemafile.name}")


if __name__ == '__main__':
    # Get apps.yaml raw data and validate against schema
    apps_data = yaml.load(ROOT.joinpath('apps.yaml'))
    apps_schema = json.loads(ROOT.joinpath('schemas/apps.schema.json').read_text())
    jsonschema.validate(instance=apps_data, schema=apps_schema)

    # Get categories.yaml raw data and validate against schema
    categories_data = yaml.load(ROOT.joinpath('categories.yaml'))
    categories_schema = json.loads(ROOT.joinpath('schemas/categories.schema.json').read_text())
    jsonschema.validate(instance=categories_data, schema=categories_schema)

    # Generate the apps_meta data
    apps_meta = generate_apps_meta(apps_data, categories_data)

    # Build the HTML pages
    build_pages(apps_meta)
