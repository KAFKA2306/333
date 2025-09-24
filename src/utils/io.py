"""Utility functions for reading and writing structured data files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import yaml  # type: ignore[import-untyped]


def load_dataframe(path: str | Path) -> pd.DataFrame:
    """Load a CSV or YAML file into a :class:`~pandas.DataFrame`.

    The canonical dataset is stored either as CSV or as a YAML document with a
    top-level ``records`` key. When the YAML file stores entries grouped by
    index name (for example ``{"yomiuri333": [...]}``), the helper will inject
    the grouping key into each record as the ``index`` column.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    suffix = file_path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(file_path)

    if suffix in {".yaml", ".yml"}:
        content = yaml.safe_load(file_path.read_text(encoding="utf-8"))
        if content is None:
            return pd.DataFrame()

        records: list[dict[str, Any]]
        if isinstance(content, dict):
            if "records" in content and isinstance(content["records"], list):
                raw_records = content["records"]
            else:
                raw_records = []
                for group, entries in content.items():
                    if isinstance(entries, list):
                        for entry in entries:
                            if isinstance(entry, dict):
                                normalized = {**entry}
                                normalized.setdefault("index", group)
                                raw_records.append(normalized)
                if not raw_records:
                    # Fallback: treat dictionary as a single record.
                    raw_records = [content]
            records = [entry for entry in raw_records if isinstance(entry, dict)]
        elif isinstance(content, list):
            records = [entry for entry in content if isinstance(entry, dict)]
        else:
            raise ValueError(f"Unsupported YAML structure in {file_path}")

        return pd.DataFrame(records)

    raise ValueError(f"Unsupported file extension: {file_path.suffix}")


def dump_json(data: Any, path: str | Path) -> None:
    """Persist *data* as a JSON document."""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def dump_yaml(data: Any, path: str | Path) -> None:
    """Persist *data* as a YAML document."""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
