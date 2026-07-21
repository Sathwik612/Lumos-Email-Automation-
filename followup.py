from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
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

        if pd.isna(row["email"]):
            continue

        recipient_email = str(row["email"]).strip()
        subject_text = str(row["subject"]).strip()

        if pd.isna(row["custom_message"]):
            message = ""
        else:
            message = str(row["custom_message"])

        print(f"\nSending {index + 1}/{len(df)} -> {recipient_email}")

        # --------------------------------------------------
        # ATTEMPT REPLY FROM SENT → ELSE COMPOSE NEW
        # --------------------------------------------------

        driver.switch_to.default_content()
        time.sleep(1)

        driver.switch_to.frame(
            driver.find_element(By.ID, "sg-webmail")
        )
        time.sleep(1)

        # Click Mail to go to mailbox
        mail_btn = driver.find_element(By.ID, "rcmbtn101")
        driver.execute_script("arguments[0].click();", mail_btn)
        time.sleep(3)

        # Click Sent folder
        sent = driver.find_element(
            By.CSS_SELECTOR,
            "a[rel='INBOX.Sent']"
        )
        driver.execute_script("arguments[0].click();", sent)
        time.sleep(2)

        # Search for recipient email
        search = driver.find_element(By.ID, "mailsearchform")
        search.clear()
        search.send_keys(recipient_email)
        search.send_keys(Keys.RETURN)
        time.sleep(5)

        # Try to find matching thread — check multiple possible result containers
        results = driver.find_elements(
            By.CSS_SELECTOR,
            "#messagelist a[href*='_action=show']"
        )

        # If empty, try matching by email text in the message list
        if not results:
            all_rows = driver.find_elements(By.CSS_SELECTOR, "#messagelist tr")
            for row_el in all_rows:
                try:
                    row_text = row_el.text.lower()
                    if recipient_email.lower() in row_text:
                        link = row_el.find_element(By.CSS_SELECTOR, "a[href*='_action=show']")
                        if link:
                            results = [link]
                            print(f"Found thread for {recipient_email} by text match")
                            break
                except:
                    pass

        if results:
            is_reply = True
            print("Previous thread found. Replying...")

            top_link = results[0]
            ActionChains(driver).move_to_element(top_link).click().perform()
            top_link.send_keys(Keys.RETURN)
            time.sleep(2)

            reply = driver.find_element(
                By.CSS_SELECTOR,
                "a.reply"
            )
            driver.execute_script("arguments[0].click();", reply)

            time.sleep(6)

            driver.switch_to.default_content()
            driver.switch_to.frame(
                driver.find_element(By.ID, "sg-webmail")
            )
            time.sleep(2)

            try:
                subject = driver.find_element(
                    By.ID,
                    "compose-subject"
                )
                subject.click()
                time.sleep(0.5)
                subject.clear()
                subject.send_keys(subject_text)
                print("Subject entered")
            except Exception as e:
                print("Subject failed:", e)
                continue

        else:
            is_reply = False
            print("No previous thread found. Composing fresh email...")

            driver.switch_to.default_content()
            time.sleep(1)

            compose_clicked = False
            for btn in driver.find_elements(
                By.CSS_SELECTOR,
                "button.sg-button"
            ):
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
                except:
                    pass

            if not compose_clicked:
                print("Could not click compose")
                continue

            time.sleep(2)

            driver.switch_to.frame(
                driver.find_element(By.ID, "sg-webmail")
            )
            time.sleep(2)

            to_field = None
            for box in driver.find_elements(
                By.CSS_SELECTOR,
                "input[role='combobox']"
            ):
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

                    if is_reply:
                        driver.execute_script(
                            "arguments[0].insertAdjacentHTML('afterbegin', arguments[1]);",
                            body,
                            message
                        )
                    else:
                        driver.execute_script(
                            "arguments[0].innerHTML='';",
                            body
                        )
                        time.sleep(0.3)
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
            path = str(attachment_path).strip().strip('"')
            if os.path.isfile(path):
                driver.switch_to.default_content()
                time.sleep(1)
                driver.switch_to.frame(
                    driver.find_element(By.ID, "sg-webmail")
                )
                time.sleep(1)

                file_input = driver.find_element(
                    By.ID,
                    "uploadformInput"
                )
                driver.execute_script(
                    "arguments[0].style.display = 'block';",
                    file_input
                )
                file_input.send_keys(os.path.abspath(path))
                print(f"Attaching: {path}")
                time.sleep(5)
            else:
                print(f"Attachment file not found: {path}")

        # --------------------------------------------------
        # SEND
        # --------------------------------------------------

        time.sleep(2)

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

                    print(f"EMAIL SENT TO {recipient_email}")
                    break

            except:
                pass

        if not sent:
            driver.switch_to.default_content()
            buttons = driver.find_elements(
                By.CSS_SELECTOR,
                "button.sg-button"
            )
            for btn in buttons:
                try:
                    if "SEND" in btn.text.strip().upper():
                        driver.execute_script(
                            "arguments[0].click();",
                            btn
                        )
                        sent = True
                        print(f"EMAIL SENT TO {recipient_email}")
                        break
                except:
                    pass

        if not sent:
            print("Could not find SEND button")

        driver.switch_to.default_content()
        time.sleep(3)

    except Exception as e:

        print(f"FAILED FOR {recipient_email}")
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