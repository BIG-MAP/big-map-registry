import string
from urllib.parse import urlparse

from dulwich.client import get_transport_and_path_from_url


def get_html_app_fname(app_name):
    valid_characters = set(string.ascii_letters + string.digits + "_-")

    simple_string = "".join(c for c in app_name if c in valid_characters)

    return f"{simple_string}.html"


def get_hosted_on(url):
    netloc = urlparse(url).netloc

    # Remove port (if any)
    netloc = netloc.partition(":")[0]

    # Remove subdomains (this only works for domain suffixes of length 1!)
    # TODO: fix it for domains like yyy.co.uk
    netloc = ".".join(netloc.split(".")[-2:])

    return netloc


def get_git_branches(git_url):
    t, p = get_transport_and_path_from_url(git_url)
    branches = t.get_refs(p)
    res = {}
    for key, value in branches.items():
        res[key.decode("utf-8")] = value.decode("utf-8")
    return res


def get_git_author(git_url):
    return urlparse(git_url).path.split("/")[1]
