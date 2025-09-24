from __future__ import annotations

# ruff: noqa: I001

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1] / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest  # noqa: E402

from analysis.pbr_stats import compute_pbr_stats  # noqa: E402
from analysis.roe_stats import compute_roe_stats  # noqa: E402
from analysis.sector_hhi import compute_concentration_metrics  # noqa: E402
from analysis.yield_stats import compute_yield_stats  # noqa: E402
from ingest.csv_to_canonical import build_canonical  # noqa: E402
from render.common import derive_logic_summary  # noqa: E402


@pytest.fixture()
def sample_files(tmp_path: Path) -> tuple[Path, Path]:
    constituents = {
        "yomiuri333": [
            {"code": "1001", "name": "Alpha", "sector": "Materials", "weight": 0.5},
            {"code": "2002", "name": "Beta", "sector": "Industrials", "weight": 0.5},
        ],
        "topix": [
            {"code": "1001", "name": "Alpha", "sector": "Materials", "weight": 0.6},
            {"code": "2002", "name": "Beta", "sector": "Industrials", "weight": 0.25},
            {"code": "3003", "name": "Gamma", "sector": "IT", "weight": 0.15},
        ],
    }
    financials = [
        {
            "index": "yomiuri333",
            "code": "1001",
            "date": "2023-12-31",
            "pbr": 0.8,
            "roe": 5.0,
            "dy": 2.6,
        },
        {
            "index": "yomiuri333",
            "code": "2002",
            "date": "2023-12-31",
            "pbr": 1.2,
            "roe": 3.6,
            "dy": 2.1,
        },
        {
            "index": "topix",
            "code": "1001",
            "date": "2023-12-31",
            "pbr": 1.4,
            "roe": 7.5,
            "dy": 1.8,
        },
        {
            "index": "topix",
            "code": "2002",
            "date": "2023-12-31",
            "pbr": 0.9,
            "roe": 5.5,
            "dy": 1.9,
        },
        {
            "index": "topix",
            "code": "3003",
            "date": "2023-12-31",
            "pbr": 2.1,
            "roe": 10.5,
            "dy": 1.2,
        },
    ]

    constituents_path = tmp_path / "constituents.yaml"
    financials_path = tmp_path / "financials.yaml"
    constituents_path.write_text(json.dumps(constituents), encoding="utf-8")
    financials_path.write_text(json.dumps(financials), encoding="utf-8")
    return constituents_path, financials_path


def test_build_canonical(sample_files: tuple[Path, Path]) -> None:
    constituents_path, financials_path = sample_files
    dataset = build_canonical(constituents_path, financials_path)

    assert set(dataset.columns) >= {
        "index",
        "code",
        "sector",
        "pbr",
        "roe",
        "dy",
        "weight",
    }
    assert len(dataset) == 5
    assert dataset.loc[
        (dataset["index"] == "yomiuri333") & (dataset["code"] == "1001"), "pbr"
    ].iloc[0] == pytest.approx(0.8)
    assert (
        dataset.loc[
            (dataset["index"] == "topix") & (dataset["code"] == "3003"), "sector"
        ].iloc[0]
        == "IT"
    )


def test_metrics_and_logic(sample_files: tuple[Path, Path]) -> None:
    constituents_path, financials_path = sample_files
    dataset = build_canonical(constituents_path, financials_path)

    pbr_metrics = compute_pbr_stats(dataset)
    roe_metrics = compute_roe_stats(dataset)
    dy_metrics = compute_yield_stats(dataset)
    hhi_metrics = compute_concentration_metrics(dataset)

    assert pbr_metrics["lt1"]["yomiuri333"] == pytest.approx(0.5)
    assert roe_metrics["median"]["yomiuri333"] == pytest.approx(4.3, rel=1e-3)
    assert dy_metrics["mean"]["yomiuri333"] == pytest.approx(2.35, rel=1e-3)
    assert hhi_metrics["hhi"]["yomiuri333"] == pytest.approx(0.5)

    logic = derive_logic_summary(pbr_metrics, roe_metrics, dy_metrics, hhi_metrics)
    assert any("PBR" in item for item in logic["strengths"])
    assert any("ROE" in item for item in logic["weaknesses"])
