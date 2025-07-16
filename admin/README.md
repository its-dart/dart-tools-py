# Admin functionality

- [Admin functionality](#admin-functionality)
  - [Install local version](#install-local-version)
  - [Test with a different Python version](#test-with-a-different-python-version)
  - [Sync API](#sync-api)
  - [Deploy setup](#deploy-setup)
  - [Deploy](#deploy)
  - [Dependency updating](#dependency-updating)

## Install local version

1. Run `uv sync` as needed
2. Run with `uv run dart [args ...]`

## Test with a different Python version

1. Choose the version with `uv venv --python 3.x`
2. Run `uv sync`

## Sync API

1. Run `uv sync` as needed
2. Run `make api`

## Deploy setup

1. Get an existing PyPI token or [make a new one](https://pypi.org/manage/account/token/)
2. Set the `UV_PUBLISH_TOKEN` environment variable, for example, by running `export UV_PUBLISH_TOKEN=<PyPI token>`

## Deploy

1. Bump the version in `pyproject.toml`
2. Run `uv sync`
3. Run `make deploy`
4. Commit and push all local changes to GitHub

## Dependency updating

1. Manually bump versions in `pyproject.toml`
   1. Bump the dependencies in `dependencies` to be `>=` the lowest functional minor version
   2. Bump the dependencies in `[dependency-groups]` to be `==` the latest patch version
2. Run `make req-up-all`
