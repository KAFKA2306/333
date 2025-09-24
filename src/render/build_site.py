"""Generate the static HTML report for GitHub Pages."""

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

from render.common import (  # noqa: E402
    build_environment,
    current_timestamp,
    derive_logic_summary,
    load_metrics,
    safe_get,
    wrap_metrics,
)

LOGGER = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[2]
    default_template = root / "docs" / "templates" / "site.template.html"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template", type=Path, default=default_template)
    parser.add_argument("--out", dest="output", type=Path, required=True)
    parser.add_argument("--pbr", dest="pbr", type=Path)
    parser.add_argument("--roe", dest="roe", type=Path)
    parser.add_argument("--hhi", dest="hhi", type=Path)
    parser.add_argument("--yield", dest="yield_file", type=Path)
    parser.add_argument("--notes", dest="notes", type=Path)
    return parser.parse_args()


def build_insights(
    pbr: dict[str, Any], roe: dict[str, Any], dy: dict[str, Any], hhi: dict[str, Any]
) -> list[str]:
    insights: list[str] = []
    y_ratio = safe_get(pbr, "lt1", "yomiuri333")
    t_ratio = safe_get(pbr, "lt1", "topix")
    if y_ratio is not None and t_ratio is not None:
        diff = (y_ratio - t_ratio) * 100
        direction = "上回" if diff >= 0 else "下回"
        insights.append(
            "バリュー: 読売333のPBR<1比率はTOPIXを"
            f"{abs(diff):.1f}pt{direction}っています。"
        )
    else:
        insights.append("バリュー: PBRデータが不足しているため比較できません。")

    y_roe = safe_get(roe, "median", "yomiuri333")
    t_roe = safe_get(roe, "median", "topix")
    if y_roe is not None and t_roe is not None:
        diff = y_roe - t_roe
        descriptor = "低い" if diff < 0 else "高い"
        insights.append(
            "収益性: 読売333のROE中央値はTOPIXより"
            f"{descriptor}水準({y_roe:.2f} vs {t_roe:.2f})です。"
        )
    else:
        insights.append("収益性: ROE中央値の比較ができません。")

    y_dy = safe_get(dy, "mean", "yomiuri333")
    t_dy = safe_get(dy, "mean", "topix")
    if y_dy is not None and t_dy is not None:
        diff = y_dy - t_dy
        descriptor = "高い" if diff >= 0 else "低い"
        insights.append(
            "インカム: 読売333の配当利回り平均はTOPIXより"
            f"{descriptor}水準({y_dy:.2f}% vs {t_dy:.2f}%)です。"
        )
    else:
        insights.append("インカム: 配当利回りデータが不足しています。")

    y_hhi = safe_get(hhi, "hhi", "yomiuri333")
    if y_hhi is not None:
        insights.append(
            "集中度: HHIは"
            f"{y_hhi:.3f}で、均等分散(1/333)と比べると集中リスクを把握できます。"
        )
    else:
        insights.append("集中度: セクター情報が不足しています。")

    return insights


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()

    env = build_environment(args.template, enable_autoescape=True)
    template = env.get_template(args.template.name)

    pbr_metrics = load_metrics(args.pbr)
    roe_metrics = load_metrics(args.roe)
    hhi_metrics = load_metrics(args.hhi)
    dy_metrics = load_metrics(args.yield_file)

    logic = derive_logic_summary(pbr_metrics, roe_metrics, dy_metrics, hhi_metrics)
    context: dict[str, Any] = {
        "updated_at": current_timestamp(),
        "pbr": wrap_metrics(pbr_metrics),
        "roe": wrap_metrics(roe_metrics),
        "hhi": wrap_metrics(hhi_metrics),
        "dy": wrap_metrics(dy_metrics),
        "insights": build_insights(pbr_metrics, roe_metrics, dy_metrics, hhi_metrics),
        "logic": logic,
        "notes": None,
    }

    if args.notes and args.notes.exists():
        context["notes"] = args.notes.read_text(encoding="utf-8")

    rendered = template.render(**context)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    LOGGER.info("Site generated at %s", args.output)


if __name__ == "__main__":
    main()
