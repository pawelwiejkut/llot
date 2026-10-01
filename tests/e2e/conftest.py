"""Browser tests run against a live LLOT instance (default http://localhost:8080).

Run with:  pytest -m e2e            (or: make e2e)
Override:  LLOT_URL=http://host:port pytest -m e2e
"""

import os

import pytest

BASE_URL = os.getenv("LLOT_URL", "http://localhost:8080").rstrip("/")


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture
def console_errors(page):
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: m.type == "error" and errors.append(m.text))
    return errors


def pick_target_language(page, code):
    """Choose a target language through the visible custom dropdown."""
    dropdown = (
        page.locator("[id^=target-lang-dropdown]")
        .filter(has=page.locator(".language-dropdown-trigger:visible"))
        .first
    )
    dropdown.locator(".language-dropdown-trigger").click()
    dropdown.locator(f"[data-code='{code}']").click()
