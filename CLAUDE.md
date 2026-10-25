# tvsalebot — вход для Claude Code

AI-консультант по продаже телевизоров Samsung в Telegram (демо-MVP для одного клиента-магазина, цель — получить контракт на полноценную разработку). Два сервиса в одном репо: Core API (FastAPI) + Telegram-обёртка (aiogram 3.x), LLM — GigaChat 2 Pro, контекст — Redis.

---

## 1. Что читать перед каждой задачей (жёстко)

Перед **любой** правкой кода, промпта или архитектурного решения прочитай нужные части:

- [architecture/README.md](architecture/README.md) — оглавление архитектуры. Код пишется строго по [architecture/](architecture/).
- [architecture/00-правила-проекта.md](architecture/00-правила-проекта.md) — правила П1–П7 ниже. Это закон.
- [architecture/05-стек.md](architecture/05-стек.md) — что из технологий и почему; какие порты и адаптеры.
- [architecture/08-структура-кода.md](architecture/08-структура-кода.md) — какая папка за что отвечает, карта владения.
- [architecture/decisions.md](architecture/decisions.md) — журнал решений; каждое изменение туда одной строкой (правило П5).
- [idea/](idea/) — замысел, принципы и ограничения; читай нужные файлы, не всё подряд.

**Правило:** замысел живёт в [idea/](idea/), архитектура — в [architecture/](architecture/). Эти папки — источник решений. При конфликте требования пользователя с ними — явно укажи конфликт и спроси, что менять. **Не трогать** `idea/` и `architecture/` без явного запроса — это проработано ранее.

Процесс работы и чек-пойнты — [.starter/workflow.md](.starter/workflow.md) (единый процесс для Claude и Codex). Для крупных задач: [plans/TEMPLATE.md](plans/TEMPLATE.md), ретро — [retrospectives/TEMPLATE.md](retrospectives/TEMPLATE.md).

Приватный бизнес-контекст: [.business/INDEX.md](.business/INDEX.md) (локально, вне git). Полный контекст по фрилансу — `C:/Users/lavro/OneDrive/Документы/GitHub/freelance/.business/INDEX.md`.

---

## 2. Стек (кратко)

Полностью — в [architecture/05-стек.md](architecture/05-стек.md). Ничего нового в стек не добавлять без «ок» (правило П6).

- Python 3.11+, FastAPI + Pydantic v2 + Uvicorn, aiogram 3.x.
- Redis 7 (контекст, лок, бюджет). БД — PostgreSQL появится только на проде, после первого контракта.
- LLM: GigaChat 2 Pro (Freemium) — default; YandexGPT 5 Pro — fallback; OpenRouter — **только dev** с анонимными данными.
- Хостинг схема B: aiogram + Core API + Redis на РФ-сервере; NL-сервер — SOCKS5-прокси к `api.telegram.org`. ПДн граждан РФ не покидают РФ-контур.
- Разработка: ruff, mypy, pytest.
- PostToolUse-хук после Edit/Write (`.starter/post_edit.sh`) гонит ruff + mypy + pytest, когда код появится.

---

## 3. Карта папок

```
api/              Вход через HTTP (FastAPI). POST /chat, /reset, /gdpr/stop, GET /health.
bot/              Вход через Telegram (aiogram). Только транспорт, никакой бизнес-логики и промптов.
features/         Бизнес-фичи: dialog/, consent/, deletion/, recommendation/, b2b/. Одна фича — одна папка — одна дверь (__init__.py).
domain/           Сущности, value objects, ошибки, порты (Protocol). Не импортирует инфраструктуру.
infrastructure/   Адаптеры к внешним сервисам: llm/, context/, alerting/, tv_catalog/. Один файл = один вендор.
composition/      DI-контейнер + единая точка чтения env (pydantic-settings).
prompts/          Все тексты, промпт, спеки 12–14 моделей ТВ, политика ПДн. Правка не требует релиза.
scripts/          Служебные скрипты: smoke_llm, smoke_api, test_scenarios, sweep_abandoned (прод).
tests/            unit/ + integration/, зеркалят код.
landing/          Одностраничник (6-й этап mvp.md).
architecture/     Архитектура проекта. Канонический источник для кода.
idea/             Замысел, принципы, риски, MVP, deep-research.
plans/            План(ы) результата по шаблону. Один план — один согласованный результат.
retrospectives/   Короткие ретро после каждой сессии.
.business/        Приватный бизнес-контекст (в .gitignore).
.starter/         Общий процесс (workflow.md) и системные скрипты (check_secrets.py, post_edit.sh).
.claude/          Настройки Claude Code (permissions deny-list, PostToolUse-хук).
.github/hooks/    Образцы git-хуков. Устанавливаются вручную в .git/hooks/.
```

Структура кода подробно — [architecture/08-структура-кода.md](architecture/08-структура-кода.md).

---

## 4. Правила проекта (перенесено из architecture/00-правила-проекта.md)

Полный текст с объяснениями «почему» — в [architecture/00-правила-проекта.md](architecture/00-правила-проекта.md). Ниже — обязательная выжимка. Проверки указаны прямо здесь, чтобы не ходить за ними в соседний файл.

### Всегда делай

- **П1. Бизнес-тексты — вне `.py`.** Системный промпт, роль Samsung-эксперта, спеки 12–14 моделей, цены-вилки, тексты команд, политика — только в `prompts/*.md`, `data/*.yaml` или Redis.
  Проверка: `grep -rE "QN90|S95|Crystal UHD|Dolby Vision|HDMI 2\.1|[0-9]+\s*нит|[0-9]+\s*Hz" api/ bot/ core/ features/ --include="*.py"` — пусто.

- **П2. Внешние сервисы — только через адаптер в `infrastructure/`.** Прямые HTTP/SDK-вызовы к GigaChat/YandexGPT/OpenRouter/Telegram вне `infrastructure/` запрещены.
  Проверка: `grep -rE "requests\.|httpx\.(get|post)|from gigachat|from openai|yandex_cloud_ml_sdk" api/ bot/ features/ domain/ --include="*.py"` — пусто.

- **П3. Core и bot — независимы.** `api/`, `features/`, `domain/` не импортируют `aiogram`. `bot/` не содержит LLM-SDK, промптов, логики воронки.
  Единственное исключение: `infrastructure/alerting/telegram_alert.py` (dev-алерты разработчику) — зафиксировано в decisions.md.

- **П4. Состояние диалога — только в Redis через порт `ContextStore`.** Никаких глобальных `dict[int, …]` по `user_id` на уровне модулей.

- **П5. Каждое архитектурное решение — одна строка в [architecture/decisions.md](architecture/decisions.md).** Смена/добавление провайдера, формата ключей, Pydantic-схем, нового канала, крупная правка промпта, новая платная услуга. Формат: `ГГГГ-ММ-ДД — что меняем — почему`.

### Спроси разрешения, прежде чем (П6)

- Добавить библиотеку вне согласованного стека.
- Подключить нового LLM-провайдера или сменить текущего.
- Изменить место или схему хранения ПДн (новая коллекция ключей, TTL, переезд с Redis).
- Изменить публичный контракт `POST /chat` или `POST /reset`.
- Сделать первый **платный** LLM-вызов (выход за Freemium GigaChat).
- Взять задачу из «после первого контракта» (CRM, каталог, веб-виджет, админка, A/B).
- Отправить что-либо наружу: push, деплой, ссылка клиенту, лендос, КП.

Форма: краткий план в чате (что меняется, зачем, альтернатива) → ждать явное «ок»/«делай».

### Запрещено (П7)

- **(а) Секреты и приватные файлы — не в индексе git.** `.env`, `.env.local`, `*.key`, `*.pem`, `.business/`, `/uploads`, `/storage`, `screenshots/private/`, `cp/`, `kp/`, `*.log`, медиа вне `landing/assets/`. Перед коммитом — `git status` без этих путей.
  В коде: значения ключей — только через `AppSettings` из переменных окружения.

- **(б) ПДн граждан РФ не покидают РФ-контур в production.** При `ENVIRONMENT=prod` допустимо `LLM_PROVIDER` ∈ {gigachat, yandex}. `openrouter`/`anthropic`/`openai` — только в dev и только на анонимных данных. (ст. 12 ФЗ-152, штраф 150к–миллионы ₽.)

- **(в) Удаление данных пользователя — только по его команде** (`/stop`, `/удалить_данные`), через `features/deletion/delete_user_data(...)`. Факт удаления логируется (`user_id` + `timestamp`), содержимое — нет.

- **(г) Приватный бизнес-контекст не копируется в репо.** Имя клиента-магазина, суммы КП (90/130/170 тыс. ₽), себестоимость, тестеры — не в `prompts/`, не в `landing/`, не в коммит-сообщениях. Эти данные — в `C:/Users/lavro/OneDrive/Документы/GitHub/freelance/.business/`. В этом проекте допустима максимум ссылка на `.business/INDEX.md`.

---

## 5. Как Claude берётся за задачу

1. **Прочитай нужные части** `idea/` и `architecture/` (не всё подряд — то, что относится к задаче).
2. **Сверься с правилами П1–П7.** Если задача требует П6-разрешения — остановись и спроси.
3. **Найди действующий план.** `plans/*.md` или встроенный в архитектуру ([architecture/10-план-реализации.md](architecture/10-план-реализации.md)). Не создавай дубликат.
4. **Реализуй маленькими шагами.** Один файл = одна ответственность. Чужих файлов (вне своей «карты владения» из [architecture/08-структура-кода.md § 5](architecture/08-структура-кода.md)) не трогай.
5. **После правки .py — PostToolUse-хук сам прогонит ruff + mypy + pytest.** Если упало — чини, не выпускай «зелёной» то, что красное.
6. **Любое архитектурное решение → строка в `architecture/decisions.md`** (правило П5).
7. **Коммит — только по явной просьбе пользователя.** Поимённо, без `git add -A`. Push, деплой, публикация — тем более.
8. **Ретро после сессии** — короткое, по [retrospectives/TEMPLATE.md](retrospectives/TEMPLATE.md).

---

## 6. Что уже стоит для защиты

- **pre-commit хук** (`.git/hooks/pre-commit`) — эвристический скан staged-блобов индекса на секреты и запрещённые пути (`.starter/check_secrets.py`). Не блокирует историю; требует Python 3.
- **`.claude/settings.json`** — deny-list: `rm -rf`, `sudo`, `curl|sh`, `git push`, `git reset --hard`, `redis-cli flushall`, `pip install`, чтение `.env*`, `*.pem`, `*.key`, `credentials.json`, `.business/**`, `kp/**`, `cp/**`.
- **PostToolUse-хук** — `.starter/post_edit.sh` после Edit/Write/MultiEdit: ruff → mypy → pytest. Пока `.py` в проекте нет — молча пропускает.
- **`.gitignore`** — секреты, медиа вне `landing/assets/`, `.business/`, `cp/`, `kp/`. Полный список в самом файле и в [architecture/00-правила-проекта.md § «Автоматический механизм для П7»](architecture/00-правила-проекта.md).

---

## 7. Коротко про меня (контекст пользователя)

Python-разработчик (джуниор–мидл), фриланс «AI-автоматизация для малого бизнеса». Ставка — от 1000 ₽/ч, учитывать при оценках и пакетах. Отвечать на русском. Приватный контекст не копировать в репо; `.env` и значения секретов не читать и не выводить — проверять только имена переменных.

Attribution для коммитов и PR, которые ты создаёшь, — из системного напоминания сессии (не хардкодится в этот файл).
