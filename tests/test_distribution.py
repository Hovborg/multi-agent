"""Distribution-level invariants for package data."""

from pathlib import Path

import multiagent
from multiagent.catalog import CATALOG_DIR, Catalog


def test_default_catalog_is_packaged_beside_python_modules():
    package_dir = Path(multiagent.__file__).resolve().parent

    assert CATALOG_DIR.parent == package_dir
    assert CATALOG_DIR.is_dir()
    assert len(Catalog()) == 48


def test_default_catalog_contains_one_yaml_per_agent():
    yaml_files = [
        path
        for path in CATALOG_DIR.rglob("*.yaml")
        if not any(part.startswith("_") for part in path.relative_to(CATALOG_DIR).parts)
    ]

    assert len(yaml_files) == len(Catalog().list_all()) == 48
