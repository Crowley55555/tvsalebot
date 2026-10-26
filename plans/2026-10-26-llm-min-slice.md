# План: минимальный LLM-срез (F1 + F10)

Дата: 2026-10-26
Статус: в работе
Владелец/исполнитель: Claude Opus 4.7 (оркестратор) + агент W3
Одобрение: общее «продолжай разработку согласно плану» 2026-10-26; GigaChat Freemium — согласованный стек ([05-стек.md § «ИИ-модель»](../architecture/05-стек.md)), новых библиотек вне стека нет, П6-разрешение не требуется.

## Цель и контекст

Подменить эхо-счётчик из F5 на реальный вызов GigaChat 2 Pro Freemium через порт `LLMClient`. Воронка пока живёт в системном промпте (как советует [mvp.md § 4 этап 4](../idea/mvp.md)), не в коде. Это выполняет Этап 2 из [mvp.md § 4](../idea/mvp.md) без consent-гейта (F7 — следующий срез).

Канонический чертёж — [architecture/](../architecture/). Что уже готово — F5 Walking Skeleton (commit `c07fd73`): HTTP+aiogram+Redis-транспорт.

## Границы

**Входит:**
- Порт `LLMClient` + сущность `ChatResult` в `domain/`.
- Адаптеры `infrastructure/llm/gigachat.py` (httpx OAuth2 + chat) и `infrastructure/llm/fake.py` (для тестов).
- Фабрика `infrastructure/llm/__init__.py` по `LLM_PROVIDER`.
- Минимальный `prompts/system.md` (роль Samsung-эксперта в черновом виде — наращивается в F10/F11).
- `DialogService` переписан под LLM: читает промпт из файла, зовёт `LLMClient.chat`, сохраняет user+assistant в историю.
- Контейнер + `AppSettings` расширены (`GIGACHAT_API_KEY`, `GIGACHAT_SCOPE`, `LLM_MODEL`, `PROMPTS_DIR`).
- Тесты переписаны под `FakeLLMClient` (эхо-тесты удаляются).

**Не входит (явно отрезано):**
- F7 consent-гейт, `/start`-кнопка, `/stop` — следующий срез.
- F6 10-шаговая воронка в коде — живёт в системном промпте.
- F4 каталог 12–14 моделей в `MarkdownTVCatalog` — отдельный срез, пока модели упомянуты в `prompts/system.md` текстом.
- F12 budget-счётчик токенов — пока только логируем `tokens_used`.
- Retry/fallback YandexGPT — F19.
- F16 PII-фильтр перед LLM.
- v0-усечение `ChatRequest/ChatResponse` остаётся (не трогаем).

**Полномочия:**
- Автономная сборка кода, тесты, строка в `decisions.md`.
- Коммит и пуш — отдельным явным «ок» от пользователя.
- Реального вызова GigaChat не делаем — только через `FakeLLMClient` в тестах. Боевой вызов — руками пользователя через `uvicorn + .env`.

## Фазы

### Фаза 1 — W0-дополнение (порт LLMClient + ChatResult)
Делаю сам. Критерий: `grep "from gigachat\|import gigachat" domain/ --include=*.py` пусто.

### Фаза 2 — GigaChatClient (httpx) + FakeLLMClient
Делегирую агенту. Критерии: `GigaChatClient` реализует порт; OAuth-токен кэшируется до `exp - 60s`; таймаут 10 с на chat; `FakeLLMClient` возвращает запрограммированный ответ и фиксирует вызовы.

### Фаза 3 — минимальный `prompts/system.md`
Делаю сам. Критерии: `.md` в `prompts/`; П1-греп по `QN90|S95|нит|Hz` в `.py` пусто.

### Фаза 4 — DialogService + контейнер + env
Делаю сам. Критерии: сервис читает промпт из файла при инициализации, зовёт `self._llm.chat(system, history)`, сохраняет user+assistant.

### Фаза 5 — тесты и приёмка
Делаю сам. Критерии: три интеграционных теста поверх `FakeLLMClient` — зелёные.

### Фаза 6 — строка в `architecture/decisions.md`

## Риски

- **Деньги.** Реальные LLM-токены Freemium (40 млн/год). Защита: `FakeLLMClient` в тестах; `grep "GIGACHAT_API_KEY" tests/` остаётся пустым; боевой запрос — только через `uvicorn` с `.env`.
- **Идемпотентность.** Унаследован дедуп `update_id` из F5. Лок на сессию — F6 (вне scope).
- **ПДн.** Текст пользователя уходит в GigaChat (РФ-контур, [05-стек.md](../architecture/05-стек.md)) — ФЗ-152 не нарушается. Ссылку наружу до F7 (consent) **никому не выдаём** — [CLAUDE.md § П7в](../CLAUDE.md).
- **П1.** Единственное место для «Samsung-эксперт/модели» — `prompts/system.md`; греп по `.py` проверяю.

## Чекпойнт

После каждой фазы — TodoWrite update. Коммит в конце одной порцией.
