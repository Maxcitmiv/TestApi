import json

import allure
from selene import browser


def attach_screenshot() -> None:
    try:
        png = browser.driver.get_screenshot_as_png()
    except Exception as exc:
        allure.attach(
            str(exc),
            name="screenshot_error",
            attachment_type=allure.attachment_type.TEXT,
        )
        return

    allure.attach(
        png,
        name="browser_screenshot",
        attachment_type=allure.attachment_type.PNG,
    )


def attach_page_source() -> None:
    try:
        html = browser.driver.page_source
    except Exception as exc:
        allure.attach(
            str(exc),
            name="page_source_error",
            attachment_type=allure.attachment_type.TEXT,
        )
        return

    allure.attach(
        html,
        name="page_source",
        attachment_type=allure.attachment_type.HTML,
    )


def attach_console_log() -> None:
    try:
        logs = browser.driver.get_log("browser")
        formatted_logs = json.dumps(logs, indent=2, ensure_ascii=False)
    except Exception as exc:
        formatted_logs = f"Could not get browser console logs: {exc}"

    allure.attach(
        formatted_logs,
        name="browser_console_log",
        attachment_type=allure.attachment_type.JSON,
    )


def attach_video(video_url: str) -> None:
    allure.attach(
        video_url,
        name="selenoid_video_url",
        attachment_type=allure.attachment_type.URI_LIST,
    )
