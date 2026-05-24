from __future__ import annotations

from typing import Any

import requests


class ApiClient:
    def __init__(self, base_url: str, session: requests.Session | None = None):
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()

    def with_session(self, session: requests.Session) -> "ApiClient":
        return ApiClient(self.base_url, session)

    def get(self, endpoint: str, **kwargs: Any) -> requests.Response:
        return self.session.get(self._url(endpoint), **kwargs)

    def post(self, endpoint: str, **kwargs: Any) -> requests.Response:
        return self.session.post(self._url(endpoint), **kwargs)

    def put(self, endpoint: str, **kwargs: Any) -> requests.Response:
        return self.session.put(self._url(endpoint), **kwargs)

    def delete(self, endpoint: str, **kwargs: Any) -> requests.Response:
        return self.session.delete(self._url(endpoint), **kwargs)

    def _url(self, endpoint: str) -> str:
        if not endpoint.startswith("/"):
            raise ValueError("Endpoint must start with '/'")

        return f"{self.base_url}{endpoint}"
