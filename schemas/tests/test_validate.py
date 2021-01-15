import json
from pathlib import Path
from functools import partial

import pytest
import jsonschema

ROOT = Path(__file__).parent.parent.parent.resolve()


@pytest.fixture
def validate():
    return partial(jsonschema.validate, format_checker=jsonschema.draft7_format_checker)


@pytest.fixture
def apps_schema():
    return json.loads(ROOT.joinpath('schemas/apps.schema.json').read_text())


@pytest.fixture
def apps_meta_schema():
    return json.loads(ROOT.joinpath('schemas/apps_meta.schema.json').read_text())


@pytest.fixture
def categories_schema():
    return json.loads(ROOT.joinpath('schemas/categories.schema.json').read_text())


@pytest.fixture
def metadata_schema():
    return json.loads(ROOT.joinpath('schemas/metadata.schema.json').read_text())


@pytest.fixture
def apps_json():
    return json.loads(ROOT.joinpath('apps.json').read_text())


@pytest.fixture
def categories_json():
    return json.loads(ROOT.joinpath('categories.json').read_text())


@pytest.fixture
def valid_categories(categories_json):
    return set(categories_json)


def test_validate_apps_schema(apps_schema):
    jsonschema.Draft7Validator.check_schema(apps_schema)


def test_validate_apps_meta_schema(apps_meta_schema):
    jsonschema.Draft7Validator.check_schema(apps_meta_schema)


def test_validate_categories_schema(categories_schema):
    jsonschema.Draft7Validator.check_schema(categories_schema)


def test_validate_metadata_schema(metadata_schema):
    jsonschema.Draft7Validator.check_schema(metadata_schema)


def test_validate_apps_json_schema(validate, apps_schema, apps_json, valid_categories):
    validate(instance=apps_json, schema=apps_schema)


def test_validate_apps_json_categories(apps_json, valid_categories):
    for app in apps_json.values():
        for category in app.get('categories', []):
            assert category in valid_categories


def test_validate_categories_json(validate, categories_schema, categories_json):
    validate(instance=categories_json, schema=categories_schema)
