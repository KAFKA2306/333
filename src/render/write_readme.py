"""Render the project README from the Jinja template and metric files."""
# ruff: noqa: I001

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any

import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from render.common import (  # noqa: E402
    build_environment,
    current_timestamp,
    derive_logic_summary,
    load_metrics,
    resolve_badges,
    wrap_metrics,
)

LOGGER = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--out", dest="output", type=Path, required=True)
    parser.add_argument("--pbr", dest="pbr", type=Path)
    parser.add_argument("--roe", dest="roe", type=Path)
    parser.add_argument("--hhi", dest="hhi", type=Path)
    parser.add_argument("--yield", dest="yield_file", type=Path)
    parser.add_argument("--notes", dest="notes", type=Path)
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()

    env = build_environment(args.template, enable_autoescape=False)
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
        "logic": logic,
        "badges": resolve_badges(),
        "notes": None,
    }

    if args.notes and args.notes.exists():
        context["notes"] = args.notes.read_text(encoding="utf-8")

    rendered = template.render(**context)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered.strip() + "\n", encoding="utf-8")
    LOGGER.info("README generated at %s", args.output)


if __name__ == "__main__":
    main()
