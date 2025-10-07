<div align="center">
  <h1>Dart Tools</h1>
  <p>
    <a href="https://pypi.org/project/dart-tools"><img src="https://img.shields.io/pypi/v/dart-tools" alt="PyPI"></a>
    <a href="pyproject.toml"><img src="https://img.shields.io/pypi/pyversions/dart-tools" alt="Supported Python Versions"></a>
    <a href="LICENSE"><img src="https://img.shields.io/github/license/its-dart/dart-tools-py" alt="License"></a>
  </p>
</div>

[Dart](https://dartai.com?nr=1) is Project Management powered by AI.

`dart-tools` is the Dart CLI and Python Library. It enables direct integration with Dart through a terminal CLI or through Python. It implements client functions to the [Dart Public API](https://app.dartai.com/api/v0/public/docs/).

- [Installation](#installation)
  - [Naming conflicts](#naming-conflicts)
- [Using the CLI](#using-the-cli)
- [Using the Python Library](#using-the-python-library)
- [Help and Resources](#help-and-resources)
- [Contributing](#contributing)
- [License](#license)

## Installation

In the terminal, install by running

```sh
pip install dart-tools
```

### Naming conflicts

If you have a preexisting shell command named `dart`, a quick fix is to run `which -a dart` and fine the path for this `dart` application. Then you can create an alias and add it to your shell profile file (`.zshrc`, `.bashrc`, etc.). For example, open `~/.zshrc` and add a line like `alias dartai="/path/to/dart"`, save it, and restart your terminal.

## Using the CLI

Start off by setting up authentication with

```sh
dart login
```

Then, you can create a new task with a command along the lines of

```sh
dart task-create "Update the landing page" -p0 --tag marketing
```

which will make a new task called 'Update the landing page' with priority 'Critical' (i.e. P0) and with the 'marketing' tag.

You can explore all of these options and many more with `dart --help` or the more specific help for subcommands, in this case `dart task-create --help`.

Another common workflow is to updating a preexisting task. To do this, run something like

```sh
dart task-update [ID] -s Done
```

This command will mark the referenced task 'Done'. Here `[ID]` is meant to be replaced (including the brackets) with the ID of an existing task. You can get a ID from any existing task in a number of ways, such as by copying it from the end of a task's URL or by clicking the '...' button in a task page in Dart and then choosing 'Copy ID'.

## Using the Python Library

First, set up authentication. Run `dart login` in the terminal for an interactive process. Alternatively, copy your authentication token from [your Dart profile](https://app.dartai.com/?settings=account) and save that as the `DART_TOKEN` environment variable.

Then, you can run something like

```python
import os
from dart import create_task, is_logged_in, update_task

# Check that auth is set up and stop if not, can remove this once everything is set up
is_logged_in(should_raise=True)

# Create a new task called 'Update the landing page' with priority 'Critical' (i.e. p0) and with the 'marketing' tag
new_task = create_task(
    "Update the landing page", priority_int=0, tag_titles=["marketing"]
)

# Update the task to be 'Done'
update_task(new_task.id, status_title="Done")
```

## Help and Resources

- [Homepage](https://dartai.com/?nr=1)
- [Web App](https://app.dartai.com/)
- [Help Center](https://help.dartai.com/)
- [Bugs and Features](https://app.dartai.com/p/r/JFyPnhL9En61)
- [Library Source](https://github.com/its-dart/dart-tools-py/)
- [Chat on Discord](https://discord.gg/RExv8jEkSh)
- Email us at [support@dartai.com](mailto:support@dartai.com)

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under [the MIT License](LICENSE).
