from dataclasses import dataclass

import jsonschema


@dataclass
class AppStoreSchemas:

    apps: dict
    categories: dict
    apps_meta: dict


@dataclass
class AppStoreData:

    apps: dict
    categories: dict

    def validate(self, schemas: AppStoreSchemas):
        jsonschema.validate(instance=self.apps, schema=schemas.apps)
        jsonschema.validate(instance=self.categories, schema=schemas.categories)


class AppStore:
    def __init__(self, data: AppStoreData, schemas: AppStoreSchemas):
        self.data = data
        self.schemas = schemas
        self.data.validate(self.schemas)

    @classmethod
    def from_directory(cls, root):
        raise NotImplementedError()

    def build_html(self, out, static, apps_meta=None):
        raise NotImplementedError()
