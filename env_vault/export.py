"""Export and import environment variables in various formats."""

from __future__ import annotations

import json
from typing import Dict


SUPPORTED_FORMATS = ("dotenv", "json", "shell")


def export_dotenv(variables: Dict[str, str]) -> str:
    """Export variables as a .env file string."""
    lines = []
    for key, value in sorted(variables.items()):
        escaped = value.replace('"', '\\"')
        lines.append(f'{key}="{escaped}"')
    return "\n".join(lines) + ("\n" if lines else "")


def export_json(variables: Dict[str, str]) -> str:
    """Export variables as a JSON string."""
    return json.dumps(variables, indent=2, sort_keys=True) + "\n"


def export_shell(variables: Dict[str, str]) -> str:
    """Export variables as shell export statements."""
    lines = []
    for key, value in sorted(variables.items()):
        escaped = value.replace("'", "'\"'\"'")
        lines.append(f"export {key}='{escaped}'")
    return "\n".join(lines) + ("\n" if lines else "")


def import_dotenv(content: str) -> Dict[str, str]:
    """Parse a .env file string into a dict of variables."""
    variables: Dict[str, str] = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, raw_value = line.partition("=")
        key = key.strip()
        raw_value = raw_value.strip()
        if len(raw_value) >= 2 and raw_value[0] == '"' and raw_value[-1] == '"':
            raw_value = raw_value[1:-1].replace('\\"', '"')
        elif len(raw_value) >= 2 and raw_value[0] == "'" and raw_value[-1] == "'":
            raw_value = raw_value[1:-1]
        if key:
            variables[key] = raw_value
    return variables


def import_json(content: str) -> Dict[str, str]:
    """Parse a JSON string into a dict of variables."""
    data = json.loads(content)
    if not isinstance(data, dict):
        raise ValueError("JSON content must be a top-level object")
    return {str(k): str(v) for k, v in data.items()}


def format_output(variables: Dict[str, str], fmt: str) -> str:
    """Dispatch export to the requested format."""
    if fmt == "dotenv":
        return export_dotenv(variables)
    if fmt == "json":
        return export_json(variables)
    if fmt == "shell":
        return export_shell(variables)
    raise ValueError(f"Unsupported format '{fmt}'. Choose from: {SUPPORTED_FORMATS}")
