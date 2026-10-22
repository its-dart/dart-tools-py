# Admin functionality

- [Admin functionality](#admin-functionality)
  - [Local setup](#local-setup)
  - [Test with a different Python version](#test-with-a-different-python-version)
  - [Sync API](#sync-api)
  - [Deploy setup](#deploy-setup)
  - [Deploy](#deploy)
  - [Dependency updating](#dependency-updating)

## Local setup

1. Install the pinned uv version: `curl -LsSf https://astral.sh/uv/0.13.5/install.sh | sh`
2. Run `uv sync` to install the dependencies
3. Run `cp -n .env.example .env` to copy the example environment file and then fill out all needed variables
4. Run with `uv run dart [args ...]`

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
3. Commit and push all local changes to GitHub, then open a PR there
4. After the PR merges run `make deploy`

## Dependency updating

1. Manually bump versions in `pyproject.toml`
   1. Bump the dependencies in `dependencies` to be `>=` the lowest functional minor version
   2. Bump the dependencies in `[dependency-groups]` to be `==` the latest patch version
2. Update the uv pin in `pyproject.toml` and local setup instructions as needed
3. Run `make req-up-all`
4. Update supported Python versions in package metadata and installer for new stable releases, and drop EOL versions as needed
