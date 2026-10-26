# План: F4 MarkdownTVCatalog + prompts/models.md

Дата: 2026-10-26
Статус: в работе
Владелец/исполнитель: Claude Opus 4.7 (оркестратор) + агент для реализации
Одобрение: общее «продолжай как оркестратор самостоятельно, принимай те решения что сам рекомендуешь» 2026-10-26.

## Цель и контекст

Без справочника 12–14 моделей со спеками бот отвечает общими словами семейств, демо клиенту-магазину показать нельзя. F4 — ворота ко всем остальным MVP-задачам: F19/F20 (прогон 5 сценариев), F22 (деплой), F23 (QA с внешними тестерами).

Канонический чертёж — [../architecture/](../architecture/). Что уже готово (4 коммита в main):
- F5 Walking Skeleton (HTTP + aiogram + Redis)
- F1+F10 LLM (GigaChat через порт `LLMClient`, `prompts/system.md` с ролью Samsung-эксперта)
- F7 Consent-гейт (ФЗ-152)
- F8 Отзыв+удаление (`/stop`, `/удалить_данные`, журнал удалений)

Этап 4 из [idea/mvp.md § 4](../idea/mvp.md) — «главная работа»: промпт + 12–14 моделей.

## Границы

**Входит:**
- Сущность `TVModel` в `domain/entities.py`.
- Порт `TVCatalog` в `domain/ports/tv_catalog.py` с методами из [architecture/08-структура-кода.md § 3.3](../architecture/08-структура-кода.md): `all() -> list[TVModel]`, `by_code(code) -> TVModel | None`.
- Адаптер `infrastructure/tv_catalog/markdown_source.py` + фабрика `infrastructure/tv_catalog/__init__.py`.
- Контент `prompts/models.md` — 12–14 реальных моделей Samsung 2024 (поколение D) с TOML-frontmatter + человекочитаемый markdown-текст. Правила честности из `prompts/system.md`: Samsung НЕ поддерживает Dolby Vision, Crystal UHD ≠ QLED, разделяем HDR10+/HDR10.
- `DialogService` расширен: принимает `catalog: TVCatalog`, при каждом вызове LLM собирает `system_prompt + "\n\n## Каталог моделей\n\n" + <блок каталога>` и передаёт в `LLMClient.chat`.
- `composition/container.py` строит `MarkdownTVCatalog` и прокидывает в `DialogService`.
- Тесты: 3–5 unit-тестов парсера (`tests/unit/infrastructure/test_markdown_tv_catalog.py`) + интеграционный тест на /chat (проверка, что фрагмент каталога попадает в `system_prompt`).

**Не входит (явно отрезано):**
- `features/recommendation/` — отдельный срез (F6+F11).
- Reranking/релевантность каталога под конкретный запрос — пока передаём весь каталог, 12–14 моделей ≈ 1,5–2k токенов, помещается.
- PostgreSQL-каталог — после первого контракта.
- Правка `prompts/system.md` в части уточнения правил работы с каталогом — минимальная (замена абзаца «Точные характеристики и цены конкретных моделей появятся в отдельном справочнике» на ссылку, что каталог теперь прикрепляется ниже).

**Полномочия:**
- Автономная реализация кода, тесты, строка в `architecture/decisions.md`.
- Коммит и пуш — отдельным явным «ок» от пользователя.
- Новых библиотек нет (`tomllib` — stdlib Python 3.11+, П6-разрешение не нужно).
- Реального вызова GigaChat не делаем — только через `FakeLLMClient` в тестах.

## Принятые архитектурные решения

| Выбор | Из ТЗ | Из архитектуры | Приняли |
|---|---|---|---|
| Файл адаптера | `markdown_catalog.py` | `markdown_source.py` ([08-структура § 2.4](../architecture/08-структура-кода.md)) | `markdown_source.py` — архитектура = закон |
| Методы порта | `list_models()`, `find_by_query(q)` | `all()`, `by_code(code)` ([08-структура § 3.3](../architecture/08-структура-кода.md)) | `all()`, `by_code(code)` |
| Формат `models.md` | не задан | TOML/YAML-frontmatter + markdown ([08-структура § 3.5](../architecture/08-структура-кода.md)) | TOML-frontmatter + markdown (`tomllib`, stdlib) |
| Как каталог попадает в LLM | «фрагмент или весь каталог ≤ 4k токенов» | — | Передаём весь каталог; текстовый блок собирается в `DialogService` поверх `system.md` |

## Фазы

### Фаза 1 — W0-дополнение (контракт)
Правит агент. Критерии:
- `domain/entities.py` расширен классом `TVModel` (pydantic BaseModel) — поля: `code`, `trade_name`, `tv_class`, `diagonals_inches: list[int]`, `refresh_hz`, `brightness_nits_min`, `brightness_nits_max`, `hdmi_version`, `hdmi_ports`, `backlight`, `price_min`, `price_max`, `fits_short`, `honest_caveats`.
- `domain/ports/tv_catalog.py` — `Protocol TVCatalog { all(); by_code(code); }`.
- `domain/ports/__init__.py` — экспорт `TVCatalog`.
- `domain/__init__.py` — экспорт `TVModel`.

### Фаза 2 — W4-контент (`prompts/models.md`)
Правит агент. 12–14 реальных моделей Samsung поколения D (2024). Структура файла:
```md
# Каталог моделей Samsung TV 2024

<TOML-frontmatter в виде ```toml блока с [[models]] массивом>

## <trade_name>

Человекочитаемое описание под LLM (3–5 строк): для какой комнаты, сценария, бюджета.
Честные ограничения (нет Dolby Vision и т.п.).
```

Критерии:
- 12–14 моделей, минимум по одной из каждого семейства system.md (Neo QLED / OLED / QLED / Crystal UHD / The Frame).
- У каждой: честный блок caveats (нет Dolby Vision — везде; Crystal UHD помечен как LED, не QLED).
- Файл валиден: TOML-блок парсится через `tomllib.loads()`, кол-во моделей в TOML = кол-во ##-секций в markdown.

### Фаза 3 — W3-инфра (`MarkdownTVCatalog`)
Правит агент. Критерии:
- `infrastructure/tv_catalog/__init__.py` — фабрика `build_tv_catalog(settings) -> TVCatalog`.
- `infrastructure/tv_catalog/markdown_source.py` — `MarkdownTVCatalog(path: Path)`:
  - В `__init__` читает файл один раз, парсит TOML-блок через `tomllib.loads`, строит `list[TVModel]`, индексирует по `code`.
  - Хранит оригинальный markdown-текст (всё, что между моделями) — чтобы `DialogService` мог вставить человекочитаемый блок в LLM-prompt.
  - Добавить публичный метод `as_prompt_block() -> str` (возвращает markdown-блок с заголовком «## Каталог моделей» для LLM) — это не часть порта `TVCatalog`, а публичный метод конкретного адаптера. **Нет**, лучше в DialogService самостоятельно формировать блок из `catalog.all()`.
  - Хм, но тогда теряется человекочитаемый блок. Решение: добавить метод `as_prompt_block()` в порт `TVCatalog`. Это атрибут контракта.
- Тесты (3–5): парсит TOML; кидает `ValueError` на пустой/битый файл; `by_code()` возвращает `None` для несуществующего кода; `by_code()` регистронезависимо; `all()` сохраняет порядок из файла.

### Фаза 4 — W2 + W1 (`DialogService` + контейнер)
Правит агент. Критерии:
- `DialogService.__init__` принимает `catalog: TVCatalog` (новый параметр, обязательный).
- При вызове `handle_user_message` — собирает `full_system_prompt = self._system_prompt + "\n\n" + self._catalog.as_prompt_block()` (блок каталога идёт после системного промпта).
- `composition/container.py` строит `MarkdownTVCatalog(settings.PROMPTS_DIR / "models.md")` и передаёт в `DialogService`.
- Обновлены `tests/conftest.py` fixtures: добавлен `catalog` (с 2–3 тестовыми моделями), `dialog_service` принимает `catalog`.

### Фаза 5 — тесты и приёмка
Правит агент. Критерии:
- `tests/unit/infrastructure/test_markdown_tv_catalog.py` — 3–5 unit-тестов парсера.
- `tests/integration/test_api_chat_llm.py` — существующие 4 теста остаются зелёными; добавлен 5-й: `test_catalog_is_included_in_system_prompt` (ассерт, что в `fake_llm.calls[0]["system_prompt"]` присутствует код из тестового каталога, например `TEST-MODEL-A`).
- Все остальные интеграционные тесты (`test_consent_gate.py`, `test_gdpr_stop.py`) остаются зелёными — ничего в их логике не меняли.
- Греп правило П1: `grep -rE "QN90|S95|HDMI 2\.1|нит|Hz|Crystal UHD" api/ bot/ features/ domain/ composition/ --include="*.py"` — пусто. Эти слова только в `prompts/models.md`, `prompts/system.md`, `tests/*` (тесты про поведение, не про бизнес-строки).
- Греп правило П2: `grep -rE "tomllib|from pathlib" features/ api/ bot/ domain/ --include="*.py"` — только в `composition/` и `infrastructure/`.
- `ruff check . && mypy . && pytest -q` — зелёные.

### Фаза 6 — строка в `architecture/decisions.md`
Правит оркестратор (не агент). Форматом из П5.

## Риски и защита

- **П6-риск: `tomllib`.** `tomllib` входит в stdlib Python 3.11+. `pyproject.toml` требует Python 3.11+. **Разрешение не нужно.**
- **П6-риск: расширение порта.** Порт `TVCatalog` новый, но его структура уже зафиксирована в [architecture/08-структура-кода.md § 3.3](../architecture/08-структура-кода.md) ещё 2026-10-25 (`all()` + `by_code(code)`). **Разрешение не нужно**, только строка в decisions.md (П5).
- **П6-риск: расширение DialogService (контракт).** Публичный контракт `POST /chat` не меняется — ChatRequest/ChatResponse те же. Меняется только внутренний конструктор `DialogService`. **Разрешение не нужно**.
- **Деньги.** Реальных LLM-токенов не тратим — только FakeLLMClient в тестах.
- **ПДн.** Каталог — не ПДн, обычный Samsung-прайс. Проблем нет.
- **Честность каталога.** Правила честности из system.md: нет Dolby Vision, Crystal UHD не QLED, HDR10+/HDR10 разделять. Агенту явно напомнить.

## Чекпойнт

После каждой фазы агент сообщает статус. Коммит — в конце одной порцией по явному «ок» пользователя.

## Итоговая приёмка

- [ ] 12–14 моделей в `prompts/models.md` с TOML-frontmatter.
- [ ] Порт `TVCatalog` + адаптер `MarkdownTVCatalog`.
- [ ] `DialogService` прокидывает каталог в system-prompt.
- [ ] Все интеграционные тесты (12 было + 1 новый = 13) зелёные.
- [ ] Greps П1/П2 чистые.
- [ ] Строка в `architecture/decisions.md`.
