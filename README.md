# AiiDAlab Application Registry

This repository contains the **source code** of the official App registry for the [AiiDAlab](https://www.materialscloud.org/aiidalab).

<p align="center">
 <a href="http://aiidalab.github.io/aiidalab-registry" rel="Go to AiiDAlab app registry">
  <img src="make_ghpages/static/gotobutton.svg">
 </a>
</p>

## Adding your app

 1. Add a `metadata.json` file to your app repository. Example:

    ```json
        {
            "title": "AiiDA Tutorials",
            "description": "Learn how to use AiiDA using jupyter notebooks on the AiiDAlab.",
            "version": "0.1-alpha",
            "authors": "A. Person, B. Smart",
            "logo": "folder/logo.png",
            "state": "development",
            "documentation_url": "https://aiidalab-exmpl.readthedocs.io",
            "external_url": "http://www.aiida.net"
        }
    ```

    **Note**: The fields `title` and `description` are mandatory.

    **Note**: If you used the
    [AiiDAlab App cookie cutter](https://github.com/aiidalab/aiidalab-app-cutter)
    to create your app, you should already have `metadata.json` in your repository
    and need only update it.

 1. Fork this repository.

 1. Make a pull request that adds your app to the `apps.json` file. Example:

    ```json
        "aiida-tutorials": {
            "git_url": "https://github.com/aiidateam/aiida_demos.git",
            "meta_url": "https://raw.githubusercontent.com/aiidateam/aiida_demos/master/metadata.json",
            "categories": ["tutorials"]
        }
    ```

Your app will show up in the
[AiiDAlab App Store](https://github.com/aiidalab/aiidalab-home/blob/master/appstore.ipynb)
once your pull request is merged.

### Valid keys for `metadata.json`

| Key | Requirement | Description |
|:---:|:---:|:---|
| `title` | **Mandatory** | The title will be displayed in the list of apps in the application manager. |
| `description` | **Mandatory** | The description will be displayed on the detail page of your app. |
| `version` | Optional | The version will be displayed on the detail page of your app. This is also used by the [AiiDAlab App Store](https://github.com/aiidalab/aiidalab-home/blob/master/appstore.ipynb). |
| `authors` | Optional | Comma-separated list of authors. |
| `logo` | Optional | Relative path to a logo (png or jpg) within your repository. |
| `state` | Optional | One of<br>- `registered`: lowest level - app may not yet be in a working state. Use this to secure a specific name.<br>- `development`: app is under active development, expect the occasional bug.<br>- `stable`: app can be used in production. |
| `documentation_url` | Optional | The link to the online documentation of the app (e.g. on [Read The Docs](https://readthedocs.org/)). |
| `external_url` | Optional | General homepage for your app. |

### Valid keys for your app in `apps.json`

| Key | Requirement | Description |
|:---:|:---:|:---|
| `git_url` | **Mandatory** | Link to the source code repository. |
| `meta_url` | **Mandatory** | Link to the location of your app's `metadata.json` file. |
| `categories` | Optional | List of valid categories.<br>You can see the most recent list of categories in [`categories.json`](https://github.com/aiidalab/aiidalab-registry/blob/master/categories.json), including a description of each category. |

## Acknowledgements

This work is supported by the [MARVEL National Centre for Competency in Research](<http://nccr-marvel.ch>)
funded by the [Swiss National Science Foundation](<http://www.snf.ch/en>), as well as by the [MaX
European Centre of Excellence](<http://www.max-centre.eu/>) funded by the Horizon 2020 EINFRA-5 program,
Grant No. 676598.

![MARVEL](make_ghpages/static/img/MARVEL.png)
![MaX](make_ghpages/static/img/MaX.png)
