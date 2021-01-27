import json
from pathlib import Path
from functools import partial

import pytest
import jsonschema

from util import load_yaml

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
def apps_yaml():
    return load_yaml(ROOT.joinpath('apps.yaml'))


@pytest.fixture
def categories_yaml():
    return load_yaml(ROOT.joinpath('categories.yaml'))


@pytest.fixture
def valid_categories(categories_yaml):
    return set(categories_yaml)


def test_validate_apps_schema(apps_schema):
    jsonschema.Draft7Validator.check_schema(apps_schema)


def test_validate_apps_meta_schema(apps_meta_schema):
    jsonschema.Draft7Validator.check_schema(apps_meta_schema)


def test_validate_categories_schema(categories_schema):
    jsonschema.Draft7Validator.check_schema(categories_schema)


def test_validate_metadata_schema(metadata_schema):
    jsonschema.Draft7Validator.check_schema(metadata_schema)


def test_validate_apps_yaml_schema(validate, apps_schema, apps_yaml, valid_categories):
    validate(instance=apps_yaml, schema=apps_schema)


def test_validate_apps_yaml_categories(apps_yaml, valid_categories):
    for app in apps_yaml.values():
        for category in app.get('categories', []):
            assert category in valid_categories


def test_validate_categories_yaml(validate, categories_schema, categories_yaml):
    validate(instance=categories_yaml, schema=categories_schema)
