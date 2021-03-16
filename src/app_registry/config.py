from pathlib import Path
from typing import Union
from dataclasses import dataclass
from dataclasses import field
from collections.abc import Mapping

from dacite import from_dict

from . import yaml


API_VERSION = "v1"


@dataclass
class DataConfig:
    apps: str
    categories: str


@dataclass
class SchemasConfig:
    apps: str
    categories: str
    apps_meta: str


@dataclass
class BuildConfig:
    html: str = "./html"
    schemas: str = None
    schema_version: str = "v1"
    static_src: str = None

    def __post_init__(self):
        if self.schemas is None:
            self.schemas = str(Path(self.html) / "schemas" / self.schema_version)


@dataclass
class Config:
    data: DataConfig
    schemas: SchemasConfig
    build: BuildConfig = field(default_factory=BuildConfig)
    api_version: str = "v1"

    @classmethod
    def from_mapping(cls, config_mapping: Mapping):
        _check_api_version(config_mapping.get("api_version"))
        return from_dict(data_class=cls, data=config_mapping)

    @classmethod
    def from_path(cls, config_path: Union[Path, str]):
        config_yaml = yaml.load(config_path)
        return cls.from_mapping(config_yaml)

    def __post_init__(self):
        _check_api_version(self.api_version)


def _check_api_version(api_version):
    if api_version is None:
        raise ValueError("No config api_version provided.")
    elif api_version != API_VERSION:
        raise RuntimeError(
            f"The config api_version ({api_version}) is not supported by this version of the app registry. Consider upgrading."
        )
