# Admin functionality

- [Admin functionality](#admin-functionality)
  - [Local setup](#local-setup)
  - [Test with a different Python version](#test-with-a-different-python-version)
  - [Sync API](#sync-api)
  - [Deploy setup](#deploy-setup)
  - [Deploy](#deploy)
  - [Dependency updating](#dependency-updating)

## Local setup

1. Run `uv sync` to install the dependencies
2. Run `cp -n .env.example .env` to copy the example environment file and then fill out all needed variables
3. Run with `uv run dart [args ...]`

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
4. Commit and push all local changes to GitHub, then open and merge a PR there

## Dependency updating

1. Manually bump versions in `pyproject.toml`
   1. Bump the dependencies in `dependencies` to be `>=` the lowest functional minor version
   2. Bump the dependencies in `[dependency-groups]` to be `==` the latest patch version
2. Run `make req-up-all`
