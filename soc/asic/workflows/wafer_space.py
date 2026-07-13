"""GF180 Wafer.Space RTL export workflow."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from asic.targets import AsicTarget
from asic.templates import render_template


CPU_VARIANT_FILES = {
    "minimal+cfu": "VexRiscv_MinCfu.v",
    "slim+cfu": "VexRiscv_SlimCfu.v",
    "slim+cfu+debug": "VexRiscv_SlimCfuDebug.v",
    "full+cfu": "VexRiscv_FullCfu.v",
    "full+cfu+debug": "VexRiscv_FullCfuDebug.v",
}


@dataclass(frozen=True)
class WaferSpaceOptions:
    project: str
    slot: str
    scl: str
    pad: str
    sram: str
    cpu_variant: str


class WaferSpaceWorkflow:
    """Generate LiteX RTL, then export a deterministic Wafer.Space source bundle."""

    name = "wafer_space"

    def __init__(self, cfu_root: Path, target: AsicTarget, options: WaferSpaceOptions):
        self.cfu_root = cfu_root.resolve()
        self.target = target
        self.options = options
        self.asic_dir = Path(__file__).resolve().parents[1]
        self.plugin_dir = self.asic_dir / "librelane" / "gf180mcu-waferspace-plugin"
        self.build_dir = (
            self.cfu_root
            / "soc"
            / "build"
            / "asic"
            / f"{target.name}.{self.name}.{options.project}"
        )

    def describe(self) -> dict:
        return {
            "target": self.target.name,
            "pdk": self.target.pdk_variant,
            "shuttle": self.name,
            "project": self.options.project,
            "cpu_variant": self.options.cpu_variant,
            "clock_hz": self.target.default_clock_hz,
            "slot": self.options.slot,
            "scl": self.options.scl,
            "pad": self.options.pad,
            "sram": self.options.sram,
            "build_dir": str(self.build_dir),
            "plugin_dir": str(self.plugin_dir),
        }

    def validate(self) -> Path:
        if self.name not in self.target.supported_shuttles:
            raise ValueError(
                f"Target {self.target.name!r} does not support shuttle {self.name!r}"
            )
        if self.options.slot not in {"1x1", "0p5x1", "1x0p5", "0p5x0p5"}:
            raise ValueError(f"Unsupported Wafer.Space slot {self.options.slot!r}")
        if self.options.cpu_variant not in CPU_VARIANT_FILES:
            valid = ", ".join(sorted(CPU_VARIANT_FILES))
            raise ValueError(
                f"Unsupported ASIC CPU variant {self.options.cpu_variant!r}; choose: {valid}"
            )

        is_3v3 = (
            self.options.scl == "gf180mcu_as_sc_mcu7t3v3"
            or self.options.pad == "gf180mcu_ocd_io"
            or self.options.sram == "gf180mcu_ocd_ip_sram"
        )
        if is_3v3 and (
            self.options.scl != "gf180mcu_as_sc_mcu7t3v3"
            or self.options.pad != "gf180mcu_ocd_io"
            or self.options.sram != "gf180mcu_ocd_ip_sram"
        ):
            raise ValueError(
                "The experimental 3.3 V target must select the 3.3 V SCL, PAD and SRAM together"
            )

        project_dir = self.cfu_root / "proj" / self.options.project
        candidates = (project_dir / "cfu.sv", project_dir / "cfu.v")
        cfu_source = next((path for path in candidates if path.exists()), None)
        if cfu_source is None:
            raise FileNotFoundError(
                f"No cfu.sv or cfu.v found for project {self.options.project!r} in {project_dir}"
            )
        return cfu_source

    def generate(self) -> Path:
        cfu_source = self.validate()
        self.build_dir.mkdir(parents=True, exist_ok=True)

        env = os.environ.copy()
        env["CFU_ROOT"] = str(self.cfu_root)
        generator = self.target.litex_dir / "caravel.py"
        subprocess.run(
            [
                sys.executable,
                str(generator),
                "--cpu-cfu",
                str(cfu_source),
                "--cpu-variant",
                self.options.cpu_variant,
                "--sys-clk-freq",
                str(self.target.default_clock_hz),
                "--output-dir",
                str(self.build_dir),
            ],
            cwd=self.target.litex_dir,
            env=env,
            check=True,
        )

        generated_top = self.build_dir / "gateware" / "mgmt_core.v"
        modified_top = self.build_dir / "gateware" / "mgmt_core_asic.v"
        subprocess.run(
            [
                sys.executable,
                str(self.target.litex_dir / "modify_verilog.py"),
                "--input",
                str(generated_top),
                "--output",
                str(modified_top),
                "--debug-reset",
                str(self.target.litex_dir / "debug_reset.v"),
            ],
            cwd=self.target.litex_dir,
            check=True,
        )

        cpu_source = (
            self.cfu_root / "soc" / "vexriscv" / CPU_VARIANT_FILES[self.options.cpu_variant]
        )
        sources = [
            cpu_source,
            cfu_source,
            self.target.rtl_dir / "sram.v",
            self.target.rtl_dir / "GF180_RAM_512x32.v",
            modified_top,
        ]
        self._assert_sources(sources)

        generated_dir = self.plugin_dir / "src" / "generated"
        generated_dir.mkdir(parents=True, exist_ok=True)
        bundle = generated_dir / "litex_soc.v"
        self._write_bundle(bundle, sources)
        render_template(
            "gf180_sram_wrapper.v.tpl",
            generated_dir / "gf180_sram_wrapper.v",
            {},
        )
        render_template(
            "wafer_space_chip_core.sv.tpl",
            self.plugin_dir / "src" / "chip_core.sv",
            {"clock_hz": self.target.default_clock_hz},
        )

        manifest = {
            **self.describe(),
            "cfu_source": str(cfu_source),
            "generated_top": str(generated_top),
            "exported_sources": [
                "src/generated/litex_soc.v",
                "src/generated/gf180_sram_wrapper.v",
                "src/chip_core.sv",
                "src/chip_top.sv",
            ],
            "sha256": {
                path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in (
                    bundle,
                    generated_dir / "gf180_sram_wrapper.v",
                    self.plugin_dir / "src" / "chip_core.sv",
                )
            },
        }
        manifest_path = self.build_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        return manifest_path

    @staticmethod
    def _assert_sources(sources: Iterable[Path]) -> None:
        missing = [str(path) for path in sources if not path.is_file()]
        if missing:
            raise FileNotFoundError("Missing generated RTL dependencies: " + ", ".join(missing))

    @staticmethod
    def _write_bundle(destination: Path, sources: List[Path]) -> None:
        chunks = ["// Auto-generated by soc/asic; do not edit.\n"]
        for source in sources:
            chunks.extend(
                [
                    "\n`default_nettype wire\n",
                    f"// ---- source: {source.name} ----\n",
                    source.read_text(),
                    "\n",
                ]
            )
        content = "".join(chunks)
        if not destination.exists() or destination.read_text() != content:
            destination.write_text(content)


__all__ = ["WaferSpaceOptions", "WaferSpaceWorkflow"]
