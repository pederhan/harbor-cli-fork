# Contributing

`harbor-cli` is an open source project, and contributions are welcome. This document outlines the development process.

## Development environment

The easiest way to set up a development environment is by configuring a Hatch environment.

```
hatch env create
```

See [the Hatch docs](https://hatch.pypa.io/latest/environment/) for more information.

## Pre-commit hooks

The code is linted and formatted using a pre-commmit configuration consisting of tools such as [Black](https://github.com/psf/black), [Ruff](https://github.com/charliermarsh/ruff), [reorder_python_imports](https://github.com/asottile/reorder_python_imports) and [mypy](https://github.com/python/mypy/).

Install pre-commit:

```
pip install pre-commit
```

Install the pre-commit hooks:

```
pre-commit install
```

Run the pre-commit hooks:

```
pre-commit run --all-files
```

## Testing

Hatch supports testing against multiple Python versions, similar to [Tox](https://tox.wiki/en/latest/) and [Nox](https://nox.thea.codes/en/stable/).

To run the test suite for the current environment:

```
hatch run test
```

Run the test suite for all supported Python versions:

```
hatch run test:test
```

Tests are run in CI, but it's a good idea to run them locally before pushing changes.

## Documentation

The documentation is built using [MkDocs](https://www.mkdocs.org/). To serve the documentation locally:

```
hatch run docs:serve
```

To build the documentation:

```
hatch run docs:build
```

## Changelog

TBD

## Pull requests

When submitting a pull request, please make sure to run the pre-commit hooks and tests locally before pushing. This will ensure a smoother review process.

## Releasing

Releases are handled by a GitHub actions workflow found [here](https://github.com/pederhan/harbor-cli/blob/main/.github/workflows/build.yml). Whenever a new tag whose name starts `harbor-cli-v` is pushed to the repository on the `main` branch, the workflow will build and publish a new release to PyPI.

```
$ python scripts/bump_version.py --help

 Usage: bump_version.py [OPTIONS] [major|minor|patch|x.y.z],[release|a|a
                        lpha|b|beta|c|rc|pre|preview|r|rev|post|dev]

 Bump the version of the project and create a new git tag.
 Examples:
 $ python bump_version.py minor
 $ python bump_version.py major,rc
 $ python bump_version.py 1.2.3 # generally don't use this

╭─ Arguments ───────────────────────────────────────────────────────────╮
│ *    version      [major|minor|patch|x.y.z  Version bump to perform   │
│                   ],[release|a|alpha|b|bet  or new version to set.    │
│                   a|c|rc|pre|preview|r|rev  [default: None]           │
│                   |post|dev]                [required]                │
╰───────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                           │
╰───────────────────────────────────────────────────────────────────────╯

```

The tool will automatically update the version in `harbor_cli/__about__.py`, and create a new tag with the new version number (`harbor-cli-vx.y.z`).

Pushing the new tag to the remote repository will trigger a new release.

```
git push origin --tags
```

!!! attention "On versioning"

    In general, managing releases and versioning should only be handled by the project maintainer(s), but it is documented here for completeness.

### Examples

#### Bump major version

Major releases are used to indicate breaking changes. Breaking changes are changes that break backwards compatibility, such as removing or renaming a command or option, changing the configuration file format, or changing the behavior of an existing command.

```
python scripts/bump_version.py major
```

#### Bump minor version

Minor releases are used to indicate new features that maintain backwards compatibility. New commands and new options are considered new features.

```
python scripts/bump_version.py minor
```

#### Bump patch version

Patch releases are used to indicate bug fixes, refactoring, and other minor non-feature changes that maintain backwards compatibility.

```
python scripts/bump_version.py patch
```

#### Bump major version and graduate to pre-release

Sometimes we want to publish a pre-release version to allow users to test the new version before it is officially released.

```
python scripts/bump_version.py major,pre
```

#### Graduate to release candidate

Graduating to release candidate is not necessary, but can sometimes be useful to indicate that the release is feature-complete and ready for testing, but not yet ready for general use due to possible minor bugs or missing/incomplete documentation.

```
python scripts/bump_version.py major,rc
```

#### Graduate to release

Going from a pre-release or a release candidate to a release is done by removing the status suffix:

```
python scripts/bump_version.py release
```