import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Store browser instances per username
browser_instances = {}

NODE_ENV = os.environ.get("NODE_ENV", "development")

def init_browser():
    options = Options()
    # Adjust headless mode based on environment
    options.headless = False if NODE_ENV == "production" else True
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-setuid-sandbox")
    return webdriver.Chrome(ChromeDriverManager().install(), options=options)

def scrape_balance(username: str, password: str, otp: str = None) -> dict:
    """
    Drives the login/scraping flow:
      - Without OTP: navigates to the login page, fills in credentials, and waits for OTP.
      - With OTP: submits the OTP, waits for the balance element, and extracts the balance.
    """
    if username not in browser_instances:
        browser_instances[username] = init_browser()
    driver = browser_instances[username]
    
    try:
        login_url = "https://www.cihnet.co.ma"
        username_selector = "input#Main_ctl00_txtHBLogin"
        otp_input_selector = "input#Main_ctl00_txtOtpValue"
        login_button_selector = "button#Main_ctl00_btn"
        otp_submit_button_selector = "button#Main_ctl00_btnSendOtp"
        balance_selector = "#itemPlaceholderContainer"

        if not otp:
            driver.get(login_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, username_selector))
            )
            # Enter username
            driver.find_element(By.CSS_SELECTOR, username_selector).send_keys(username)
            # Simulate entering the password digit-by-digit
            for digit in str(password):
                driver.find_element(By.CSS_SELECTOR, username_selector).send_keys(digit)
                time.sleep(1)
            driver.find_element(By.CSS_SELECTOR, login_button_selector).click()
            # Wait for OTP input to appear
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, otp_input_selector))
            )
            return {"status": "OTP_REQUIRED"}
        else:
            # Enter OTP and submit
            otp_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, otp_input_selector))
            )
            otp_field.clear()
            otp_field.send_keys(otp)
            time.sleep(1)
            driver.find_element(By.CSS_SELECTOR, otp_submit_button_selector).click()
            # Wait for the balance element
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, balance_selector))
            )
            balance_element = driver.find_element(
                By.CSS_SELECTOR, f"{balance_selector} tbody tr td:nth-child(3)"
            )
            balance = balance_element.text.strip() if balance_element else None
            if balance:
                return {"status": "balance", "balance": balance}
            else:
                raise Exception("Balance not found on page")
    except Exception as e:
        print("Error during scraping:", e)
        raise