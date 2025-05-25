import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def scroll_into_view(driver, element, center=True):
    position = 'center' if center else 'start'
    driver.execute_script(
        f"arguments[0].scrollIntoView({{behavior: 'smooth', block: '{position}'}});", element
    )
    time.sleep(0.5)


def scroll_and_toggle(driver, wait, xpath, should_check):
    try:
        checkbox = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

        # Smooth scroll to center of the screen
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", checkbox)
        time.sleep(0.3)  # Short enough to ensure scroll without freeze

        # Simple highlight without setTimeout
        driver.execute_script("""
            arguments[0].style.outline = '2px solid orange';
            arguments[0].style.transition = 'outline 0.4s ease-in-out';
        """, checkbox)

        is_checked = checkbox.is_selected()
        if should_check and not is_checked:
            checkbox.click()
            print(f"⚫ Checked: {xpath}")
        elif not should_check and is_checked:
            checkbox.click()
            print(f"⚪ Unchecked: {xpath}")

        time.sleep(0.2)  # Enough for stability / avoiding double-click
    except Exception as e:
        print(f"⚠️ Element not found or not accessible: {xpath} | Error: {e}")


def click_and_wait_for_new_tab(driver, clickable_element, timeout=10):
    """
    Clicks an element and waits for a new tab to appear.

    Parameters:
        driver: WebDriver
        clickable_element: WebElement - the element to be clicked
        timeout: int - maximum wait time

    Returns:
        str - handle of the newly opened tab
    """
    tabs_before = set(driver.window_handles)
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", clickable_element)
    driver.execute_script("arguments[0].click();", clickable_element)

    WebDriverWait(driver, timeout).until(
        lambda d: len(set(d.window_handles) - tabs_before) > 0,
        message="❌ New tab did not open after click"
    )

    new_tabs = set(driver.window_handles) - tabs_before
    return new_tabs.pop()
