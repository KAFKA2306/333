"""Compute concentration metrics such as Herfindahl-Hirschman Index."""
# ruff: noqa: I001

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd  # noqa: E402
from utils.io import dump_json, load_dataframe  # noqa: E402

LOGGER = logging.getLogger(__name__)


def _resolve_weights(subset: pd.DataFrame) -> pd.Series:
    weights = pd.to_numeric(subset.get("weight"), errors="coerce")
    if weights.notna().any():
        weights = weights.fillna(0.0)
    else:
        weights = pd.Series(1.0, index=subset.index)

    total = float(weights.sum())
    if total <= 0:
        weights = pd.Series(1.0, index=subset.index)
        total = float(weights.sum())

    return weights / total


def compute_concentration_metrics(dataset: pd.DataFrame) -> dict[str, Any]:
    if "index" not in dataset.columns:
        raise ValueError("Canonical dataset must include an 'index' column")
    if "sector" not in dataset.columns:
        raise ValueError("Canonical dataset must include a 'sector' column")

    metrics: dict[str, Any] = {
        "hhi": {},
        "top10_weight": {},
        "constituents": {},
    }

    for index_name, subset in dataset.groupby("index"):
        weights = _resolve_weights(subset)
        sector_series = subset["sector"].fillna("Unknown")
        sector_weights = weights.groupby(sector_series).sum()
        hhi_value = float((sector_weights**2).sum())
        top10_value = float(weights.sort_values(ascending=False).head(10).sum())
        metrics["hhi"][index_name] = hhi_value
        metrics["top10_weight"][index_name] = top10_value
        metrics["constituents"][index_name] = int(len(subset))

    return metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--in", dest="input_path", type=Path, required=True)
    parser.add_argument("--out", dest="output_path", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()
    dataset = load_dataframe(args.input_path)
    metrics = compute_concentration_metrics(dataset)
    dump_json(metrics, args.output_path)


if __name__ == "__main__":
    main()
