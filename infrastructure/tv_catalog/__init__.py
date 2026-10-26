"""Адаптеры порта `TVCatalog` + фабрика.

Публичный интерфейс пакета:
- `build_tv_catalog(settings)` — фабрика, строит `MarkdownTVCatalog` из
  `settings.PROMPTS_DIR / "models.md"`.
- `MarkdownTVCatalog` — реализация порта `TVCatalog` поверх markdown-файла
  с TOML-блоком спеков.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .markdown_source import MarkdownTVCatalog

if TYPE_CHECKING:
    from composition.env import AppSettings
    from domain.ports.tv_catalog import TVCatalog


__all__ = ["build_tv_catalog", "MarkdownTVCatalog"]


def build_tv_catalog(settings: AppSettings) -> TVCatalog:
    """Собрать основной каталог Samsung TV из `prompts/models.md`."""
    return MarkdownTVCatalog(settings.PROMPTS_DIR / "models.md")
