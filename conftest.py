from __future__ import annotations

import json
import logging
import time
from collections.abc import Iterator
from typing import Any

import allure
import pytest
import requests
from selene import browser

from utils.api_client import ApiClient

logger = logging.getLogger("api")

PETSTORE_BASE_URL = "https://petstore.swagger.io/v2"
DEMO_WEBSHOP_BASE_URL = "https://demowebshop.tricentis.com"


def _to_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False, indent=2, default=str)
    return str(value)


def _headers_to_text(headers: Any) -> str:
    if not headers:
        return ""
    try:
        return "\n".join(f"{key}: {value}" for key, value in headers.items())
    except AttributeError:
        return _to_text(headers)


def _attach_request(method: str, url: str, kwargs: dict[str, Any]) -> None:
    request_meta = {
        "method": method.upper(),
        "url": url,
        "params": kwargs.get("params"),
        "timeout": kwargs.get("timeout"),
        "allow_redirects": kwargs.get("allow_redirects"),
    }
    allure.attach(
        json.dumps(request_meta, ensure_ascii=False, indent=2, default=str),
        name="request_meta",
        attachment_type=allure.attachment_type.JSON,
    )
    headers_text = _headers_to_text(kwargs.get("headers"))
    if headers_text:
        allure.attach(
            headers_text,
            name="request_headers",
            attachment_type=allure.attachment_type.TEXT,
        )
    if kwargs.get("json") is not None:
        allure.attach(
            _to_text(kwargs["json"]),
            name="request_json_body",
            attachment_type=allure.attachment_type.JSON,
        )
    if kwargs.get("data") is not None:
        allure.attach(
            _to_text(kwargs["data"]),
            name="request_data_body",
            attachment_type=allure.attachment_type.TEXT,
        )


def _attach_response(response: requests.Response, duration_ms: float) -> None:
    response_meta = {
        "status_code": response.status_code,
        "reason": response.reason,
        "duration_ms": duration_ms,
    }
    allure.attach(
        json.dumps(response_meta, ensure_ascii=False, indent=2, default=str),
        name="response_meta",
        attachment_type=allure.attachment_type.JSON,
    )
    headers_text = _headers_to_text(response.headers)
    if headers_text:
        allure.attach(
            headers_text,
            name="response_headers",
            attachment_type=allure.attachment_type.TEXT,
        )

    content_type = response.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            allure.attach(
                json.dumps(response.json(), ensure_ascii=False, indent=2, default=str),
                name="response_body",
                attachment_type=allure.attachment_type.JSON,
            )
            return
        except ValueError:
            pass

    body = response.text
    if len(body) > 10_000:
        body = f"{body[:10_000]}\n... response body truncated ..."
    allure.attach(
        body,
        name="response_body",
        attachment_type=allure.attachment_type.TEXT,
    )


@pytest.fixture(scope="session", autouse=True)
def allure_requests_logging() -> Iterator[None]:
    original_request = requests.sessions.Session.request

    def logged_request(
        session: requests.sessions.Session, method: str, url: str, **kwargs: Any
    ) -> requests.Response:
        started_at = time.perf_counter()
        response: requests.Response | None = None
        error: Exception | None = None
        try:
            response = original_request(session, method, url, **kwargs)
            return response
        except Exception as exc:
            error = exc
            raise
        finally:
            duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
            status = response.status_code if response is not None else "FAILED"
            logger.info(
                "HTTP %s %s -> %s (%s ms)",
                method.upper(),
                url,
                status,
                duration_ms,
            )
            if kwargs.get("json") is not None:
                logger.info("Request JSON: %s", kwargs["json"])

            if response is not None:
                logger.info("Response body: %s", response.text)
            with allure.step(f"HTTP {method.upper()} {url} -> {status}"):
                _attach_request(method, url, kwargs)
                if response is not None:
                    _attach_response(response, duration_ms)
                if error is not None:
                    allure.attach(
                        str(error),
                        name="request_exception",
                        attachment_type=allure.attachment_type.TEXT,
                    )

    requests.sessions.Session.request = logged_request
    yield
    requests.sessions.Session.request = original_request


@pytest.fixture()
def petstore_api() -> ApiClient:
    browser.config.base_url = PETSTORE_BASE_URL

    return ApiClient(browser.config.base_url)


@pytest.fixture()
def demowebshop_api() -> ApiClient:
    browser.config.base_url = DEMO_WEBSHOP_BASE_URL

    return ApiClient(browser.config.base_url)
