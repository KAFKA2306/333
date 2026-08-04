from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_human_readme_has_real_repository_badges() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "github.com/KAFKA2306/333" in readme
    assert "OWNER/REPO" not in readme


def test_generated_template_has_no_fixed_investment_conclusion() -> None:
    template = (ROOT / "docs/templates/README.template.md").read_text(
        encoding="utf-8"
    )
    prohibited = (
        "ディープバリュー要素が強い",
        "低ROE・低モメンタム",
        "相対優位を取りやすい",
    )
    assert not any(text in template for text in prohibited)


def test_uncalculated_pages_status_is_explicit() -> None:
    page = (ROOT / "docs/index.html").read_text(encoding="utf-8")
    assert "現在は未計算です" in page
    assert "N/A" not in page
