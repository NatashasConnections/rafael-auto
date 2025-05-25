import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def highlight_element(driver, element, border_color="orange", background_color=None, restore=True, delay=1.2):
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
    time.sleep(0.2)

    style = f"border: 2px solid {border_color}; transition: all 0.3s ease-in-out;"
    if background_color:
        style += f" background-color: {background_color};"

    driver.execute_script("""
        arguments[0].setAttribute('data-original-style', arguments[0].getAttribute('style') || '');
        arguments[0].setAttribute('style', arguments[0].getAttribute('style') + '; ' + arguments[1]);
    """, element, style)

    if restore:
        driver.execute_script(f"""
            setTimeout(() => {{
                arguments[0].setAttribute('style', arguments[0].getAttribute('data-original-style'));
            }}, {int(delay * 1000)});
        """, element)

    time.sleep(0.3)


def type_with_highlight(driver, wait, xpath, value):
    field = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    highlight_element(driver, field, border_color="orange")
    field.send_keys(value)
    time.sleep(0.5)


def click_radio_with_highlight(driver, wait, input_id, description):
    input_elem = wait.until(EC.presence_of_element_located((By.ID, input_id)))
    wrapper = input_elem.find_element(By.XPATH, './parent::*')

    highlight_element(driver, wrapper, border_color="#28a745", background_color="#d4edda")
    wrapper.click()
    time.sleep(0.4)

    state = input_elem.get_attribute("aria-checked")
    print(f"{'⚫' if state == 'true' else '⚪'} {description} (aria-checked={state})")


def fill_personal_form(driver, wait):
    try:
        # Text fields
        type_with_highlight(driver, wait, '//input[@name="firstName" and @placeholder="שם פרטי"]', "בועז")
        type_with_highlight(driver, wait, '//input[@name="lastName" and @placeholder="שם משפחה"]', "ריץ")
        type_with_highlight(driver, wait, '//input[@name="ID" and @placeholder="מספר תעודת זהות"]', "036535052")
        type_with_highlight(driver, wait, '//input[@name="email" and @placeholder="אימייל"]', "boazt1000@gmail.com")
        type_with_highlight(driver, wait, '//input[@name="phone" and @placeholder="מספר טלפון נייד"]', "0543399908")

        # Select radio buttons
        click_radio_with_highlight(driver, wait, "another_citiz_1", "Additional citizenship – Yes selected")
        click_radio_with_highlight(driver, wait, "family_in_rafael_1", "Relative in Rafael – Yes selected")
        click_radio_with_highlight(driver, wait, "isStudent_0", "Student – No selected")

        # Upload file
        try:
            upload_input = wait.until(EC.presence_of_element_located((
                By.XPATH, '//input[@type="file" and @name="file"]'
            )))
            highlight_element(driver, upload_input, border_color="#6c757d")
            driver.execute_script("arguments[0].style.display = 'block';", upload_input)
            upload_input.send_keys(os.path.abspath("data/BoazRichResume.pdf"))
            print("📎 Resume file uploaded")

            time.sleep(1)
            title = driver.find_element(By.CSS_SELECTOR, '.file-upload-data .title').text
            print(f"📄 Upload status: {title}")

        except Exception as upload_err:
            print(f"⚠️ Error uploading resume file: {upload_err}")

        time.sleep(2)

    except Exception as e:
        print(f"⚠️ General error while filling form: {e}")

