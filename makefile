# Generate OpenAPI client
api:
	admin/make-api.sh
	@$(MAKE) isort
	@$(MAKE) blacken

# Run black on python files to format them
blacken:
	uv run black ./dart ./examples

# Build a Python package and upload it to PyPI
deploy:
	admin/make-deploy.sh

# Format imports on python files
isort:
	uv run isort ./dart ./examples

# Update all dependencies
req-up-all:
	uv lock --upgrade && uv sync
