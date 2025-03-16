import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions

load_dotenv()

threshold = 30
url = 'https://my.te.eg/echannel/#/login'

def sendMail(success, quota = None, error=None):
    if success:
        message = Mail(
            from_email=os.getenv('MAIL_FROM'),
            to_emails=os.getenv('MAIL_TO'),
            subject='Quota Reminder',
            html_content=f'You have <strong>{quota} GB</strong> remaining'
        )
        try:
            sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
            sg.send(message)
        except Exception as e:
            print(e.message)
    else:
        message = Mail(
            from_email=os.getenv('MAIL_FROM'),
            to_emails=os.getenv('MAIL_TO'),
            subject='Quota Reminder - Error',
            html_content=f'An error occurred: {error}'
        )
        try:
            sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
            sg.send(message)
        except Exception as e:
            print(e.message)

options = FirefoxOptions()
options.add_argument("--headless")
driver = webdriver.Firefox(options=options)
driver.get(url)

try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "login_loginid_input_01"))
    )
    number = driver.find_element(By.ID, "login_loginid_input_01")
    number.send_keys(os.getenv('PHONE_NUMBER'))

    type = driver.find_element(By.ID, "login_input_type_01")
    type.click()

    type_internet = driver.find_element("xpath", "//*[contains(text(), 'Internet')]")
    type_internet.click()

    number = driver.find_element(By.ID, "login_password_input_01")
    number.send_keys(os.getenv('PASSWORD'))

    login = driver.find_element(By.ID, "login-withecare")
    login.click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/section/main/div/div/div[2]/div[3]/div/div/div[1]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div[1]/div[2]/div[1]/span[1]"))
    )

    remaining_element = driver.find_element("xpath", "/html/body/div[1]/section/main/div/div/div[2]/div[3]/div/div/div[1]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div[1]/div[2]/div[1]/span[1]")
    remaining_gbs = float(remaining_element.text)
    
    if remaining_gbs < threshold:
        sendMail(success=True, quota=remaining_gbs)

except Exception as e:
    print(f"An error occurred: {e}")
    sendMail(success=False, error=e)
finally:
    driver.quit()
