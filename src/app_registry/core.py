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
