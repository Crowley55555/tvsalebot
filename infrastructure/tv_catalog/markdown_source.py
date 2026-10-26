"""Markdown-источник каталога Samsung TV.

Читает `prompts/models.md` один раз при инициализации:
- вытаскивает TOML-блок (между ```toml и ```),
- парсит через `tomllib.loads` → строит `list[TVModel]`,
- сохраняет оригинальный markdown-текст для вставки в system-prompt LLM.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

from domain.entities import TVModel

_TOML_BLOCK_RE = re.compile(r"```toml\s*\n(.*?)\n```", re.DOTALL)


class MarkdownTVCatalog:
    """Каталог Samsung TV из markdown-файла с TOML-frontmatter.

    Файл читается один раз в `__init__`. На промахе формата кидает
    `ValueError` с понятным сообщением.
    """

    def __init__(self, path: Path) -> None:
        self._path = path
        self._raw_text = path.read_text(encoding="utf-8")

        match = _TOML_BLOCK_RE.search(self._raw_text)
        if match is None:
            raise ValueError(
                f"{path}: TOML-блок не найден или пуст"
            )
        toml_text = match.group(1).strip()
        if not toml_text:
            raise ValueError(
                f"{path}: TOML-блок не найден или пуст"
            )

        try:
            data = tomllib.loads(toml_text)
        except tomllib.TOMLDecodeError as e:
            raise ValueError(
                f"{path}: не удалось распарсить TOML-блок: {e}"
            ) from e

        raw_models = data.get("models")
        if not raw_models:
            raise ValueError(
                f"{path}: TOML-блок не найден или пуст"
            )

        self._models: list[TVModel] = [TVModel(**m) for m in raw_models]
        self._by_code: dict[str, TVModel] = {
            m.code.lower(): m for m in self._models
        }

    async def all(self) -> list[TVModel]:
        return list(self._models)

    async def by_code(self, code: str) -> TVModel | None:
        return self._by_code.get(code.lower())

    async def as_prompt_block(self) -> str:
        """Вернуть исходный markdown-текст файла как есть.

        LLM получает человекочитаемые описания + TOML со спеками в одном
        блоке — так же, как видит редактор в `prompts/models.md`.
        """
        return self._raw_text
