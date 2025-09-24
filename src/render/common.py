"""Shared helpers for rendering Markdown and HTML outputs."""

from __future__ import annotations

import json
import logging
import math
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2.runtime import Undefined

LOGGER = logging.getLogger(__name__)


def is_missing(value: Any) -> bool:
    if isinstance(value, Undefined):
        return True
    if isinstance(value, MissingValue):
        return True
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    return False


def format_number(value: Any, digits: int = 2) -> str:
    if is_missing(value):
        return "N/A"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    return f"{number:.{digits}f}"


def format_percent(value: Any, digits: int = 1) -> str:
    if is_missing(value):
        return "N/A"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if number <= 1:
        number *= 100
    return f"{number:.{digits}f}%"


def load_metrics(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    if not path.exists():
        LOGGER.warning("Metrics file not found: %s", path)
        return {}
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def resolve_badges() -> dict[str, dict[str, str]]:
    repository = os.getenv("GITHUB_REPOSITORY", "OWNER/REPO")
    ci_url = f"https://github.com/{repository}/actions/workflows/ci.yml"
    pages_url = f"https://github.com/{repository}/actions/workflows/pages.yml"
    return {
        "ci": {
            "image": f"{ci_url}/badge.svg",
            "link": ci_url,
        },
        "pages": {
            "image": f"{pages_url}/badge.svg",
            "link": pages_url,
        },
    }


def build_environment(
    template_path: Path, enable_autoescape: bool = False
) -> Environment:
    autoescape = select_autoescape(
        enabled_extensions=("html", "xml"), default=enable_autoescape
    )
    env = Environment(
        loader=FileSystemLoader(str(template_path.parent)), autoescape=autoescape
    )
    env.filters["format_number"] = format_number
    env.filters["format_percent"] = format_percent
    return env


def current_timestamp() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")


def safe_get(data: Any, *keys: str) -> Any:
    cursor = data
    for key in keys:
        if not isinstance(cursor, dict):
            return None
        cursor = cursor.get(key)
        if cursor is None:
            return None
    return cursor


def derive_logic_summary(
    pbr: dict[str, Any],
    roe: dict[str, Any],
    dy: dict[str, Any],
    hhi: dict[str, Any],
) -> dict[str, list[str]]:
    strengths: list[str] = []
    weaknesses: list[str] = []
    cautions: list[str] = []

    y_ratio = safe_get(pbr, "lt1", "yomiuri333")
    t_ratio = safe_get(pbr, "lt1", "topix")
    if y_ratio is not None and t_ratio is not None:
        diff = y_ratio - t_ratio
        if diff > 0:
            strengths.append(
                "PBR<1銘柄比率がTOPIXより"
                f"{diff * 100:.1f}pt高く、バリュー再評価の恩恵を受けやすい構造です。"
            )
        else:
            weaknesses.append(
                "PBR<1銘柄比率がTOPIX比で"
                f"{abs(diff) * 100:.1f}pt低く、ディープバリュー特性は限定的です。"
            )
    else:
        cautions.append(
            "PBRデータが不足しており、バリュー特性の検証に不確実性があります。"
        )

    y_roe = safe_get(roe, "median", "yomiuri333")
    t_roe = safe_get(roe, "median", "topix")
    if y_roe is not None and t_roe is not None:
        diff = y_roe - t_roe
        if diff >= 0:
            strengths.append(
                "ROE中央値がTOPIXと同等以上("
                f"{y_roe:.2f} vs {t_roe:.2f})で、低ROEバイアスが軽減されています。"
            )
        else:
            weaknesses.append(
                "ROE中央値がTOPIX比で"
                f"{abs(diff):.2f}ポイント低く、資本効率面での逆風が想定されます。"
            )
    else:
        cautions.append("ROE指標の欠損があり、収益性評価には注意が必要です。")

    y_dy = safe_get(dy, "mean", "yomiuri333")
    t_dy = safe_get(dy, "mean", "topix")
    if y_dy is not None and t_dy is not None:
        diff = y_dy - t_dy
        if diff >= 0:
            strengths.append(
                "配当利回り平均がTOPIXを"
                f"{diff:.2f}pt上回り、インカム面の魅力を維持しています。"
            )
        else:
            weaknesses.append(
                "配当利回り平均がTOPIXを"
                f"{abs(diff):.2f}pt下回り、インカム補完機能は限定的です。"
            )
    else:
        cautions.append(
            "配当利回りデータが欠落しており、インカム特性の評価が難しい状況です。"
        )

    y_hhi = safe_get(hhi, "hhi", "yomiuri333")
    t_hhi = safe_get(hhi, "hhi", "topix")
    if y_hhi is not None:
        if t_hhi is not None and y_hhi > t_hhi:
            weaknesses.append(
                "セクターHHIがTOPIX("
                f"{t_hhi:.3f})より高く({y_hhi:.3f})、集中度リスクが相対的に大きいです。"
            )
        else:
            strengths.append(
                "セクターHHIが"
                f"{y_hhi:.3f}で、等ウェート設計による分散効果が確認できます。"
            )
    else:
        cautions.append("セクター情報不足により集中度のトレースが困難です。")

    top10 = safe_get(hhi, "top10_weight", "yomiuri333")
    if top10 is None:
        cautions.append(
            "上位構成比データが欠損しており、個別銘柄集中の検証に制約があります。"
        )

    return {
        "strengths": strengths,
        "weaknesses": weaknesses,
        "cautions": cautions,
    }


class MissingValue:
    """Sentinel returned when metrics are unavailable."""

    def __getattr__(self, _item: str) -> MissingValue:
        return self

    def __getitem__(self, _item: str) -> MissingValue:
        return self

    def __bool__(self) -> bool:
        return False

    def __str__(self) -> str:
        return ""


class MetricAccessor:
    """Helper that enables safe dot access inside Jinja templates."""

    def __init__(self, data: dict[str, Any] | None):
        self._data = data or {}

    def __getattr__(self, item: str) -> Any:
        value = self._data.get(item)
        if isinstance(value, dict):
            return MetricAccessor(value)
        if value is None:
            return MissingValue()
        return value

    def __getitem__(self, item: str) -> Any:
        return self.__getattr__(item)

    def to_dict(self) -> dict[str, Any]:
        return self._data


def wrap_metrics(data: dict[str, Any] | None) -> MetricAccessor:
    return MetricAccessor(data)
