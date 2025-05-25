import os
import glob
import pytest
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from utils.ui_helpers import scroll_into_view, scroll_and_toggle, click_and_wait_for_new_tab
from utils.form_helpers import fill_personal_form

# 📁 Create screenshots folder and clear previous artifacts
os.makedirs("screenshots", exist_ok=True)
for f in glob.glob("screenshots/*") + glob.glob("*.html") + glob.glob("*.log"):
    os.remove(f)

# 🔧 Logging setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler("rafael_test_log.log", mode='w', encoding='utf-8')
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)

def save_debug(name: str, driver):
    path = f"screenshots/{name}.png"
    driver.save_screenshot(path)
    with open(f"{name}.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    logger.info(f"📸 Screenshot saved: {path}")

@pytest.mark.rafael
def test_rafael_application_flow(driver, wait):
    try:
        logger.info("====== 🌐 STEP 1: Load Rafael homepage ======")
        driver.get("https://he.rafael.co.il/")
        logger.info("✅ Rafael homepage loaded")

        logger.info("====== 🔗 STEP 2: Navigate to career tab ======")
        career_links = wait.until(EC.presence_of_all_elements_located((By.LINK_TEXT, "קריירה")))
        career_link = next(link for link in career_links if "career.rafael.co.il" in link.get_attribute("href"))
        scroll_into_view(driver, career_link)
        career_tab = click_and_wait_for_new_tab(driver, career_link)
        driver.switch_to.window(career_tab)
        logger.info("✅ Switched to career tab: %s", driver.current_url)
        save_debug("after_tab_switch", driver)

        logger.info("====== 📄 STEP 3: Scroll to form header ======")
        try:
            anchor = wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'מה הצעד הבא?')]")))
            scroll_into_view(driver, anchor)
            logger.info("✅ Scrolled to header")
            time.sleep(20)
        except Exception as e:
            logger.warning("⚠️ Header scroll failed: %s", e)

        logger.info("====== 🧩 STEP 4: Wait for form ======")
        try:
            wait.until(lambda d: d.execute_script("""
                const el = document.getElementById("next-step-form");
                return el && (el.offsetWidth || el.offsetHeight || el.getClientRects().length);
            """))
            logger.info("✅ Form visible")
        except Exception as e:
            save_debug("error_form_not_visible", driver)
            raise AssertionError("❌ Form did not become visible") from e

        logger.info("====== 📝 STEP 5: Fill dropdowns ======")
        form_fields = {
            "strong-side": "בטיחות ואיכות",
            "want-to-work": "משרה מלאה",
            "in-area": "צפון"
        }

        for field_id, text in form_fields.items():
            try:
                field = wait.until(EC.presence_of_element_located((By.ID, field_id)))
                scroll_into_view(driver, field)
                Select(field).select_by_visible_text(text)
                logger.info(f"✅ Selected '{text}' in '{field_id}'")
            except Exception as e:
                save_debug(f"error_{field_id}", driver)
                raise AssertionError(f"❌ Could not select '{text}' in '{field_id}'") from e

        logger.info("====== 📤 STEP 6: Submit form ======")
        try:
            submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="next-step-form"]/button')))
            scroll_into_view(driver, submit_button)
            submit_button.click()
            logger.info("✅ Form submitted")
        except Exception as e:
            save_debug("error_submit_button", driver)
            raise AssertionError("❌ Failed to submit form") from e

        logger.info("====== 🎛️ STEP 7: Wait for filters page ======")
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="filter-area-4"]')))
        logger.info("✅ Filters loaded")

        logger.info("====== 🧪 STEP 8: Apply filters ======")
        filters = {
            '//*[@id="filter-area-4"]': False,
            '//*[@id="filter-area-7"]': False,
            '//*[@id="filter-area-8"]': False,
            '//*[@id="filter-area-6"]': True,
            '//*[@id="filter-area-9"]': True,
            '//*[@id="filter-area-12"]': True
        }

        for xpath, should_check in filters.items():
            scroll_and_toggle(driver, wait, xpath, should_check)
        logger.info("✅ Filters applied")

        logger.info("====== 📄 STEP 9: Click 'Submit Resume' ======")
        try:
            apply_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "שליחת קורות חיים")]')))
            scroll_into_view(driver, apply_button)
            driver.execute_script("arguments[0].click();", apply_button)
            wait.until(lambda d: "resume" in d.current_url.lower() or d.title != "")
            logger.info("✅ Navigated to resume submission page")
        except Exception as e:
            save_debug("error_resume_button", driver)
            raise AssertionError("❌ Could not open resume page") from e

        logger.info("====== 👤 STEP 10: Fill personal form ======")
        try:
            fill_personal_form(driver, wait)
            logger.info("✅ Personal form filled")
        except Exception as e:
            logger.warning("⚠️ Could not fill personal form: %s", e)

        logger.info("====== 📎 STEP 11: Upload resume ======")
        try:
            upload_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="file" and @name="file"]')))
            scroll_into_view(driver, upload_input)
            driver.execute_script("arguments[0].style.display = 'block';", upload_input)
            resume_path = os.path.abspath("data/BoazRichResume.pdf")
            upload_input.send_keys(resume_path)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.file-upload-data .title')))
            title = driver.find_element(By.CSS_SELECTOR, '.file-upload-data .title').text
            logger.info(f"📎 Resume uploaded: {title}")
        except Exception as e:
            save_debug("error_upload", driver)
            raise AssertionError("❌ Failed to upload resume") from e

    finally:
        driver.quit()
