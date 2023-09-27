# -*- coding: utf-8 -*-
"""Generate the aggregated registry metadata from the registry data."""

import logging
import os
from collections import OrderedDict

import jsonschema

from . import util


logger = logging.getLogger(__name__)


def complete_metadata(app_name, metadata, git_url):
    """Fill-in any missing data for a given app metadata."""

    metadata.setdefault("state", "registered")
    metadata.setdefault("title", app_name)
    # metadata.setdefault("affiliations", "not available")
    if git_url:
        metadata.setdefault("authors", util.get_git_author(git_url))
    return metadata


def fetch_app_data(app_data, app_name):
    """Fetch additional data for the given app data."""

    # Get Git URL, fail build if git_url is not found or wrong
    git_url = app_data.get("git_url", "")
    hosted_on = util.get_hosted_on(git_url) if git_url else None

    # Check if categories are specified, warn if not
    if "categories" not in app_data:
        logger.info("  >> WARNING: No categories specified.")

    app_data["metadata"] = complete_metadata(app_name, app_data["metadata"], git_url)
    if git_url:
        app_data["gitinfo"] = util.get_git_branches(git_url)
    if hosted_on:
        app_data["hosted_on"] = hosted_on

    # Get logo URL, if it has been specified
    if "logo" in app_data["metadata"]:
        app_data["logo"] = app_data["metadata"]["logo"]

    return app_data


def validate_apps_meta(apps_meta, apps_meta_schema):
    """Validate the apps_meta file against the corresponding JSON-schema."""

    jsonschema.validate(instance=apps_meta, schema=apps_meta_schema)

    for app, appdata in apps_meta["apps"].items():
        for category in appdata["categories"]:
            assert category in apps_meta["categories"]


def generate_apps_meta(data, schema=None):
    """Generate (and optionally validate) the comprehensive app registry metadata.

    This function produces the apps_meta file, a comprehensive metadata directory that
    combines the apps data and additionally fetched data (such as the git info).

    The apps_meta file can be used to generate the app registery website and if
    published online, by other platforms that want to operate on the app registry
    and, e.g., integrate with registered apps.
    """

    apps_meta = {
        "apps": OrderedDict(),
        "categories": data.categories,
    }
    logger.info("Fetching app data...")
    for app_name in sorted(data.apps.keys()):
        logger.info(f"  - {app_name}")
        app_data = fetch_app_data(data.apps[app_name], app_name)
        app_data["name"] = app_name
        app_data["subpage"] = os.path.join("apps", util.get_html_app_fname(app_name))
        apps_meta["apps"][app_name] = app_data

    if schema:
        validate_apps_meta(apps_meta, schema)

    return apps_meta
