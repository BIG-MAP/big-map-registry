# -*- coding: utf-8 -*-

import pytest
import base64
from dataclasses import dataclass

import requests

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
def app_logo_img():
    """A one-pixel large 'logo' for the test app."""
    return base64.b64decode(b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAQMAAAAl21bKAAAAA1BMVEX/TQBcNTh/AAAAAXRSTlPM0jRW/QAAAApJREFUeJxjYgAAAAYAAzY3fKgAAAAASUVORK5CYII=')


@pytest.fixture
def app_logo(requests_mock, app_logo_url, app_logo_img):

    @dataclass
    class AppLogo:
        url = app_logo_url
        img = app_logo_img

    requests_mock.get(app_logo_url, content=app_logo_img)
    return AppLogo


@pytest.fixture
def app_metadata(requests_mock, app_logo):
    """Create metadata content for a test app."""
    return {
        "description": "A test app that does not really exist.",
        "title": "Test App",
        "version": "1.0.0",
        "authors": "big-map",
        "logo": app_logo.url,
        "state": "development"
    }


@pytest.fixture
def apps_yaml(requests_mock, app_git_url, app_metadata):
    """Create apps.yaml content with one test app entry."""
    apps_yaml = {
        "test": {
            "git_url": app_git_url,
            "metadata": app_metadata,
            "categories": ["utilities"]
        }
    }
    requests_mock.get(app_git_url)
    yield apps_yaml


@pytest.fixture
def categories_yaml():
    """Create categories.yaml content."""
    return {
        "utilities": {
           "title": "Utilities",
           "description": "Utility apps for everyday tasks."
        }
    }


@pytest.mark.usefixtures('mock_schema_endpoints')
def test_generate_apps_meta(apps_yaml, categories_yaml):
    apps_meta = make_pages.generate_apps_meta(apps_yaml, categories_yaml)
    # Very basic validation here, the apps_meta.json file is already validated via the schema:
    assert 'apps' in apps_meta
    assert 'categories' in apps_meta

    # Check that the test app metadata is present.
    assert 'test' in apps_meta['apps']
    assert apps_meta['apps']['test']['git_url'] == apps_yaml['test']['git_url']
    assert all(cat in apps_meta['categories'] for cat in apps_meta['apps']['test']['categories'])


@pytest.mark.usefixtures('mock_schema_endpoints')
def test_get_logo_url(apps_yaml, categories_yaml, app_logo_url):
    """Test whether the logo url is correctly resolved."""
    apps_meta = make_pages.generate_apps_meta(apps_yaml, categories_yaml)
    assert apps_meta['apps']['test']['logo'] == app_logo_url
    r = requests.get(app_logo_url)
    assert r.status_code == 200
