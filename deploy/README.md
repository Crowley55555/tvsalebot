# deploy/ — артефакты для развёртывания tvsalebot

## Что это такое

Локальная часть Этапа 7: оффлайн-артефакты для развёртывания MVP. Сам деплой на VPS (покупка домена, установка Let's Encrypt, подключение UptimeRobot, прод-ключи GigaChat) — ЗА пределами репозитория и делается пользователем вручную по инструкции ниже.

Внутри:
- `Dockerfile.api` — образ Core API (FastAPI + Uvicorn).
- `Dockerfile.bot` — образ Telegram-бота (aiogram 3).
- `docker-compose.yml` — связка Redis + Core API + бот для РФ-контура (или локального запуска).
- `nginx/tvsalebot.conf.template` — reverse-proxy с SSL и security-заголовками.
- `systemd/tvsalebot-api.service`, `systemd/tvsalebot-bot.service` — варианты запуска без Docker.

## Прод-инвариант (жёсткий)

Валидатор `AppSettings` в `composition/env.py` требует: при `ENVIRONMENT=prod` разрешены только `LLM_PROVIDER=gigachat` или `LLM_PROVIDER=yandex`. Любые зарубежные провайдеры в проде → приложение не стартует (защита от ФЗ-152, П7-б).

Сейчас `Literal` в коде допускает только `gigachat`; `yandex` разрешён валидатором «на вырост» (отдельная П6-итерация с подключением `YandexGPTClient`).

## Что нужно от пользователя для деплоя

1. **VPS в РФ** (Timeweb/Beget/RUVDS/Reg.ru, ≥2 GB RAM, Ubuntu 22.04/24.04).
2. **Домен** и A-запись → IP VPS.
3. **Прод-ключ GigaChat 2 Pro** (`GIGACHAT_API_KEY`, scope `GIGACHAT_API_PERS`).
4. **Токен Telegram-бота** (`BOT_TOKEN` от @BotFather).
5. **Пароль Redis** (`REDIS_PASSWORD`) — любая случайная строка ≥32 символов.
6. **Bearer-токен Core API** (`CORE_API_BEARER_TOKEN`) — такая же случайная строка; бот ею авторизуется.
7. **Аккаунт UptimeRobot** (бесплатный тариф) — для пинга `https://<domain>/health` раз в 5 минут.
8. (Опционально) второй **NL-сервер** под `bot/` отдельно — только при схеме B с SOCKS5-прокси.

Все значения — только в `.env` файле на VPS, не в репо (`.env` в `.gitignore`, см. П7-а).

## Локальный запуск через compose

```bash
# 1. Корень репо.
cp .env.example deploy/.env     # положить .env РЯДОМ с docker-compose.yml
# заполнить BOT_TOKEN, GIGACHAT_API_KEY, REDIS_PASSWORD, CORE_API_BEARER_TOKEN

# 2. Собрать и запустить.
docker compose -f deploy/docker-compose.yml up --build

# 3. Проверить:
curl -s http://127.0.0.1:8000/health
# -> {"status":"ok","redis":"ok"}
```

Остановить: `docker compose -f deploy/docker-compose.yml down`.
Полный сброс Redis: `docker compose -f deploy/docker-compose.yml down -v` (запрещено на проде — удалит данные пользователей!).

## Деплой на VPS — вариант A (docker compose)

Шаги на свежей Ubuntu 22.04:
```bash
# docker + compose-plugin
sudo apt update && sudo apt install -y docker.io docker-compose-plugin git
sudo systemctl enable --now docker

# код
sudo mkdir -p /opt/tvsalebot && sudo chown $USER /opt/tvsalebot
git clone <ваш-репо> /opt/tvsalebot
cd /opt/tvsalebot

# секреты
cp .env.example deploy/.env
# заполнить деплойные значения (ENVIRONMENT=prod!)

# запуск
docker compose -f deploy/docker-compose.yml up -d --build
docker compose -f deploy/docker-compose.yml ps
curl -s http://127.0.0.1:8000/health
```

Автозапуск при перезагрузке — compose сам поднимет (`restart: unless-stopped`).
Логи: `docker compose -f deploy/docker-compose.yml logs -f api`.

## Деплой на VPS — вариант B (systemd, без Docker)

```bash
sudo adduser --system --group --home /opt/tvsalebot tvsalebot
sudo mkdir -p /opt/tvsalebot /etc/tvsalebot
sudo chown tvsalebot:tvsalebot /opt/tvsalebot

# код + venv
sudo -u tvsalebot git clone <ваш-репо> /opt/tvsalebot
cd /opt/tvsalebot
sudo -u tvsalebot python3.11 -m venv .venv
sudo -u tvsalebot .venv/bin/pip install -e .

# секреты (не в репо!)
sudo cp .env.example /etc/tvsalebot/.env
sudo chmod 600 /etc/tvsalebot/.env
sudo chown tvsalebot:tvsalebot /etc/tvsalebot/.env
# заполнить

# Redis (отдельно, системный)
sudo apt install -y redis-server
# в /etc/redis/redis.conf прописать requirepass <REDIS_PASSWORD>

# systemd юниты
sudo cp deploy/systemd/tvsalebot-api.service /etc/systemd/system/
sudo cp deploy/systemd/tvsalebot-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now tvsalebot-api tvsalebot-bot
sudo systemctl status tvsalebot-api tvsalebot-bot
```

## nginx + Let's Encrypt

```bash
sudo apt install -y nginx certbot python3-certbot-nginx
sudo mkdir -p /var/www/certbot /var/www/tvsalebot/landing

# скопировать лендос, если нужен
sudo cp -r landing/* /var/www/tvsalebot/landing/

# шаблон → реальный конфиг
export DOMAIN=example.ru
envsubst '$DOMAIN' < deploy/nginx/tvsalebot.conf.template | sudo tee /etc/nginx/sites-available/tvsalebot.conf
sudo ln -s /etc/nginx/sites-available/tvsalebot.conf /etc/nginx/sites-enabled/

# сертификат
sudo certbot --nginx -d $DOMAIN --redirect --agree-tos -m you@example.com -n
sudo nginx -t && sudo systemctl reload nginx
```

Авто-продление сертификата — крон certbot уже стоит после `apt install certbot`.

## UptimeRobot (внешний мониторинг)

1. Зарегистрироваться на https://uptimerobot.com (бесплатный тариф — 50 мониторов).
2. Добавить **HTTP(s) Monitor**:
   - URL: `https://<domain>/health`
   - Interval: 5 min
   - Timeout: 30 s
3. Alert Contacts: Email или Telegram-бот @UptimeRobotNotify.
4. При падении `/health` → 503 — пришлёт алерт.

Эндпоинт `/health` публичный, не требует консента, не читает ПДн — безопасно опрашивать снаружи.

## Проверка перед первым прод-деплоем

- [ ] `ENVIRONMENT=prod` в `/etc/tvsalebot/.env` (или в `deploy/.env` для compose).
- [ ] `LLM_PROVIDER=gigachat` (yandex разрешён валидатором, но до появления адаптера не используется).
- [ ] `REDIS_PASSWORD` не пустой, ≥32 символов.
- [ ] `CORE_API_BEARER_TOKEN` не пустой, тот же — в `.env` бота.
- [ ] `curl -s https://<domain>/health` → `{"status":"ok","redis":"ok"}`.
- [ ] Firewall: наружу открыты только 22, 80, 443. Порт 8000 — только `127.0.0.1`.
- [ ] UptimeRobot мониторит `/health` раз в 5 мин.
