"""Normalize raw constituent and financial files into a canonical dataset."""

# ruff: noqa: I001

from __future__ import annotations

import argparse
import logging
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd  # noqa: E402
import yaml  # type: ignore[import-untyped]  # noqa: E402

from utils.io import dump_yaml  # noqa: E402

LOGGER = logging.getLogger(__name__)


NUMERIC_COLUMNS = [
    "pbr",
    "roe",
    "dy",
    "market_cap",
    "weight",
]


def _load_yaml(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _normalize_constituents(raw_data: Any) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    pairs: Iterable[tuple[str | None, Any]]
    if isinstance(raw_data, dict):
        pairs = raw_data.items()
    else:
        pairs = [(None, raw_data)]

    for index_name, entries in pairs:
        if entries is None:
            continue
        if isinstance(entries, dict) and "records" in entries:
            candidate_entries = entries["records"]
        else:
            candidate_entries = entries

        if not isinstance(candidate_entries, list):
            raise ValueError("Constituent entries must be provided as a list")

        for entry in candidate_entries:
            if not isinstance(entry, dict):
                continue
            record = {
                "index": entry.get("index") or index_name or "yomiuri333",
                "code": str(entry.get("code", "")).strip(),
                "name": entry.get("name", ""),
                "sector": entry.get("sector", "Unknown"),
                "weight": entry.get("weight"),
            }
            rows.append(record)

    if not rows:
        raise ValueError("No constituent records found")

    frame = pd.DataFrame(rows)
    frame["index"] = frame["index"].fillna("yomiuri333")
    return frame


def _normalize_financials(raw_data: Any) -> pd.DataFrame:
    if raw_data is None:
        return pd.DataFrame()

    if isinstance(raw_data, dict) and "records" in raw_data:
        entries = raw_data["records"]
    elif isinstance(raw_data, dict):
        entries = []
        for index_name, index_records in raw_data.items():
            if isinstance(index_records, list):
                for item in index_records:
                    if isinstance(item, dict):
                        normalized_entry = {**item}
                        normalized_entry.setdefault("index", index_name)
                        entries.append(normalized_entry)
    else:
        entries = raw_data

    if not isinstance(entries, list):
        raise ValueError("Financial records must be provided as a list")

    normalized: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        normalized.append(
            {
                "index": entry.get("index", "yomiuri333"),
                "code": str(entry.get("code", "")).strip(),
                "date": entry.get("date"),
                "pbr": entry.get("pbr"),
                "roe": entry.get("roe"),
                "dy": entry.get("dy"),
                "market_cap": entry.get("market_cap"),
                "weight": entry.get("weight"),
            }
        )

    if not normalized:
        return pd.DataFrame()

    frame = pd.DataFrame(normalized)
    if "date" in frame.columns:
        frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    return frame


def build_canonical(constituents_path: Path, financials_path: Path) -> pd.DataFrame:
    """Create the canonical dataset from raw constituent and financial files."""
    constituents_raw = _load_yaml(constituents_path)
    financials_raw = _load_yaml(financials_path) if financials_path.exists() else None

    constituents_df = _normalize_constituents(constituents_raw)
    financials_df = _normalize_financials(financials_raw)

    if not financials_df.empty:
        # Deduplicate by selecting the latest available date for each code/index pair.
        if "date" in financials_df.columns:
            financials_df = (
                financials_df.sort_values(["index", "code", "date"], na_position="last")
                .drop_duplicates(subset=["index", "code"], keep="last")
                .reset_index(drop=True)
            )
        else:
            financials_df = financials_df.drop_duplicates(
                subset=["index", "code"], keep="last"
            )
    merged = constituents_df.merge(
        financials_df,
        on=["index", "code"],
        how="left",
        suffixes=("", "_fin"),
    )

    if "date_fin" in merged.columns and "date" not in merged.columns:
        merged = merged.rename(columns={"date_fin": "date"})
    if "weight_fin" in merged.columns:
        merged["weight"] = merged["weight"].fillna(merged["weight_fin"])
        merged = merged.drop(columns=["weight_fin"])

    for column in NUMERIC_COLUMNS:
        if column in merged.columns:
            merged[column] = pd.to_numeric(merged[column], errors="coerce")

    if "date" in merged.columns:
        merged["date"] = merged["date"].astype("datetime64[ns]")
        merged["date"] = merged["date"].dt.strftime("%Y-%m-%d")

    merged = merged.sort_values(["index", "code"]).reset_index(drop=True)
    return merged


def write_output(dataset: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.suffix.lower() in {".yaml", ".yml"}:
        payload = {
            "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "records": dataset.to_dict(orient="records"),
        }
        dump_yaml(payload, output_path)
    else:
        dataset.to_csv(output_path, index=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", dest="constituents", type=Path, required=True)
    parser.add_argument("--fin", dest="financials", type=Path, required=True)
    parser.add_argument("--out", dest="output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()
    LOGGER.info("Loading constituents from %s", args.constituents)
    dataset = build_canonical(args.constituents, args.financials)
    LOGGER.info("Writing canonical dataset to %s", args.output)
    write_output(dataset, args.output)


if __name__ == "__main__":
    main()
