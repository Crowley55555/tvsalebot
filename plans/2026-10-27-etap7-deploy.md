# План: Этап 7 — реальный деплой РФ + NL

Дата: 2026-10-27
Статус: в работе
Владелец и исполнитель: Артём + Claude (оркестратор) + deploy-агент
Одобрение: пользователь, 2026-10-27, «делай деплой проводи тесты. .env скопируй на сервер из корня проекта путем команды в терминале, сам в него не смотри.»

## Контекст
- Коммит для деплоя: `69a1cb4` (feat(deploy): Этап-7-local), запушен в `origin/main` (github.com/Crowley55555/tvsalebot — публичный репо).
- РФ-сервер: `root@153.80.246.243` (Ubuntu 24.04 LTS, Docker 29.9.1, compose v5.6.0, 1.9Gi RAM, 22GB free).
- NL-сервер: `root@78.17.117.189` (Ubuntu 24.04.5 LTS, Docker 29.8.1, compose v5.5.1, 1.9Gi RAM, 7.3GB free).
- Домена нет → работаем по IP, без SSL/certbot на этом срезе.
- `.env` в корне локального проекта содержит рабочие BOT_TOKEN + GIGACHAT_API_KEY (пользователь настроил сам). Копируем через `scp`, не читаем.

## Границы и полномочия
- **Разрешено:** SSH на оба сервера под root (ключи у пользователя настроены), git clone/pull из публичного github, scp .env (без чтения), sed-замена значений в .env на серверах (ENVIRONMENT=prod, REDIS_URL, CORE_API_URL), `docker compose up -d --build`, `ufw` правила, `curl` для health-тестов.
- **Запрещено:** читать .env (ни `cat`, ни `grep` на значения, только имена и `sed -i`), трогать идеи/архитектуру, менять код в репо.
- **П6-санкция:** первая прод-эксплуатация LLM GigaChat — пользователь явно разрешил «делай деплой». Прод-инвариант П7-б форсится валидатором в AppSettings (при `ENVIRONMENT=prod` → `LLM_PROVIDER ∈ {gigachat, yandex}`, текущий Literal — только `gigachat`).

## Архитектура
- **РФ (153.80.246.243):** `redis` + `api` поднимаются через `docker compose -f deploy/docker-compose.yml up -d redis api`. Порт api — `0.0.0.0:8000:8000` (overrider через sed, чтобы доступ был не только с localhost). Firewall ufw: 22/tcp все, 80/tcp все, 8000/tcp только с NL IP.
- **NL (78.17.117.189):** только `bot` через `docker compose up -d --no-deps bot`. CORE_API_URL в .env → `http://153.80.246.243:8000`. Исходящие свободные. Firewall ufw: 22/tcp все.
- Nginx + SSL — в этом срезе пропускаем (нет домена). Можно добавить позже под `UptimeRobot` + custom domain.

## Фазы

### Фаза 1 — РФ-сервер
- `ssh root@153.80.246.243 "mkdir -p /opt/tvsalebot && cd /opt/tvsalebot && git clone https://github.com/Crowley55555/tvsalebot.git . || git pull origin main"`.
- `scp .env root@153.80.246.243:/opt/tvsalebot/.env` (локальный .env → сервер).
- `ssh root@153.80.246.243` — sed:
  - `sed -i 's|^ENVIRONMENT=.*|ENVIRONMENT=prod|' /opt/tvsalebot/.env`
  - `sed -i 's|^REDIS_URL=.*|REDIS_URL=redis://redis:6379/0|' /opt/tvsalebot/.env`
- Overrider `0.0.0.0`: `sed -i 's|127.0.0.1:8000:8000|0.0.0.0:8000:8000|' /opt/tvsalebot/deploy/docker-compose.yml`.
- `docker compose -f /opt/tvsalebot/deploy/docker-compose.yml --env-file /opt/tvsalebot/.env up -d --build redis api`.
- Ждём healthcheck (до 2 минут), `curl -fsS http://127.0.0.1:8000/health`.
- Firewall: `ufw allow 22/tcp; ufw allow 80/tcp; ufw allow from 78.17.117.189 to any port 8000 proto tcp; ufw --force enable`.
- **Приёмка фазы:** `curl http://127.0.0.1:8000/health` → `{"status":"ok","redis":"ok"}`.

### Фаза 2 — NL-сервер
- `ssh root@78.17.117.189 "mkdir -p /opt/tvsalebot && cd /opt/tvsalebot && git clone https://github.com/Crowley55555/tvsalebot.git . || git pull origin main"`.
- `scp .env root@78.17.117.189:/opt/tvsalebot/.env`.
- sed:
  - `sed -i 's|^ENVIRONMENT=.*|ENVIRONMENT=prod|' /opt/tvsalebot/.env`
  - `sed -i 's|^CORE_API_URL=.*|CORE_API_URL=http://153.80.246.243:8000|' /opt/tvsalebot/.env`
- `docker compose -f /opt/tvsalebot/deploy/docker-compose.yml --env-file /opt/tvsalebot/.env up -d --build --no-deps bot`.
- `docker logs <bot-container> 2>&1 | tail -20` — должно быть `bot_started env=prod core_api=http://153.80.246.243:8000`.
- Firewall: `ufw allow 22/tcp; ufw --force enable`.
- **Приёмка фазы:** лог бота показывает подключение к Telegram без ошибок.

### Фаза 3 — тесты
- С NL: `curl -fsS http://153.80.246.243:8000/health` → 200.
- Опциональный ручной smoke: пользователь пишет боту в Telegram, бот отвечает (без консента — вернёт 409 с policy_url, пользователь нажимает «Согласен», шлёт сообщение, бот отвечает через GigaChat).
- Проверить что `/health` снаружи **недоступен** с левого IP (iptables ACL проверит).

### Фаза 4 — отчёт + строка в decisions.md
- Оркестратор впишет строку о срезе Этап-7-deploy.
- План финализируется с итогом.

## Checkpoint
- До начала: коммит `69a1cb4` в origin/main, pytest 21/21.
- Активные локальные процессы: Redis `tvsalebot-redis` + uvicorn :8000 (локальные dev-процессы, трогать не нужно, никак не связаны с прод-деплоем).

## Условия остановки
- SSH-доступ пропал → остановиться, доложить.
- GigaChat API ошибку возвращает (ключ не рабочий / сеть) → остановиться, доложить, не вливать пустой compose в loop.
- Firewall заблокировал сам ssh → паника, но у пользователя есть панель провайдера для отката.

## Откат
- `docker compose -f /opt/tvsalebot/deploy/docker-compose.yml down -v` на обоих серверах.
- `ufw disable` на обоих.
- Удаление `/opt/tvsalebot/` — опционально.

## Итог

- **Реализовано целиком:** да (фазы 1–3 деплой + E2E smoke на реальном GigaChat).
- **Что работает и чем подтверждено:**
  - РФ `/health` → `{"status":"ok","redis":"ok"}` (локально на РФ и с NL).
  - E2E smoke на тестовом telegram_id=99887766: consent → chat → GigaChat ответил релевантной рекомендацией Crystal UHD DU8000/DU7000 с правилом «не QLED» (F11 правило честности живое) → gdpr/stop удалил 2 ключа.
  - Bot `@tvsalebot_bot` на NL в polling-режиме (`Start polling` в логах).
  - Firewall: порт 8000 на РФ открыт **только** с 78.17.117.189 (ufw + iptables DOCKER-USER); с левого IP — timeout. iptables-persistent сохранил правила на ребут.
- **Процесс:** оркестратор → план → deploy-агент (детальный отчёт с проблемами, не скрывал) → судья проверил критическое (iptables-persistent + E2E smoke) → приёмка.
- **Технический долг (документирован в decisions.md):**
  1. `deploy/.env -> ../.env` симлинк на обоих серверах (обход `env_file: path: .env` относительного пути).
  2. `0.0.0.0:8000:8000` правлен `sed`-ом на РФ, при `git reset --hard` затрётся — надо исправить в репо через `${API_BIND:-127.0.0.1}:8000:8000`.
  3. HTTPS/certbot пропущен — нет домена. Работаем по IP+HTTP, UptimeRobot пингует по IP.
  - Все три фикса — следующим срезом «Этап-7-polish» по команде пользователя.
- **Остаточные риски:**
  - `GIGACHAT_API_KEY` сейчас работает на Freemium 40 млн токенов/год — следим за расходом (бюджет-счётчик — F12, не в этом срезе).
  - При очередном `git reset --hard` на РФ правка compose исчезнет — сервис не отвалится до перезапуска, но при ребуте порт переедет на localhost и `curl` с NL начнёт тайм-аутить.
- **Что ждёт пользователя:**
  - Ручной тест: открыть `@tvsalebot_bot` в Telegram, нажать `/start`, согласиться с ПДн, задать вопрос про ТВ, проверить что бот отвечает.
  - Если ответ ok — Этап 7 полностью закрыт. Если нет — вернуться к deploy-агенту с конкретной ошибкой.
