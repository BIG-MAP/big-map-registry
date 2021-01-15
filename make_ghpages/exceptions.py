# -*- coding: utf-8 -*-

class MissingEntity(Exception):
    """ Missing entity
    Base exception for missing entities, usually URLs
    """
    pass


class WrongEntity(Exception):
    """ Wrong entity
    Base exception for wrong entities
    """
    pass


class MissingMetadata(MissingEntity):
    """ Missing metadata
    The key 'meta_url' is missing from apps.json or
    the value of 'meta_url' is wrong/missing.
    """
    pass


class WrongMetadata(WrongEntity):
    """ Wrong metadata
    The provided metadata.json file cannot be loaded by Python's built-in json.loads method.
    The metadata.json file may not be a correct JSON file.
    """
    pass


class MissingGit(MissingEntity):
    """ Missing git URL
    The key 'git_url' is missing from apps.json or
    the value of 'git_url' is wrong/missing.
    """
    pass


class MissingCategories(MissingEntity):
    """ Missing categories
    The key 'categories' is missing from apps.json or
    the value of 'categories' is wrong/missing.
    """
    pass


class WrongCategory(WrongEntity):
    """ Wrong category
    The specified category does not exist in categories.json.
    """
    pass


class MissingLogo(MissingEntity):
    """ Missing logo
    Having retrieved the URL for the logo (from metadata.json),
    it is now found that the logo does not exist on the given URL.
    """
    pass
