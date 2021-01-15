# -*- coding: utf-8 -*-

import pytest
import os
import json
import base64
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import requests

import exceptions
import make_pages


@pytest.fixture
def app_git_url():
    return "https://github.com/aiidalab/aiidalab-hello-world.git"


@pytest.fixture
def app_metadata_url():
    """A URL for the test app metadata."""
    return "https://raw.githubusercontent.com/aiidalab/aiidalab-hello-world/master/metadata.json"


@pytest.fixture
def app_logo_url():
    """A URL for the test app logo."""
    return "https://raw.githubusercontent.com/aiidalab/aiidalab-hello-world/master/img/logo.png"

@pytest.fixture
def app_logo():
    """A one-pixel large 'logo' for the test app."""
    return base64.b64decode(b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAQMAAAAl21bKAAAAA1BMVEX/TQBcNTh/AAAAAXRSTlPM0jRW/QAAAApJREFUeJxjYgAAAAYAAzY3fKgAAAAASUVORK5CYII=')


@pytest.fixture
def app_metadata_json():
    """Create metadata.json content for a test app."""
    return {
        "description": "A test app that does not really exist.",
        "title": "Test App",
        "version": "1.0.0",
        "authors": "big-map",
        "logo": "img/logo.png",
        "state": "development"
    }


@pytest.fixture
def apps_json(requests_mock, app_git_url, app_metadata_url, app_metadata_json, app_logo, app_logo_url):
    """Create apps.json content with one test app entry."""
    apps_json = {
        "test": {
            "git_url": app_git_url,
            "meta_url": app_metadata_url,
            "categories": ["utilities"]
        }
    }
    requests_mock.get(app_git_url)
    requests_mock.get(app_metadata_url, text=json.dumps(app_metadata_json))
    requests_mock.get(app_logo_url, content=app_logo)
    yield apps_json


@pytest.fixture
def categories_json():
    """Create categories.json contect for testing."""
    return {
        "utilities": {
           "title": "Utilities",
           "description": "Utility apps for everyday tasks."
        }
    }


@pytest.mark.usefixtures('mock_schema_endpoints')
def test_generate_apps_meta(apps_json, categories_json):
    apps_meta = make_pages.generate_apps_meta(apps_json, categories_json)
    # Very basic validation here, the apps_meta.json file is already validated via the schema:
    assert 'apps' in apps_meta
    assert 'categories' in apps_meta

    # Check that the test app metadata is present.
    assert 'test' in apps_meta['apps']
    assert apps_meta['apps']['test']['git_url'] == apps_json['test']['git_url']
    assert all(cat in apps_meta['categories'] for cat in apps_meta['apps']['test']['categories'])


@pytest.mark.usefixtures('mock_schema_endpoints')
def test_validate_logo(requests_mock, app_metadata_json, app_metadata_url, apps_json, categories_json):
    """Test whether exception is raised in case that logo URL location does not exist."""
    # Manipulate metadata.json endpoint to point logo to non-existant location.
    app_metadata_json['logo'] = 'path/to/file/that/does/not/exist.png'
    requests_mock.get(app_metadata_url, text=json.dumps(app_metadata_json))

    app_metadata_url_parsed = urlsplit(app_metadata_url)
    expected_logo_url = urlunsplit(app_metadata_url_parsed._replace(path=str(Path(app_metadata_url_parsed.path).parent.joinpath(app_metadata_json['logo']))))
    requests_mock.register_uri('GET', expected_logo_url, exc=requests.HTTPError)

    # Attempt to create the apps_meta.json file.
    with pytest.raises(exceptions.MissingLogo):
        apps_meta = make_pages.generate_apps_meta(apps_json, categories_json)


@pytest.mark.usefixtures('mock_schema_endpoints')
def test_get_logo_url(apps_json, categories_json, app_logo_url):
    """Test whether the logo url is correctly resolved."""
    apps_meta = make_pages.generate_apps_meta(apps_json, categories_json)
    assert apps_meta['apps']['test']['logo'] == app_logo_url
    r = requests.get(app_logo_url)
    assert r.status_code == 200
