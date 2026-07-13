"""Small, dependency-free template renderer for generated ASIC files."""

from pathlib import Path
from string import Template
from typing import Mapping


def render_template(name: str, destination: Path, values: Mapping[str, object]) -> None:
    template_path = Path(__file__).resolve().parent / name
    rendered = Template(template_path.read_text()).substitute(
        {key: str(value) for key, value in values.items()}
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists() or destination.read_text() != rendered:
        destination.write_text(rendered)


__all__ = ["render_template"]
