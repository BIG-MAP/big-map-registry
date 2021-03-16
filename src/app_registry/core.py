from dataclasses import dataclass

import jsonschema


@dataclass
class AppRegistrySchemas:

    apps: dict
    categories: dict
    apps_meta: dict


@dataclass
class AppRegistryData:

    apps: dict
    categories: dict

    def validate(self, schemas: AppRegistrySchemas):
        jsonschema.validate(instance=self.apps, schema=schemas.apps)
        jsonschema.validate(instance=self.categories, schema=schemas.categories)


class AppRegistry:
    def __init__(self, data: AppRegistryData, schemas: AppRegistrySchemas):
        self.data = data
        self.schemas = schemas
        self.data.validate(self.schemas)

    @classmethod
    def from_directory(cls, root):
        raise NotImplementedError()

    def build_html(self, out, static, apps_meta=None):
        raise NotImplementedError()
