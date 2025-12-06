from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re, os, csv, math

class WithdrawTest(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(30)
        self.base_url = "https://www.google.com/"
        self.verificationErrors = []
        self.accept_next_alert = True
        self.driver.maximize_window()

    def test_withdraw_data_driven(self):
        driver = self.driver
        wait = WebDriverWait(driver, 10)

        # Read test data from CSV file
        csv_file = os.path.join(os.path.dirname(__file__), 'withdraw.csv')
        with open(csv_file, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)

            for row in csv_reader:
                testcase_id = row['testcase_id'].strip()
                deposit_amount = row['deposit_amount'].strip()
                withdraw_amount = row['withdraw_amount'].strip()
                expected_balance = row['expect_balance'].strip()
                expected_message = row['expect_message'].strip()
                error_message_input = row.get('error_message_input', '').strip()

                try:
                    withdraw_float = float(withdraw_amount)
                except ValueError:
                    pass
                else:
                    if withdraw_float % 1 != 0:
                        lower = math.floor(withdraw_float)
                        upper = math.ceil(withdraw_float)

                        # đảm bảo error_message_input luôn là string hợp lệ
                        if not error_message_input:
                            error_message_input = ""

                        error_message_input += f" {lower} and {upper}."
                

                print(f"{'='*60}")
                print(f"Test Case: {testcase_id}")

                # Navigate to the banking application
                driver.get("https://www.globalsqa.com/angularJs-protractor/BankingProject/")
                driver.execute_script("window.localStorage.clear();")
                time.sleep(0.5)

                # Click Customer Login
                wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Customer Login']"))).click()

                # Select user
                wait.until(EC.element_to_be_clickable((By.ID, "userSelect"))).click()
                Select(driver.find_element(By.ID, "userSelect")).select_by_visible_text("Albus Dumbledore")
                driver.find_element(By.XPATH, "//button[@type='submit']").click()

                # Select account
                wait.until(EC.element_to_be_clickable((By.ID, "accountSelect"))).click()
                Select(driver.find_element(By.ID, "accountSelect")).select_by_visible_text("1012")

                # Click Deposit tab
                wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Deposit']"))).click()
                time.sleep(0.5)

                # Deposit amount - wait for input to be ready and clear
                deposit_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='amount']")))
                deposit_input.click()
                time.sleep(0.3)
                deposit_input.clear()
                time.sleep(0.3)
                deposit_input.send_keys(deposit_amount)
                time.sleep(0.5)

                # Click Deposit button
                wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Deposit']"))).click()
                time.sleep(0.5)

                # Click Withdrawl tab
                wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Withdrawl']"))).click()
                time.sleep(0.5)

                # Withdraw amount - wait for input to be ready and clear
                withdraw_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='amount']")))
                withdraw_input.click()
                time.sleep(0.3)
                withdraw_input.clear()
                time.sleep(0.3)
                withdraw_input.send_keys(withdraw_amount)
                time.sleep(0.5)

                # Click Withdraw button
                withdraw_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Withdraw']")))
                withdraw_button.click()
                time.sleep(1)

                # Verify HTML5 validation message if error_message_input is provided
                if error_message_input:
                    try:
                        validation_message = driver.execute_script("return arguments[0].validationMessage;", withdraw_input)
                        self.assertEqual(error_message_input, validation_message)
                        print(f"Input validation verification: PASSED - '{validation_message}'")
                    except AssertionError as e:
                        print(f"Input validation verification: FAILED - Expected: '{error_message_input}', Actual: '{validation_message}'")
                        self.verificationErrors.append(str(e))

                # Verify transaction message
                if expected_message:
                    try:
                        actual_message = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@ng-show='message']"))).text
                        self.assertEqual(expected_message, actual_message)
                        print(f"Message verification: PASSED - '{actual_message}'")
                    except AssertionError as e:
                        print(f"Message verification: FAILED - Expected: '{expected_message}', Actual: '{actual_message}'")
                        self.verificationErrors.append(str(e))
                    except Exception as e:
                        print(f"Error getting message: {str(e)}")

                # Verify balance
                try:
                    actual_balance = driver.find_element(By.XPATH, "//div[@class='center']//strong[2]").text
                    self.assertEqual(expected_balance, actual_balance)
                    print(f"Balance verification: PASSED - '{actual_balance}'")
                except AssertionError as e:
                    print(f"Balance verification: FAILED - Expected: '{expected_balance}', Actual: '{actual_balance}'")
                    self.verificationErrors.append(str(e))

                time.sleep(1)

    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException as e: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)


if __name__ == "__main__":
    unittest.main()
