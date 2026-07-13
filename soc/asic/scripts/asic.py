"""CLI used by the ASIC Makefile facade."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# This file is also invoked directly by the Make facade.  Add `soc/` so the
# local `asic` package is importable without installing another Python package.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from asic.targets import get_target
from asic.workflows import get_workflow
from asic.workflows.wafer_space import WaferSpaceOptions


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a CFU-Playground ASIC target")
    parser.add_argument("command", choices=("describe", "generate"))
    parser.add_argument("--target", default="gf180")
    parser.add_argument("--shuttle", default="wafer_space")
    parser.add_argument("--project", default="wamCFU")
    parser.add_argument("--slot", default="1x1")
    parser.add_argument("--scl", default="gf180mcu_fd_sc_mcu7t5v0")
    parser.add_argument("--pad", default="gf180mcu_fd_io")
    parser.add_argument("--sram", default="gf180mcu_fd_ip_sram")
    parser.add_argument("--cpu-variant", default="minimal+cfu")
    return parser


def main() -> None:
    args = _parser().parse_args()
    target = get_target(args.target)
    workflow_type = get_workflow(args.shuttle)
    cfu_root = Path(__file__).resolve().parents[3]
    workflow = workflow_type(
        cfu_root,
        target,
        WaferSpaceOptions(
            project=args.project,
            slot=args.slot,
            scl=args.scl,
            pad=args.pad,
            sram=args.sram,
            cpu_variant=args.cpu_variant,
        ),
    )

    if args.command == "describe":
        workflow.validate()
        print(json.dumps(workflow.describe(), indent=2, sort_keys=True))
    else:
        manifest = workflow.generate()
        print(f"ASIC export manifest: {manifest}")


if __name__ == "__main__":
    main()
