import asyncio
from pathlib import Path

import pytest

from infrastructure.tv_catalog import MarkdownTVCatalog

REAL_MODELS_MD = Path(__file__).resolve().parents[3] / "prompts" / "models.md"


def test_parses_toml_frontmatter() -> None:
    catalog = MarkdownTVCatalog(REAL_MODELS_MD)
    models = asyncio.run(catalog.all())
    assert len(models) >= 12
    codes = {m.code for m in models}
    # ядро семейств должно быть на месте
    assert "QN90D" in codes
    assert "S95D" in codes
    assert "LS03D" in codes


def test_by_code_case_insensitive(catalog: MarkdownTVCatalog) -> None:
    upper = asyncio.run(catalog.by_code("TEST-A"))
    lower = asyncio.run(catalog.by_code("test-a"))
    mixed = asyncio.run(catalog.by_code("Test-A"))
    assert upper is not None
    assert lower is not None
    assert mixed is not None
    assert upper.code == lower.code == mixed.code == "TEST-A"


def test_by_code_returns_none_for_unknown(
    catalog: MarkdownTVCatalog,
) -> None:
    assert asyncio.run(catalog.by_code("NONEXISTENT")) is None


def test_raises_on_empty_file(tmp_path: Path) -> None:
    bad = tmp_path / "empty.md"
    bad.write_text("# No TOML here, just text.\n", encoding="utf-8")
    with pytest.raises(ValueError, match="TOML-блок не найден"):
        MarkdownTVCatalog(bad)


def test_as_prompt_block_returns_file_content(
    catalog: MarkdownTVCatalog,
) -> None:
    block = asyncio.run(catalog.as_prompt_block())
    assert "TEST-A" in block
    assert "Test Alpha" in block
