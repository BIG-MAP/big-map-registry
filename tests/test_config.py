import json
from pathlib import Path

import pytest
import jsonschema

import app_registry
from app_registry import yaml


ROOT = Path(__file__).parent.parent.resolve()
CONFIG_YAML = ROOT.joinpath("config.yaml")


@pytest.fixture
def config_yaml():
    return yaml.load(CONFIG_YAML)


@pytest.fixture
def config_schema():
    return json.loads(
        Path(app_registry.__file__).parent.joinpath("config.schema.json").read_text()
    )


def test_validate_config_schema(config_schema):
    jsonschema.Draft7Validator.check_schema(config_schema)


@pytest.mark.skipif(not CONFIG_YAML.exists(), reason="no config.yaml in repository")
def test_validate_config(validate, config_yaml, config_schema):
    validate(instance=config_yaml, schema=config_schema)
