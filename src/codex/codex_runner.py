"""Optional integration with OpenAI's APIs to refresh commentary."""

# ruff: noqa: I001

from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path
from typing import Any

import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
LOGGER = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--prompt", type=Path, required=True, help="Prompt template file"
    )
    parser.add_argument(
        "--out",
        dest="output",
        type=Path,
        required=True,
        help="Destination markdown file",
    )
    parser.add_argument("--model", default="gpt-4o-mini", help="OpenAI model name")
    parser.add_argument("--temperature", type=float, default=0.2)
    return parser.parse_args()


def load_prompt(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8")


def _call_openai(prompt: str, model: str, temperature: float) -> str | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        LOGGER.warning("OPENAI_API_KEY is not configured; skipping Codex refresh.")
        return None

    try:
        from openai import OpenAI
    except ImportError:
        LOGGER.warning("openai package is not installed; skipping Codex refresh.")
        return None

    client = OpenAI()
    try:
        response = client.responses.create(
            model=model, input=prompt, temperature=temperature
        )
    except Exception as exc:  # noqa: BLE001
        LOGGER.error("OpenAI API call failed: %s", exc)
        return None

    if hasattr(response, "output_text"):
        return str(response.output_text)

    choices: Any = getattr(response, "choices", None)
    if isinstance(choices, list):
        texts: list[str] = []
        for choice in choices:
            message = getattr(choice, "message", None)
            if message and getattr(message, "content", None):
                texts.append(str(message.content))
        if texts:
            return "\n".join(texts)

    return str(response)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()
    prompt_text = load_prompt(args.prompt)
    LOGGER.info("Submitting prompt to OpenAI model %s", args.model)
    output = _call_openai(prompt_text, args.model, args.temperature)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    if output:
        args.output.write_text(output, encoding="utf-8")
        LOGGER.info("Codex notes updated at %s", args.output)
    else:
        placeholder = (
            "## Codex refresh unavailable\n\n"
            "自動生成コメントは現在利用できません。OPENAI_API_KEYの設定やネットワーク状態を確認してください。\n"
        )
        args.output.write_text(placeholder, encoding="utf-8")
        LOGGER.info("Wrote placeholder notes to %s", args.output)


if __name__ == "__main__":
    main()
