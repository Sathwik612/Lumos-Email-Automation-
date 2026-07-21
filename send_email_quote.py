from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
import time
import os

# --------------------------------------------------
# START CHROME
# --------------------------------------------------

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

driver.get("https://vm701.sgvps.net/webmail/log-in")

input("Login manually and press ENTER when inbox is visible...")

time.sleep(5)

# --------------------------------------------------
# LOAD CSV
# --------------------------------------------------

df = pd.read_csv("emails.csv", encoding="utf-8")

# Clean column names
df.columns = (
    df.columns
      .str.strip()
      .str.lower()
)

print(df.columns.tolist())

print(f"Loaded {len(df)} recipients")

# --------------------------------------------------
# SEND EMAILS
# --------------------------------------------------

for index, row in df.iterrows():

    try:

        # Skip blank rows
        if pd.isna(row["email"]):
            continue

        recipient_email = str(row["email"]).strip()
        subject_text = str(row["subject"]).strip()

        if pd.isna(row["custom_message"]):
            message = ""
        else:
            message = str(row["custom_message"])

        print(
            f"\nSending {index + 1}/{len(df)} -> {recipient_email}"
        )

        # Always start from top level
        driver.switch_to.default_content()

        # --------------------------------------------------
        # CLICK COMPOSE
        # --------------------------------------------------

        buttons = driver.find_elements(
            By.CSS_SELECTOR,
            "button.sg-button"
        )

        compose_clicked = False

        for btn in buttons:

            try:
                if "COMPOSE" in btn.text.upper():

                    driver.execute_script(
                        "arguments[0].scrollIntoView({block:'center'});",
                        btn
                    )

                    time.sleep(1)

                    driver.execute_script(
                        "arguments[0].click();",
                        btn
                    )

                    compose_clicked = True

                    print("Compose clicked!")

                    break

            except Exception as e:
                print(e)

        if not compose_clicked:
            print("Could not click compose")
            continue

        # --------------------------------------------------
        # SWITCH TO ROUNDCUBE IFRAME
        # --------------------------------------------------

        time.sleep(2)

        driver.switch_to.frame(
            driver.find_element(By.ID, "sg-webmail")
        )

        time.sleep(2)

        # --------------------------------------------------
        # TO FIELD
        # --------------------------------------------------

        recipient_boxes = driver.find_elements(
            By.CSS_SELECTOR,
            "input[role='combobox']"
        )

        to_field = None

        for box in recipient_boxes:
            try:
                if box.is_displayed():
                    to_field = box
                    break
            except:
                pass

        if to_field:

            driver.execute_script(
                "arguments[0].scrollIntoView(true);",
                to_field
            )

            time.sleep(0.5)

            driver.execute_script(
                "arguments[0].click();",
                to_field
            )

            time.sleep(0.5)

            to_field.send_keys(recipient_email)

            print("Recipient entered")

        else:
            print("Could not locate TO field")
            continue

        # --------------------------------------------------
        # SUBJECT
        # --------------------------------------------------

        try:

            subject = driver.find_element(
                By.ID,
                "compose-subject"
            )

            subject.click()

            subject.send_keys(subject_text)

            print("Subject entered")

        except Exception as e:

            print("Subject failed:", e)
            continue

        # --------------------------------------------------
        # BODY (HTML VERSION)
        # --------------------------------------------------

        body_filled = False

        iframes = driver.find_elements(
            By.TAG_NAME,
            "iframe"
        )

        print("Searching for body editor...")

        for i, frame in enumerate(iframes):

            try:

                print(f"Trying iframe {i}")

                driver.switch_to.frame(frame)

                body = driver.find_element(
                    By.TAG_NAME,
                    "body"
                )

                if body.is_displayed():

                    print("Editor found!")

                    # Remove default signature
                    driver.execute_script(
                        "arguments[0].innerHTML='';",
                        body
                    )

                    time.sleep(0.5)

                    # Insert FULL HTML directly
                    driver.execute_script(
                        "arguments[0].innerHTML = arguments[1];",
                        body,
                        message
                    )

                    time.sleep(0.5)

                    print("HTML body inserted successfully")

                    body_filled = True

                    driver.switch_to.parent_frame()

                    break

                driver.switch_to.parent_frame()

            except Exception as e:

                print("BODY ERROR:", e)

                try:
                    driver.switch_to.parent_frame()
                except:
                    pass

        if not body_filled:
            print("Could not fill body")
            continue

        # --------------------------------------------------
        # ATTACH FILE
        # --------------------------------------------------

        attachment_path = row.get("attachment_path", "")
        if pd.notna(attachment_path) and str(attachment_path).strip():
            path = str(attachment_path).strip()
            if os.path.isfile(path):
                driver.switch_to.default_content()
                time.sleep(1)
                driver.switch_to.frame(driver.find_element(By.ID, "sg-webmail"))
                time.sleep(1)

                file_input = driver.find_element(By.ID, "uploadformInput")
                driver.execute_script("arguments[0].style.display = 'block';", file_input)
                file_input.send_keys(os.path.abspath(path))
                print(f"Attaching: {path}")
                time.sleep(5)
            else:
                print(f"Attachment file not found: {path}")

        # --------------------------------------------------
        # SEND
        # --------------------------------------------------

        time.sleep(1)

        buttons = driver.find_elements(
            By.TAG_NAME,
            "button"
        )

        sent = False

        for btn in buttons:

            try:

                text = btn.text.strip()

                if "SEND" in text.upper():

                    driver.execute_script(
                        "arguments[0].click();",
                        btn
                    )

                    sent = True

                    print(
                        f"EMAIL SENT TO {recipient_email}"
                    )

                    break

            except:
                pass

        if not sent:
            print("Could not find SEND button")

        # Back to top for next email
        driver.switch_to.default_content()

        # Delay between emails
        time.sleep(6)

    except Exception as e:

        print(
            f"FAILED FOR {recipient_email}"
        )

        print(e)

        try:
            driver.switch_to.default_content()
        except:
            pass

        continue

# --------------------------------------------------
# FINISHED
# --------------------------------------------------

print("\nAll emails processed.")

input("Press ENTER to close browser...")

driver.quit()