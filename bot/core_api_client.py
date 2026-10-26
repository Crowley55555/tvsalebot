import logging

import httpx

log = logging.getLogger("bot.core_api_client")


class CoreAPIError(RuntimeError):
    def __init__(self, status_code: int, detail: str):
        super().__init__(f"{status_code}: {detail}")
        self.status_code = status_code
        self.detail = detail


class ConsentRequiredFromAPI(CoreAPIError):
    def __init__(self, user_message: str, policy_url: str):
        super().__init__(409, "consent_required")
        self.user_message = user_message
        self.policy_url = policy_url


class CoreAPIClient:
    def __init__(self, base_url: str, bearer_token: str | None = None, timeout_s: float = 5.0):
        headers = {}
        if bearer_token:
            headers["Authorization"] = f"Bearer {bearer_token}"
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            headers=headers,
            timeout=timeout_s,
        )

    async def chat(self, telegram_id: int, text: str, update_id: int | None = None) -> str:
        payload: dict = {"telegram_id": telegram_id, "text": text}
        if update_id is not None:
            payload["update_id"] = update_id
        try:
            response = await self._client.post("/chat", json=payload)
        except httpx.TimeoutException as exc:
            log.error("core_api_timeout telegram_id=%s", telegram_id)
            raise CoreAPIError(504, "timeout") from exc
        except httpx.HTTPError as exc:
            log.error("core_api_transport_error telegram_id=%s err=%s", telegram_id, exc)
            raise CoreAPIError(502, "transport_error") from exc

        if response.status_code == 409:
            data = response.json()
            if data.get("error") == "consent_required":
                raise ConsentRequiredFromAPI(
                    user_message=data.get(
                        "user_message", "Нужно согласие на обработку ПДн."
                    ),
                    policy_url=data.get("policy_url", ""),
                )
        if response.status_code >= 500:
            log.error(
                "core_api_5xx telegram_id=%s status=%s", telegram_id, response.status_code
            )
            raise CoreAPIError(response.status_code, "upstream_error")
        if response.status_code >= 400:
            detail = response.json().get("detail", "client_error")
            raise CoreAPIError(response.status_code, detail)

        data = response.json()
        reply = data.get("reply", "")
        if not isinstance(reply, str):
            raise CoreAPIError(502, "bad_response_shape")
        return reply

    async def grant_consent(self, telegram_id: int) -> str:
        try:
            response = await self._client.post(
                "/consent/grant", json={"telegram_id": telegram_id}
            )
        except httpx.HTTPError as exc:
            raise CoreAPIError(502, "transport_error") from exc
        if response.status_code >= 400:
            raise CoreAPIError(response.status_code, "grant_failed")
        data = response.json()
        version = data.get("policy_version", "")
        if not isinstance(version, str):
            raise CoreAPIError(502, "bad_response_shape")
        return version

    async def gdpr_stop(self, telegram_id: int, reason: str = "user_stop") -> int:
        try:
            response = await self._client.post(
                "/gdpr/stop",
                json={"telegram_id": telegram_id, "reason": reason},
            )
        except httpx.HTTPError as exc:
            raise CoreAPIError(502, "transport_error") from exc
        if response.status_code >= 400:
            raise CoreAPIError(response.status_code, "stop_failed")
        data = response.json()
        return int(data.get("deleted_keys", 0))

    async def aclose(self) -> None:
        await self._client.aclose()
