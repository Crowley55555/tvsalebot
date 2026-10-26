# План: F7 consent-гейт (ФЗ-152)

Дата: 2026-10-26
Статус: в работе
Владелец/исполнитель: Claude Opus 4.7 (оркестратор) + агент W3
Одобрение: продолжение автономной сессии 2026-10-26 («продолжай разработку согласно плану»).

## Цель

Любой пользователь, пришедший в бот, должен **согласиться с политикой обработки ПДн** до того, как `features/dialog` отправит его реплику в LLM. Это закрывает [CLAUDE.md § П7в](../CLAUDE.md), [00-правила-проекта.md § «Красные линии»](../architecture/00-правила-проекта.md), [idea/mvp.md § 4 этап 5](../idea/mvp.md). Без F7 ссылку на бота никому выдавать нельзя — ни клиенту-магазину, ни тестерам.

## Что входит

- Текст политики `prompts/policy.md` (черновик; ссылку на хостинг укажем в F22 деплое).
- Короткое приветствие `prompts/start_greeting.md`.
- Домен: расширение `domain/ports/context_store.py` методами `grant_consent(telegram_id, policy_version) -> None`, `has_consent(telegram_id) -> bool`.
- Доменная ошибка `ConsentRequired(RuntimeError)` в `domain/ports/consent.py` или `domain/errors.py` (создаю `domain/errors.py` — отдельный файл).
- Фича `features/consent/` с дверью `grant`/`has_consent`.
- `features/dialog/service.py`: до вызова LLM проверяет `has_consent`; если нет — поднимает `ConsentRequired`.
- `api/routes.py`: ловит `ConsentRequired` → `409 { "error": "consent_required", "user_message": "..." }`.
- `api/schemas.py`: расширить `ErrorPayload` или добавить `ConsentRequiredResponse { error, user_message }`.
- Бот: `/start` (приветствие + inline-кнопка «Согласен»), callback-handler сохраняет consent через `POST /chat` → либо отдельный `POST /consent/grant` (решение в плане ниже).
- Бот `bot/handlers/text.py`: при 409 consent_required — показывает кнопку «Согласен».
- Redis-ключ `consent:<telegram_id>` → значение `policy_version` (например `v1-2026-10-26`), TTL такой же как у истории (`REDIS_TTL_SECONDS`).
- Env: `POLICY_VERSION: str = "v1-2026-10-26"`, `PRIVACY_POLICY_URL` уже есть.
- Тесты: без согласия /chat → 409; после consent /chat работает; `FakeLLMClient` не вызывается до consent.

**Решение по API-контракту:** вводим отдельный эндпоинт `POST /consent/grant` вместо впихивания в `POST /chat`. Причина: разделение ответственностей (одна дверь — одно поведение), симметрия с будущим `POST /gdpr/stop` (F8).

## Что не входит (явно отрезано)

- F8 `/stop`, `/удалить_данные`, журнал удалений — отдельный срез вслед за F7.
- F4 каталог моделей.
- F6 полная воронка 10 шагов.
- `data_deletion_log` в Redis — F8.
- Второе согласие на маркетинг — не нужно.
- Хостинг политики на лендосе — F22.

## Фазы

### Фаза 1 — W0: порт + ошибка + схемы (я)
- Добавить в `domain/ports/context_store.py` два метода.
- Новый `domain/errors.py` с `ConsentRequired(RuntimeError)`.
- Экспорт в `domain/__init__.py` и `domain/ports/__init__.py`.
- `api/schemas.py`: `ConsentGrantRequest { telegram_id }`, `ConsentGrantResponse { granted: bool, policy_version: str }`, `ConsentRequiredResponse`.

### Фаза 2 — W3: реализация в Redis+Memory (агент)
- `infrastructure/context/keys.py`: `consent_key(telegram_id) -> f"consent:{telegram_id}"`.
- `RedisContextStore.grant_consent/has_consent`: SET/GET, TTL из `REDIS_TTL_SECONDS`.
- `InMemoryContextStore.grant_consent/has_consent`: dict `_consents: dict[int, str]`.

### Фаза 3 — W2: features/consent + DialogService (я)
- `features/consent/__init__.py` + `service.py` с классом `ConsentService(store, policy_version)`.
- `DialogService.__init__` принимает `consent: ConsentService`; в `handle_user_message` после дедупа и до append — `if not await self._consent.has_consent(telegram_id): raise ConsentRequired`.

### Фаза 4 — W4: prompts/policy.md + prompts/start_greeting.md (я)

### Фаза 5 — W1: api + bot (я)
- `api/routes.py`: `POST /consent/grant` → `ConsentService.grant`; обработчик `ConsentRequired` в `POST /chat` → 409 с payload.
- `composition/container.py`: завести `ConsentService`, передать в `DialogService`.
- `composition/env.py`: `POLICY_VERSION`.
- `bot/handlers/start.py`: отвечает `/start` приветствием + inline-кнопка «Согласен».
- `bot/handlers/callback.py`: обрабатывает callback `consent_grant` → вызывает `POST /consent/grant` → ответ «спасибо, можешь задавать вопросы».
- `bot/handlers/text.py`: при `CoreAPIError(409, "consent_required")` показывает кнопку «Согласен».
- `bot/keyboards.py`: функция `consent_keyboard(policy_url) -> InlineKeyboardMarkup`.
- `bot/core_api_client.py`: метод `grant_consent(telegram_id)`.

### Фаза 6 — тесты (я)
- Интеграционный тест: без consent → 409, LLM не вызван.
- Тест: после /consent/grant → /chat работает нормально.
- Тест: повторный grant идемпотентен.

### Фаза 7 — строка в decisions.md + коммит + пуш

## Риски

- **ПДн.** Теперь без consent не отправляем в LLM — ФЗ-152 ст. 6 закрыта по форме. Текст политики в `prompts/policy.md` — шаблон, не финальная версия. На проде обязательна юридическая вычитка.
- **Идемпотентность grant.** Повторный grant перезаписывает ключ той же value — безопасно.
- **Деньги.** До consent LLM не вызывается — сокращает расход токенов на спам.

## Полномочия

- Автономная сборка, коммит и пуш в конце — продолжение разрешения из начала сессии.
- Политика хоститься пока не будет (F22) — ссылка в сообщении остаётся placeholder (`https://example.com/privacy`), значение из `.env.PRIVACY_POLICY_URL`.
