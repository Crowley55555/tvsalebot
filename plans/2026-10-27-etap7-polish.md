# План: Этап 7-polish — выжечь техдолг прод-деплоя

Дата: 2026-10-27
Статус: в работе
Владелец и исполнитель: Артём + Claude (оркестратор) + writer-агент + reviewer-агент + deploy-агент
Одобрение: пользователь, 2026-10-27, «Этап-7-polish»

## Контекст

После среза Этап-7-deploy три пункта техдолга зафиксированы в [architecture/decisions.md](../architecture/decisions.md):

1. `deploy/.env -> ../.env` симлинк на обоих серверах (compose не находит `.env` из-за относительного пути `env_file: path: .env`).
2. `127.0.0.1:8000:8000 → 0.0.0.0:8000:8000` правлен `sed`-ом на РФ-сервере, при `git reset --hard` затрётся.
3. HTTPS/certbot пропущен — нет домена.

Этот срез закрывает (1) и (2). Пункт (3) требует домена — вне scope, пойдёт отдельным срезом когда домен будет куплен.

## Цель и измеримый результат

- В `deploy/docker-compose.yml` путь к `.env` корректный → симлинк `deploy/.env` на серверах можно удалить, compose поднимается с чистой структуры `/opt/tvsalebot/`.
- Биндинг порта api управляется переменной `API_BIND` → в репо дефолт безопасный (`127.0.0.1`), на РФ прод-инстансе в `.env` стоит `API_BIND=0.0.0.0`, при `git reset --hard` правка не теряется.
- На обоих серверах: `git pull`, удалить симлинк, перезапустить compose, пройти smoke — всё без деградации.
- Декодировать в `deploy/README.md`: раздел про `API_BIND`, что он значит, когда ставить `0.0.0.0`.

## Границы и полномочия

- **Входит:**
  - `deploy/docker-compose.yml`: `env_file: path: .env` → `path: ../.env` (у `api` и у `bot`); `ports: "127.0.0.1:8000:8000"` → `${API_BIND:-127.0.0.1}:8000:8000`.
  - `deploy/README.md`: короткий раздел про `API_BIND`.
  - На РФ-сервере: `git pull`, добавить `API_BIND=0.0.0.0` в `/opt/tvsalebot/.env` через `echo >>` (без чтения существующих значений), удалить симлинк `/opt/tvsalebot/deploy/.env`, `docker compose up -d --build redis api`.
  - На NL-сервере: `git pull`, удалить симлинк `/opt/tvsalebot/deploy/.env`, `docker compose up -d --build --no-deps bot`.
  - Smoke: `curl` /health на РФ локально + с NL; логи бота — polling.
  - Строка в `architecture/decisions.md`.
- **Не входит:**
  - HTTPS/certbot (нет домена).
  - Изменение контракта `/chat` / `/reset` / `/health`.
  - Новые LLM-провайдеры.
  - Трогать `idea/` или `architecture/*.md` кроме `decisions.md`.
- **Разрешения:** compose+README-правки — через writer-агента; деплой на серверы — через deploy-агента; `.env` на серверах — только `echo >>` или `sed -i`, не читать значения.
- **Условия остановки:** если compose не стартует после правок — откат симлинка на серверах, доложить. Если новый тест не нужен (это инфра) — но pytest 21/21 должен остаться зелёным.
- **Откат:** `git revert <commit>` + вернуть симлинк на серверах (`ln -sfn ../.env /opt/tvsalebot/deploy/.env`).

## Проверки правил проекта

- **П1 (бизнес-тексты вне .py):** compose/README — не бизнес и не промпт.
- **П2 (адаптеры):** compose не трогает код адаптеров.
- **П3 (Core и bot независимы):** правки симметричные, API_BIND влияет только на api, env_file — на оба.
- **П6:** не новая либа, не новый провайдер, не изменение контракта `/chat`. `API_BIND` — внутренний параметр compose, не публичный API.
- **П7-а:** `API_BIND` — не секрет, безопасно светить дефолт в репо.
- **П7-б:** прод-инвариант `ENVIRONMENT=prod → LLM_PROVIDER ∈ {gigachat, yandex}` на месте, не меняется.

## Фазы

### Фаза 1 — writer-агент правит compose + README
- `deploy/docker-compose.yml`: 3 правки (env_file у api, env_file у bot, ports у api).
- `deploy/README.md`: раздел про `API_BIND` (прим.: пояснить что по умолчанию локалка, прод-инстансы с nginx либо без него выставляют `0.0.0.0`).
- Проверка: `docker compose -f deploy/docker-compose.yml config` — rc=0.
- Приёмка: оба файла изменены, pytest 21/21 (не должно зацепить, но прогнать).

### Фаза 2 — reviewer-агент
- Проверить корректность путей, что `${API_BIND:-127.0.0.1}` раскрывается правильно, что документация ясная.
- Вернуть вердикт.

### Фаза 3 — судья (оркестратор) + fixer если нужно
- Решить что принять.

### Фаза 4 — коммит + push
- Коммит с attribution.
- Push в origin/main (нужно для `git pull` на серверах).

### Фаза 5 — deploy-агент на РФ+NL
- РФ: `git pull`; `echo "API_BIND=0.0.0.0" >> /opt/tvsalebot/.env` (без чтения); `rm /opt/tvsalebot/deploy/.env` (симлинк); `docker compose -f deploy/docker-compose.yml --env-file /opt/tvsalebot/.env up -d --build redis api`; `curl -fsS http://127.0.0.1:8000/health`.
- NL: `git pull`; `rm /opt/tvsalebot/deploy/.env`; `docker compose -f deploy/docker-compose.yml --env-file /opt/tvsalebot/.env up -d --build --no-deps bot`; `docker logs <bot-container> | tail`.
- Smoke: с NL `curl http://153.80.246.243:8000/health` — 200.
- Проверка isolation: с левой машины (локалка пользователя) → всё ещё timeout.

### Фаза 6 — финал
- Строка в `architecture/decisions.md`.
- Заполнить Итог в этом плане.
- Коммит + push финального состояния.

## Checkpoint
- До начала: `69a1cb4..c5d7a93` в origin/main, pytest 21/21, прод работает (`@tvsalebot_bot` отвечает).
- На РФ: симлинк `/opt/tvsalebot/deploy/.env -> ../.env`, в compose порт `0.0.0.0:8000:8000` (правлено sed).
- На NL: симлинк `/opt/tvsalebot/deploy/.env -> ../.env`, compose не правлен.

## Условия остановки
- После `git pull` на серверах локальные правки `docker-compose.yml` (на РФ sed-правка `0.0.0.0`) будут перезаписаны репом → compose возьмёт `${API_BIND:-127.0.0.1}`. Если `API_BIND` в `.env` не выставлен — api биндится только на localhost → `curl` с NL начнёт timeout. Решение: ПЕРЕД `git pull` на РФ `echo "API_BIND=0.0.0.0" >> /opt/tvsalebot/.env`.
- Если docker compose не поднимается после удаления симлинка — вернуть симлинк, доложить проблему.

## Итог

- **Реализовано целиком:** да (фазы 1–6).
- **Что работает и чем подтверждено:**
  - Коммит `ad46889` в origin/main, pytest 21/21 остаётся зелёным.
  - РФ `153.80.246.243` после `git reset --hard origin/main`: api пересобран (downtime ~5–10 сек), `ss -tlnp | grep :8000` → `0.0.0.0:8000` (API_BIND подхватился из `.env`), `/health` локально → `{"status":"ok","redis":"ok"}`.
  - NL `78.17.117.189` после pull: bot жив, статус `Up` без рестарта (compose увидел что набор env не изменился — симлинк и `../.env` резолвятся в один и тот же файл), логи — `aiogram.dispatcher Start polling` + свежие `POST /chat "HTTP/1.1 200 OK"` в сторону РФ:8000.
  - Симлинки `/opt/tvsalebot/deploy/.env` удалены на обоих серверах, compose работает с прямым `path: ../.env`.
  - Isolation от левых IP: `timeout 5 curl http://153.80.246.243:8000/health` с машины вне NL-whitelist → exit 124 (пакеты дропаются после TCP-connect, firewall живой).
- **Процесс:** оркестратор → план → writer-агент (compose +3 правки, README +раздел) → reviewer-агент (вердикт «ПРИНЯТЬ С ПРАВКАМИ», одна рекомендация про противоречащий пункт чек-листа) → судья (принял) → fixer через SendMessage → коммит `ad46889` + push → deploy-агент на РФ+NL с жёстким правилом «API_BIND в .env ПЕРЕД git pull на РФ» → smoke 12/12.
- **Безопасность:** `.env` на серверах не читался — только `grep -q` (quiet) для проверки наличия `API_BIND=`, `sed -i` для замены или `echo >>` для добавления. Firewall-правила ufw/iptables не трогались.
- **Остаточный техдолг:**
  - HTTPS/certbot пропущен — нет домена. Пойдёт отдельным срезом когда домен будет куплен.
- **Что ждёт пользователя:** ничего. Прод работает чище, при следующем `git reset --hard` ничего не отвалится, одна команда `API_BIND=0.0.0.0 >> .env` стала частью прод-разворота и описана в `deploy/README.md`.
