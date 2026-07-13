"""Shuttle workflow registry."""

from .wafer_space import WaferSpaceWorkflow


def get_workflow(shuttle: str):
    canonical = shuttle.replace("-", "_").lower()
    if canonical in {"wafer_space", "waferspace"}:
        return WaferSpaceWorkflow
    raise ValueError(
        f"Unsupported shuttle {shuttle!r}; the available provider is 'wafer_space'"
    )


__all__ = ["WaferSpaceWorkflow", "get_workflow"]
