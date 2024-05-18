from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import json
import logging

class EasyApplyLinkedin:

    def __init__(self, data):
        self.email = data['email']
        self.password = data['password']
        self.keywords = data['keywords']
        self.location = data['location']

        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Optional: Run Chrome in headless mode
        chrome_options.add_argument("--no-sandbox")  # Optional: Add sandbox flag for Linux
        chrome_options.add_argument("--disable-dev-shm-usage")  # Optional: Disable shm usage for Linux

        # Initialize Chrome driver with options
        # self.driver = webdriver.Chrome(data['driver_path'], options=chrome_options)
        self.driver = webdriver.Chrome()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.handler = logging.FileHandler('application.log')
        self.handler.setLevel(logging.INFO)
        self.logger.addHandler(self.handler)

    def login_linkedin(self):
        self.driver.get("https://www.linkedin.com/login")
        login_email = self.driver.find_element(By.NAME, 'session_key')
        login_email.clear()
        login_email.send_keys(self.email)
        login_pass = self.driver.find_element(By.NAME, 'session_password')
        login_pass.clear()
        login_pass.send_keys(self.password)
        login_pass.send_keys(Keys.RETURN)

    def job_search(self):
        jobs_link = self.driver.find_element(By.LINK_TEXT, 'Jobs')
        jobs_link.click()
        search_keywords = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[id^='jobs-search-box-keyword-id']"))
        )
        search_keywords.send_keys(self.keywords)
        time.sleep(2)
        search_keywords.send_keys(Keys.RETURN)

    def filter(self):
        easy_apply_button = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Easy Apply')]")
        easy_apply_button.click()
   
    def find_offers(self):
        job_elements = self.driver.find_elements(By.CSS_SELECTOR, ".jobs-search-results__list-item")

        for job_element in job_elements:
            job_element.click()
            try:
                easy_apply_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, ".//button[contains(@aria-label, 'Easy Apply to')]"))
                )
                easy_apply_button.click()
                time.sleep(5)
                self.submit_apply(job_element)
            except (NoSuchElementException, TimeoutException):
                print("Easy Apply button not found for this job")

        self.close_session()
    
    def submit_apply(self, job_add):
        self.logger.info(f"You are applying to the position of: {job_add.text}")
        # Handle the popup and click "Next" until "Submit application" or "Review" is pressed
        while True:
            try:
                next_button = self.driver.find_element(By.XPATH, "//button[@aria-label='Continue to next step']")
                self.driver.execute_script("arguments[0].scrollIntoView();", next_button)
                next_button.click()
                time.sleep(3)  # Wait for the next page to load
            except NoSuchElementException:
                break
            # Click the "Review" button if it appears
        try:
            review_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Review your application')]"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView();", review_button)
            review_button.click()
            time.sleep(2)  # Wait for the review page to load
        except NoSuchElementException:
            self.logger.error('Review button not found')
            pass

        # Click the "Submit application" button if it appears
        try:
            submit_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Submit application')]"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView();", submit_button)
            submit_button.click()
        except NoSuchElementException:
            self.logger.error('Submit application button not found')
            pass

        # Handle the final popup with the "Done" button
        while True:
            try:
                done_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Done')]")
                done_button.click()
                time.sleep(1)  # Wait for the popup to close
            except NoSuchElementException:
                break

        time.sleep(1)

    
    def close_session(self):
        self.logger.info('End of the session, see you later!')
        self.driver.close()

    def apply(self):
        self.driver.maximize_window()
        self.login_linkedin()
        time.sleep(5)
        self.job_search()
        time.sleep(5)
        self.filter()
        time.sleep(2)
        self.find_offers()
        time.sleep(10)
        self.close_session()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    with open('config.json') as config_file:
        data = json.load(config_file)
    bot = EasyApplyLinkedin(data)
    bot.apply()
