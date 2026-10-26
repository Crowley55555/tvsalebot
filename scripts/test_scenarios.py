"""Прогон пяти эталонных сценариев бота для QA (F19).

Запуск из корня репо:

    py -3 -m scripts.test_scenarios

Что делает:

1. Для каждого сценария: ``POST /consent/grant`` -> серия ``POST /chat`` ->
   ``POST /gdpr/stop`` (чистит историю, чтобы прогоны не склеивались).
2. Пишет транскрипт диалога в ``transcripts/<timestamp>/<scenario_name>.md``.
3. В конце печатает summary со счётчиком и путём к папке с транскриптами.

Критерии оценки сценариев и реплики для human-ревью — в
``prompts/scenarios.md``. Этот скрипт — только транспорт, оценку
«прошло/не прошло» даёт человек, а не LLM-judge.

Переменные окружения:

- ``CORE_API_URL`` (default ``http://127.0.0.1:8000``) — куда стучаться.

Скрипт зовёт только наш собственный Core API. Прямых вызовов к LLM
или Telegram Bot API здесь нет — это ответственность инфраструктурных
адаптеров (П2). Bearer-авторизация Core API на MVP не используется;
когда появится — добавим здесь явной правкой, без env-отражения заранее.
"""

from __future__ import annotations

import asyncio
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import httpx

DEFAULT_BASE_URL = "http://127.0.0.1:8000"
PAUSE_BETWEEN_SCENARIOS_SEC = 1.0
HTTP_TIMEOUT_SEC = 60.0


@dataclass(frozen=True)
class Scenario:
    """Описание одного прогоняемого сценария.

    Критерии успеха и подробное описание — в ``prompts/scenarios.md``
    (ссылка в поле ``criteria_ref``). Здесь только то, что нужно
    машине: имя файла, telegram_id, последовательность реплик.
    """

    name: str
    title: str
    telegram_id: int
    criteria_ref: str
    user_messages: list[str]


# Данные сценариев специально хардкожены в коде, а не парсятся из
# prompts/scenarios.md: это служебная сущность для QA-прогонов, не
# бизнес-тексты. Фразы покупателя — это user replies, они допустимы
# в .py по П1 (см. architecture/00-правила-проекта.md).
SCENARIOS: list[Scenario] = [
    Scenario(
        name="scenario_1_living_room",
        title="Scenario 1 — Хочу телек в гостиную (главная воронка)",
        telegram_id=90001,
        criteria_ref="prompts/scenarios.md § Сценарий 1",
        user_messages=[
            "хочу купить телевизор в гостиную",
            "смотрим в основном кино, иногда футбол",
            "комната светлая, два больших окна",
            "метра три от дивана до стены",
            "бюджет до 150 тыс",
            "ps5 есть, играют дети",
        ],
    ),
    Scenario(
        name="scenario_2_ps5",
        title="Scenario 2 — У меня PS5, подбери ТВ (технический апселл)",
        telegram_id=90002,
        criteria_ref="prompts/scenarios.md § Сценарий 2",
        user_messages=[
            "нужен тв под пс5",
            "играю в шутеры и экшн, важно 4к 120 кадров",
            "комната небольшая, прямого света нет",
            "бюджет 120 тыщ",
            "саундбар уже есть, подключён по хдми",
        ],
    ),
    Scenario(
        name="scenario_3_oled_vs_qled",
        title="Scenario 3 — OLED vs QLED, что лучше (экспертный ответ)",
        telegram_id=90003,
        criteria_ref="prompts/scenarios.md § Сценарий 3",
        user_messages=[
            "что лучше oled или qled?",
            "ну мне и кино и спорт смотреть",
            "комната не очень светлая, но и не кинозал",
            "бюджет 200",
            "вечером свет можно и выключить, да",
        ],
    ),
    Scenario(
        name="scenario_4_dolby_vision",
        title="Scenario 4 — Почему samsung без dolby vision (снятие возражения)",
        telegram_id=90004,
        criteria_ref="prompts/scenarios.md § Сценарий 4",
        user_messages=[
            "хочу samsung но слышал у них нет dolby vision",
            "на apple tv смотрю, там dolby vision везде",
            "то есть у самсунга реально хуже с hdr?",
            "а что если мне dolby vision всё таки важен",
            "ладно, а что из samsung тогда хорошее под кино",
        ],
    ),
    Scenario(
        name="scenario_5_kitchen_budget",
        title="Scenario 5 — Что взять на кухню до 50 тыс (бюджет, не впаривание)",
        telegram_id=90005,
        criteria_ref="prompts/scenarios.md § Сценарий 5",
        user_messages=[
            "нужен тв на кухню",
            "бюджет 50 тыщ, не больше",
            "смотрю в основном новости и ютуб пока готовлю",
            "диагональ чтобы над столешницей висел, 43-50",
            "играть не буду, только смотреть",
        ],
    ),
]


class CoreAPIUnavailable(RuntimeError):
    """Core API недоступен или вернул non-200."""


def _get_base_url() -> str:
    return os.environ.get("CORE_API_URL", DEFAULT_BASE_URL).rstrip("/")


def _get_headers() -> dict[str, str]:
    return {"Content-Type": "application/json"}


async def _post(
    client: httpx.AsyncClient,
    base_url: str,
    path: str,
    payload: dict,
) -> httpx.Response:
    try:
        resp = await client.post(
            f"{base_url}{path}",
            json=payload,
            headers=_get_headers(),
        )
    except httpx.ConnectError as exc:
        raise CoreAPIUnavailable(
            f"Core API недоступен по {base_url} — "
            "запусти `py -3 -m uvicorn api.main:app` в соседнем терминале"
        ) from exc
    if resp.status_code >= 400:
        raise CoreAPIUnavailable(
            f"Core API {path} вернул HTTP {resp.status_code}: {resp.text[:300]}"
        )
    return resp


async def _run_scenario(
    client: httpx.AsyncClient,
    base_url: str,
    scenario: Scenario,
) -> list[tuple[str, str]]:
    """Выполняет один сценарий.

    Возвращает список пар ``(user_msg, bot_reply)`` в порядке диалога.
    """
    await _post(
        client,
        base_url,
        "/consent/grant",
        {"telegram_id": scenario.telegram_id},
    )

    dialog: list[tuple[str, str]] = []
    for user_msg in scenario.user_messages:
        resp = await _post(
            client,
            base_url,
            "/chat",
            {"telegram_id": scenario.telegram_id, "text": user_msg},
        )
        body = resp.json()
        bot_reply = body.get("reply", "<нет поля reply в ответе>")
        dialog.append((user_msg, bot_reply))

    await _post(
        client,
        base_url,
        "/gdpr/stop",
        {"telegram_id": scenario.telegram_id, "reason": "user_delete"},
    )
    return dialog


def _render_transcript(
    scenario: Scenario,
    dialog: list[tuple[str, str]],
    base_url: str,
    started_at: str,
) -> str:
    lines: list[str] = [
        f"# {scenario.title}",
        "",
        f"Запуск: {started_at}  ",
        f"Base URL: {base_url}  ",
        f"telegram_id: {scenario.telegram_id}",
        "",
        "## Что должен сделать бот",
        "",
        f"См. критерии успеха в `{scenario.criteria_ref}`.",
        "",
        "## Диалог",
        "",
    ]
    for user_msg, bot_reply in dialog:
        lines.append(f"**Покупатель:** {user_msg}")
        lines.append("")
        lines.append(f"**Бот:** {bot_reply}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


async def _main_async() -> int:
    base_url = _get_base_url()
    started_at = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    out_dir = Path("transcripts") / started_at
    out_dir.mkdir(parents=True, exist_ok=True)

    passed = 0

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT_SEC) as client:
        for i, scenario in enumerate(SCENARIOS):
            print(f"[{i + 1}/{len(SCENARIOS)}] {scenario.title}...")
            try:
                dialog = await _run_scenario(client, base_url, scenario)
            except CoreAPIUnavailable as exc:
                print(f"  ОШИБКА: {exc}", file=sys.stderr)
                return 2

            transcript = _render_transcript(scenario, dialog, base_url, started_at)
            (out_dir / f"{scenario.name}.md").write_text(transcript, encoding="utf-8")
            passed += 1

            if i < len(SCENARIOS) - 1:
                await asyncio.sleep(PAUSE_BETWEEN_SCENARIOS_SEC)

    print()
    print(f"Готово: {passed}/{len(SCENARIOS)} сценариев завершили прогон без ошибок.")
    print(f"Транскрипты: {out_dir.resolve()}")
    print("Оценка «прошло/не прошло» — вручную по prompts/scenarios.md.")
    return 0


def main() -> int:
    return asyncio.run(_main_async())


if __name__ == "__main__":
    raise SystemExit(main())
