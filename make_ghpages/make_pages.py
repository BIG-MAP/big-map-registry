#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import json
import os
import shutil
import string
from collections import OrderedDict
from pathlib import Path
from urllib.parse import urlparse, urlunparse
import exceptions as exc

## Requires jinja2 >= 2.9
from jinja2 import Environment, PackageLoader, select_autoescape
import cachecontrol
import jsonschema
import requests

### BEGIN configuration

REQUESTS = cachecontrol.CacheControl(requests.Session())

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
    try:
        REQUESTS.get(url, timeout=TIMEOUT_SECONDS).raise_for_status()
    except requests.RequestException:
        raise exc.MissingGit(f"Value for 'git_url' in apps.json may be wrong: {url!r}")

    netloc = urlparse(url).netloc

    # Remove port (if any)
    netloc = netloc.partition(':')[0]

    # Remove subdomains (this only works for domain suffixes of length 1!)
    # TODO: fix it for domains like yyy.co.uk
    netloc = ".".join(netloc.split('.')[-2:])

    return netloc


def fetch_meta_info(json_url):
    try:
        response = REQUESTS.get(json_url, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        raise exc.MissingMetadata(f"Value for 'meta_url' in apps.json may be wrong: {json_url!r}")
    except json.decoder.JSONDecodeError:
        raise exc.WrongMetadata("The apps' metadata is not valid JSON.")


def get_git_branches(git_url):
    from dulwich.client import get_transport_and_path_from_url
    t, p = get_transport_and_path_from_url(git_url)
    branches = t.get_refs(p)
    res = {}
    for key, value in branches.items():
        res[key.decode("utf-8")] = value.decode("utf-8")
    return res


def get_git_author(git_url):
    return urlparse(git_url).path.split('/')[1]


def complete_meta_info(app_name, meta_info, git_url):
    meta_info.setdefault('state', 'registered')
    meta_info.setdefault('title', app_name)
    if git_url:
        meta_info.setdefault('authors', get_git_author(git_url))
    return meta_info


def get_logo_url(logo_url, meta_url):
    logo_url_parsed = urlparse(logo_url)
    if logo_url_parsed.netloc:
        return logo_url  # logo url is already fully qualified

    elif meta_url:
        # Otherwise, assume that path is relative to the metadata file's
        # parent directory:
        meta_url_parsed = urlparse(meta_url)
        path = Path(meta_url_parsed.path).parent.joinpath(logo_url_parsed.path)
        return urlunparse(meta_url_parsed._replace(path=str(path)))

    raise exc.MissingLogo(f"The logo path must be a fully qualified url if no metadata_url is provided: {logo_url!r}")


def check_logo_url(logo_url):
    try:
        REQUESTS.get(logo_url, timeout=TIMEOUT_SECONDS).raise_for_status()
    except requests.RequestException:
        raise exc.MissingLogo(f"Unable to fetch logo from {logo_url!r}!")


def fetch_app_data(app_data, app_name):
    # Get Git URL, fail build if git_url is not found or wrong
    git_url = app_data.get('git_url', '')
    hosted_on = get_hosted_on(git_url) if git_url else None

    # Get metadata.json from the project;
    # fail build if meta_url is not found or wrong
    try:
        try:
            meta_info = app_data['metadata']
        except KeyError:
            meta_info = fetch_meta_info(app_data['meta_url'])
    except KeyError:
        raise exc.MissingMetadata(f"Unable to get metadata for {app_name!r}, neither 'metadata' nor 'meta_url' key provided in apps.json.")

    # Check if categories are specified, warn if not
    if 'categories' not in app_data:
        print("  >> WARNING: No categories specified.")

    app_data['metadata'] = complete_meta_info(app_name, meta_info, git_url)
    if git_url:
        app_data['gitinfo'] = get_git_branches(git_url)
    if hosted_on:
        app_data['hosted_on'] = hosted_on

    # Get logo URL, if it has been specified
    if 'logo' in app_data['metadata']:
        app_data['logo'] = get_logo_url(app_data['metadata']['logo'], app_data.get('meta_url'))

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
        if 'logo' in app_data:
            check_logo_url(app_data['logo'])
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
    rendered = json.dumps(apps_meta, ensure_ascii=False, indent=2)
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
    # Get apps.json raw data and validate against schema
    apps_data = json.loads(ROOT.joinpath('apps.json').read_text())
    apps_schema = json.loads(ROOT.joinpath('schemas/apps.schema.json').read_text())
    jsonschema.validate(instance=apps_data, schema=apps_schema)

    # Get categories.json raw data and validate against schema
    categories_data = json.loads(ROOT.joinpath('categories.json').read_text())
    categories_schema = json.loads(ROOT.joinpath('schemas/categories.schema.json').read_text())
    jsonschema.validate(instance=categories_data, schema=categories_schema)

    # Generate the apps_meta data
    apps_meta = generate_apps_meta(apps_data, categories_data)

    # Build the HTML pages
    build_pages(apps_meta)
