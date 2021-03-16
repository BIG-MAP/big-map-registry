import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent.parent.resolve()


@pytest.fixture
def apps_schema():
    return json.loads(ROOT.joinpath("schemas/apps.schema.json").read_text())


@pytest.fixture
def apps_meta_schema():
    return json.loads(ROOT.joinpath("schemas/apps_meta.schema.json").read_text())


@pytest.fixture
def categories_schema():
    return json.loads(ROOT.joinpath("schemas/categories.schema.json").read_text())


@pytest.fixture
def metadata_schema():
    return json.loads(ROOT.joinpath("schemas/metadata.schema.json").read_text())


@pytest.fixture
def mock_schema_endpoints(
    requests_mock, apps_schema, apps_meta_schema, categories_schema, metadata_schema
):
    requests_mock.get(
        "https://big-map.github.io/big-map-registry/schemas/v1/apps.schema.json",
        text=json.dumps(apps_schema),
    )
    requests_mock.get(
        "https://big-map.github.io/big-map-registry/schemas/v1/metadata.schema.json",
        text=json.dumps(metadata_schema),
    )
    requests_mock.get(
        "https://big-map.github.io/big-map-registry/schemas/v1/apps_meta.schema.json",
        text=json.dumps(apps_meta_schema),
    )
    requests_mock.get(
        "https://big-map.github.io/big-map-registry/schemas/v1/categories.schema.json",
        text=json.dumps(categories_schema),
    )
