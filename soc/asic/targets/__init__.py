"""Declarative ASIC target registry.

The target owns logical RTL choices.  The shuttle workflow owns physical
design details such as the PDK variant, standard cells, pads and slot.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple


@dataclass(frozen=True)
class AsicTarget:
    name: str
    pdk_family: str
    pdk_variant: str
    default_cpu_variant: str
    default_clock_hz: int
    supported_shuttles: Tuple[str, ...]
    core_dir: Path

    @property
    def litex_dir(self) -> Path:
        return self.core_dir / "litex"

    @property
    def rtl_dir(self) -> Path:
        return self.core_dir / "verilog" / "rtl"


_ASIC_DIR = Path(__file__).resolve().parents[1]

_TARGETS: Dict[str, AsicTarget] = {
    "gf180": AsicTarget(
        name="gf180",
        pdk_family="gf180mcu",
        pdk_variant="gf180mcuD",
        default_cpu_variant="minimal+cfu",
        default_clock_hz=25_000_000,
        supported_shuttles=("wafer_space",),
        core_dir=_ASIC_DIR / "core" / "gf180mcu",
    ),
}

_TARGET_ALIASES = {
    "gf180mcu": "gf180",
}


def get_target(name: str) -> AsicTarget:
    """Return a target or raise a user-facing error listing valid names."""
    canonical = _TARGET_ALIASES.get(name, name)
    try:
        return _TARGETS[canonical]
    except KeyError as exc:
        valid = ", ".join(sorted(_TARGETS))
        raise ValueError(f"Unsupported ASIC target {name!r}; choose one of: {valid}") from exc


def target_names() -> Tuple[str, ...]:
    return tuple(sorted(_TARGETS))


__all__ = ["AsicTarget", "get_target", "target_names"]
