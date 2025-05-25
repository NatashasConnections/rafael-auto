# conftest.py
import pytest
import undetected_chromedriver as uc
import os
from selenium.webdriver.support.ui import WebDriverWait
from undetected_chromedriver.patcher import Patcher

@pytest.fixture
def driver():
    Patcher().auto()

    options = uc.ChromeOptions()
    options.add_argument("--autoplay-policy=no-user-gesture-required")
    options.add_argument("--disable-popup-blocking")

    # ✅ Realistic user-agent (optional, but helps)
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )

    # ✅ Headless mode for CI
    if os.getenv("CI"):
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    # ❌ Removed excludeSwitches and useAutomationExtension
    driver = uc.Chrome(options=options)

    # Optional stealth tweak
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            """
        },
    )

    yield driver
    driver.quit()

@pytest.fixture
def wait(driver):
    return WebDriverWait(driver, 30)

