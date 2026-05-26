from __future__ import annotations

import json
import logging
import os
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import allure
import pytest
import requests
from selene import browser
from selenium import webdriver
from selenium.webdriver.remote.client_config import ClientConfig

from utils.api_client import ApiClient
from utils.attach import (
    attach_console_log,
    attach_page_source,
    attach_screenshot,
    attach_video,
)

logger = logging.getLogger("api")


def _load_env_file(path: str = ".env") -> None:
    env_file = Path(path)
    if not env_file.exists():
        return

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env_file()

PETSTORE_BASE_URL = os.getenv("PETSTORE_BASE_URL", "https://petstore.swagger.io/v2")
DEMO_WEBSHOP_BASE_URL = os.getenv(
    "DEMO_WEBSHOP_BASE_URL",
    "https://demowebshop.tricentis.com",
)
SELENOID_URL = os.getenv("SELENOID_URL")
SELENOID_VIDEO_URL = os.getenv("SELENOID_VIDEO_URL")
SELENOID_LOGIN = os.getenv("SELENOID_LOGIN") or os.getenv("LOGIN")
SELENOID_PASSWORD = os.getenv("SELENOID_PASSWORD") or os.getenv("PASSWORD")
BROWSER_NAME = os.getenv("BROWSER_NAME", "chrome")
BROWSER_VERSION = os.getenv("BROWSER_VERSION")


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default

    return value.lower() in ("1", "true", "yes", "y")


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default

    try:
        return int(value)
    except ValueError:
        return default


BROWSER_WINDOW_WIDTH = _env_int("BROWSER_WINDOW_WIDTH", 1920)
BROWSER_WINDOW_HEIGHT = _env_int("BROWSER_WINDOW_HEIGHT", 1080)
BROWSER_TIMEOUT = _env_int("BROWSER_TIMEOUT", 10)
SELENOID_ENABLE_VIDEO = _env_bool("SELENOID_ENABLE_VIDEO", True)
SELENOID_ENABLE_VNC = _env_bool("SELENOID_ENABLE_VNC", True)
SELENOID_ENABLE_LOG = _env_bool("SELENOID_ENABLE_LOG", True)
HEADLESS = _env_bool("HEADLESS", False)


def _to_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False, indent=2, default=str)
    return str(value)


def _truncate(value: str, limit: int = 10_000) -> str:
    if len(value) <= limit:
        return value

    return f"{value[:limit]}\n... truncated ..."


def _headers_to_dict(headers: Any) -> dict[str, str]:
    if not headers:
        return {}
    try:
        return {str(key): str(value) for key, value in headers.items()}
    except AttributeError:
        return {"raw": _to_text(headers)}


def _request_endpoint(url: str) -> str:
    parsed_url = urlparse(url)
    endpoint = parsed_url.path or url
    if parsed_url.query:
        endpoint = f"{endpoint}?{parsed_url.query}"

    return endpoint


def _attach_request(method: str, url: str, kwargs: dict[str, Any]) -> None:
    request_data = {
        "method": method.upper(),
        "url": url,
        "endpoint": _request_endpoint(url),
        "headers": _headers_to_dict(kwargs.get("headers")),
        "params": kwargs.get("params"),
        "timeout": kwargs.get("timeout"),
        "allow_redirects": kwargs.get("allow_redirects"),
        "json_body": kwargs.get("json"),
        "data_body": kwargs.get("data"),
    }
    allure.attach(
        json.dumps(request_data, ensure_ascii=False, indent=2, default=str),
        name="request",
        attachment_type=allure.attachment_type.JSON,
    )


def _attach_response(response: requests.Response, duration_ms: float) -> None:
    response_body: Any
    content_type = response.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            response_body = response.json()
        except ValueError:
            response_body = _truncate(response.text)
    else:
        response_body = _truncate(response.text)

    response_data = {
        "status_code": response.status_code,
        "reason": response.reason,
        "duration_ms": duration_ms,
        "headers": _headers_to_dict(response.headers),
        "body": response_body,
    }
    allure.attach(
        json.dumps(response_data, ensure_ascii=False, indent=2, default=str),
        name="response",
        attachment_type=allure.attachment_type.JSON,
    )


def _build_chrome_options(
    test_name: str,
    video_name: str | None = None,
) -> webdriver.ChromeOptions:
    options = webdriver.ChromeOptions()
    options.set_capability("browserName", BROWSER_NAME)
    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})

    if BROWSER_VERSION:
        options.set_capability("browserVersion", BROWSER_VERSION)

    if SELENOID_URL:
        options.set_capability(
            "selenoid:options",
            {
                "enableVideo": SELENOID_ENABLE_VIDEO,
                "enableVNC": SELENOID_ENABLE_VNC,
                "enableLog": SELENOID_ENABLE_LOG,
                "name": test_name,
                "videoName": video_name,
            },
        )
    else:
        options.add_argument(
            f"--window-size={BROWSER_WINDOW_WIDTH},{BROWSER_WINDOW_HEIGHT}"
        )
        if HEADLESS:
            options.add_argument("--headless=new")

    return options


def _configure_browser(request: pytest.FixtureRequest) -> str | None:
    test_name = request.node.name
    video_name = f"{test_name}.mp4"
    options = _build_chrome_options(test_name, video_name)

    browser.config.base_url = DEMO_WEBSHOP_BASE_URL
    browser.config.timeout = BROWSER_TIMEOUT
    browser.config.window_width = BROWSER_WINDOW_WIDTH
    browser.config.window_height = BROWSER_WINDOW_HEIGHT

    if not SELENOID_URL:
        browser.config.browser_name = BROWSER_NAME
        browser.config.driver_options = options
        return None

    if SELENOID_LOGIN and SELENOID_PASSWORD:
        driver = webdriver.Remote(
            command_executor=SELENOID_URL,
            options=options,
            client_config=ClientConfig(
                remote_server_addr=SELENOID_URL,
                username=SELENOID_LOGIN,
                password=SELENOID_PASSWORD,
            ),
        )
    else:
        driver = webdriver.Remote(
            command_executor=SELENOID_URL,
            options=options,
        )

    driver.set_window_size(BROWSER_WINDOW_WIDTH, BROWSER_WINDOW_HEIGHT)
    browser.config.driver = driver

    return video_name


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
                logger.info("Response body: %s", _truncate(response.text, limit=2_000))
            with allure.step(
                f"HTTP {method.upper()} {_request_endpoint(url)} -> {status}"
            ):
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


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[Any]) -> Any:
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture()
def petstore_api() -> ApiClient:
    browser.config.base_url = PETSTORE_BASE_URL

    return ApiClient(browser.config.base_url)


@pytest.fixture()
def demowebshop_api(request: pytest.FixtureRequest) -> Iterator[ApiClient]:
    video_name = _configure_browser(request)

    yield ApiClient(browser.config.base_url)

    call_report = getattr(request.node, "rep_call", None)
    test_failed = bool(call_report and call_report.failed)
    if test_failed:
        with allure.step("Приложить артефакты браузера"):
            attach_screenshot()
            attach_console_log()
            attach_page_source()
            if video_name and SELENOID_VIDEO_URL:
                attach_video(f"{SELENOID_VIDEO_URL.rstrip('/')}/{video_name}")

    browser.quit()
