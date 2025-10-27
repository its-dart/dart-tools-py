#!/usr/bin/env python3
"""
Fix enum naming issues in generated OpenAPI client.

openapi-python-client generates generic names like VALUE_0, VALUE_1 for enum
values that start with special characters (like "-published_at"). This script
automatically finds and fixes all such cases with descriptive names.
"""

import re
from pathlib import Path


def convert_to_enum_name(value: str) -> str:
    """
    Convert an enum value to a proper Python enum name.

    Examples:
        "-published_at" -> "PUBLISHED_AT_DESC"
        "published_at" -> "PUBLISHED_AT"
        "-folder__order" -> "FOLDER_ORDER_DESC"
    """
    if value.startswith("-"):
        # Descending order: convert "-published_at" to "PUBLISHED_AT_DESC"
        name = value[1:].upper().replace("__", "_").replace("-", "_") + "_DESC"
    else:
        # Ascending order: convert "published_at" to "PUBLISHED_AT"
        name = value.upper().replace("__", "_").replace("-", "_")
    return name


def fix_enum_file(file_path: Path) -> int:
    content = file_path.read_text()
    original_content = content

    # Find all VALUE_N = "value" patterns
    pattern = r'(VALUE_\d+)\s*=\s*"([^"]+)"'

    def replace_func(match: re.Match) -> str:
        value_n = match.group(1)
        enum_value = match.group(2)
        proper_name = convert_to_enum_name(enum_value)
        return f'{proper_name} = "{enum_value}"'

    content = re.sub(pattern, replace_func, content)

    if content != original_content:
        file_path.write_text(content)
        # Count replacements
        return len(re.findall(pattern, original_content))

    return 0


def main() -> None:
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    models_dir = project_root / "dart" / "generated" / "models"

    if not models_dir.exists():
        print(f"Models directory not found: {models_dir}")
        return

    total_fixed = 0
    files_fixed = 0

    # Find all Python files in models directory
    for file_path in models_dir.glob("*.py"):
        if file_path.name == "__init__.py":
            continue

        count = fix_enum_file(file_path)
        if count > 0:
            files_fixed += 1
            total_fixed += count
            print(f"Fixed {count} enum(s) in {file_path.name}")

    if files_fixed == 0:
        print("No enum naming issues found.")
    else:
        print(f"\nTotal: Fixed {total_fixed} enum(s) across {files_fixed} file(s)")


if __name__ == "__main__":
    main()
