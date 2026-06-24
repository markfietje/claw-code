"""Shared helper for archive placeholder packages."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict, cast


class ArchiveSnapshot(TypedDict):
    """Shape of each ``reference_data/subsystems/*.json`` file.

    Verified uniform across all 29 subsystem snapshots.
    """

    archive_name: str
    package_name: str
    module_count: int
    sample_files: list[str]


def load_archive_metadata(package_name: str) -> ArchiveSnapshot:
    """Load archive metadata from reference_data/subsystems/{package_name}.json."""
    snapshot_path = (
        Path(__file__).resolve().parent
        / "reference_data"
        / "subsystems"
        / f"{package_name}.json"
    )
    return _coerce_snapshot(cast("object", json.loads(snapshot_path.read_text())), package_name)


def _coerce_snapshot(data: object, package_name: str) -> ArchiveSnapshot:
    """Validate a parsed JSON value and build a typed ``ArchiveSnapshot``.

    ``json.loads`` is untyped, so we narrow to ``dict[str, object]`` (guarded by
    an ``isinstance`` check) and verify each field's concrete type at runtime.
    """
    if not isinstance(data, dict):
        raise TypeError(f"{package_name}.json: expected a JSON object")
    obj = cast(dict[str, object], data)

    required = ("archive_name", "package_name", "module_count", "sample_files")
    missing = [k for k in required if k not in obj]
    if missing:
        raise KeyError(f"{package_name}.json: missing keys: {missing}")

    archive_name = obj["archive_name"]
    pkg = obj["package_name"]
    module_count = obj["module_count"]
    sample_files = obj["sample_files"]

    if not isinstance(archive_name, str):
        raise TypeError(f"{package_name}.json: archive_name must be str")
    if not isinstance(pkg, str):
        raise TypeError(f"{package_name}.json: package_name must be str")
    # bool is a subclass of int — exclude it explicitly.
    if not isinstance(module_count, int) or isinstance(module_count, bool):
        raise TypeError(f"{package_name}.json: module_count must be int")
    if not isinstance(sample_files, list):
        raise TypeError(f"{package_name}.json: sample_files must be list")
    # Cast to list[object] (guarded by isinstance above) so elements are typed
    # `object`, then prove each is str via narrowing — no Unknown leaks out.
    files: list[str] = []
    for entry in cast(list[object], sample_files):
        if not isinstance(entry, str):
            raise TypeError(f"{package_name}.json: sample_files must be list[str]")
        files.append(entry)

    return ArchiveSnapshot(
        archive_name=archive_name,
        package_name=pkg,
        module_count=module_count,
        sample_files=files,
    )
