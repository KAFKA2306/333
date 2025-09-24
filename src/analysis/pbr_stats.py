"""Compute valuation-related indicators for the canonical dataset."""
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


def compute_pbr_stats(dataset: pd.DataFrame) -> dict[str, Any]:
    """Calculate PBR summary statistics per index."""
    if "index" not in dataset.columns:
        raise ValueError("Canonical dataset must include an 'index' column")

    if "pbr" not in dataset.columns:
        raise ValueError("Canonical dataset must include a 'pbr' column")

    dataset = dataset.copy()
    dataset["pbr"] = pd.to_numeric(dataset["pbr"], errors="coerce")

    metrics: dict[str, dict[str, Any]] = {
        "lt1": {},
        "mean": {},
        "median": {},
        "count": {},
    }

    for index_name, subset in dataset.groupby("index"):
        series = subset["pbr"].dropna()
        count = int(series.count())
        metrics["count"][index_name] = count
        if count == 0:
            metrics["lt1"][index_name] = None
            metrics["mean"][index_name] = None
            metrics["median"][index_name] = None
            continue

        lt1_ratio = float((series < 1.0).sum() / count)
        metrics["lt1"][index_name] = lt1_ratio
        metrics["mean"][index_name] = float(series.mean())
        metrics["median"][index_name] = float(series.median())

    return metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--in", dest="input_path", type=Path, required=True)
    parser.add_argument("--out", dest="output_path", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()
    LOGGER.info("Loading canonical dataset from %s", args.input_path)
    dataset = load_dataframe(args.input_path)
    metrics = compute_pbr_stats(dataset)
    LOGGER.info("Writing PBR metrics to %s", args.output_path)
    dump_json(metrics, args.output_path)


if __name__ == "__main__":
    main()
