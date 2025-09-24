"""Compute ROE distribution statistics per index."""
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
QUANTILES = (0.25, 0.5, 0.75)


def compute_roe_stats(dataset: pd.DataFrame) -> dict[str, Any]:
    if "index" not in dataset.columns:
        raise ValueError("Canonical dataset must include an 'index' column")
    if "roe" not in dataset.columns:
        raise ValueError("Canonical dataset must include a 'roe' column")

    dataset = dataset.copy()
    dataset["roe"] = pd.to_numeric(dataset["roe"], errors="coerce")

    metrics: dict[str, Any] = {
        "median": {},
        "quantiles": {str(int(q * 100)): {} for q in QUANTILES},
        "count": {},
    }

    for index_name, subset in dataset.groupby("index"):
        series = subset["roe"].dropna()
        count = int(series.count())
        metrics["count"][index_name] = count
        if count == 0:
            metrics["median"][index_name] = None
            for q in QUANTILES:
                metrics["quantiles"][str(int(q * 100))][index_name] = None
            continue

        metrics["median"][index_name] = float(series.median())
        for q in QUANTILES:
            metrics["quantiles"][str(int(q * 100))][index_name] = float(
                series.quantile(q)
            )

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
    metrics = compute_roe_stats(dataset)
    dump_json(metrics, args.output_path)


if __name__ == "__main__":
    main()
