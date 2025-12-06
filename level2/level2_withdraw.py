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
        self.driver.maximize_window()
        self.verificationErrors = []
        self.accept_next_alert = True

        # Load locators from CSV file
        self.locators = {}
        locators_file = os.path.join(os.path.dirname(__file__), 'locators_withdraw.csv')
        with open(locators_file, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                element_name = row['element_name'].strip()
                locator_type = row['locator_type'].strip()
                locator_value = row['locator_value'].strip()
                self.locators[element_name] = {
                    'type': locator_type,
                    'value': locator_value
                }

        print("" + "="*60)
        print("Loaded Locators:")
        for name, loc in self.locators.items():
            print(f"  {name}: {loc['type']} = {loc['value']}")
        print("="*60)

    def get_by_type(self, locator_type):
        """Convert locator type string to Selenium By type"""
        locator_map = {
            'id': By.ID,
            'xpath': By.XPATH,
            'name': By.NAME,
            'class': By.CLASS_NAME,
            'css': By.CSS_SELECTOR,
            'tag': By.TAG_NAME,
            'link_text': By.LINK_TEXT,
            'partial_link_text': By.PARTIAL_LINK_TEXT
        }
        return locator_map.get(locator_type.lower(), By.XPATH)

    def find_element_by_locator(self, element_name, wait_for_clickable=False):
        """Find element using locator from CSV"""
        locator = self.locators[element_name]
        by_type = self.get_by_type(locator['type'])

        if wait_for_clickable:
            wait = WebDriverWait(self.driver, 10)
            return wait.until(EC.element_to_be_clickable((by_type, locator['value'])))
        else:
            return self.driver.find_element(by_type, locator['value'])

    def test_withdraw_data_driven(self):
        driver = self.driver
        wait = WebDriverWait(driver, 10)

        # Read test data from CSV file
        csv_file = os.path.join(os.path.dirname(__file__), 'withdraw_data.csv')
        with open(csv_file, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)

            for row in csv_reader:
                testcase_id = row['testcase_id'].strip()
                user_name = row['user_name'].strip()
                account_number = row['account_number'].strip()
                deposit_amount = row['deposit_amount'].strip()
                withdraw_amount = row['withdraw_amount'].strip()
                expected_balance = row['expect_balance'].strip()
                expected_message = row['expect_message'].strip()
                error_message_input = row.get('error_message_input', '').strip()

                # Handle decimal withdraw amounts for validation message
                try:
                    withdraw_float = float(withdraw_amount)
                except ValueError:
                    pass
                else:
                    if withdraw_float % 1 != 0:
                        lower = math.floor(withdraw_float)
                        upper = math.ceil(withdraw_float)
                        if not error_message_input:
                            error_message_input = ""
                        error_message_input += f" {lower} and {upper}."

                print(f"{'='*60}")
                print(f"Test Case: {testcase_id}")

                # Navigate to the banking application using locator from CSV
                app_url = self.locators['app_url']['value']
                driver.get(app_url)
                driver.execute_script("window.localStorage.clear();")
                time.sleep(0.5)

                # Click Customer Login button
                self.find_element_by_locator('customer_login_button', wait_for_clickable=True).click()

                # Select user
                self.find_element_by_locator('user_select', wait_for_clickable=True).click()
                user_select = self.find_element_by_locator('user_select')
                Select(user_select).select_by_visible_text(user_name)
                self.find_element_by_locator('user_submit_button').click()

                # Select account
                self.find_element_by_locator('account_select', wait_for_clickable=True).click()
                account_select = self.find_element_by_locator('account_select')
                Select(account_select).select_by_visible_text(account_number)

                # Click Deposit tab
                self.find_element_by_locator('deposit_tab_button', wait_for_clickable=True).click()
                time.sleep(0.5)

                # Deposit amount
                deposit_input = self.find_element_by_locator('amount_input', wait_for_clickable=True)
                deposit_input.click()
                time.sleep(0.3)
                deposit_input.clear()
                time.sleep(0.3)
                deposit_input.send_keys(deposit_amount)
                time.sleep(0.5)

                # Click Deposit button
                self.find_element_by_locator('deposit_button', wait_for_clickable=True).click()
                time.sleep(0.5)

                # Click Withdrawl tab
                self.find_element_by_locator('withdraw_tab_button', wait_for_clickable=True).click()
                time.sleep(0.5)

                # Withdraw amount
                withdraw_input = self.find_element_by_locator('amount_input', wait_for_clickable=True)
                withdraw_input.click()
                time.sleep(0.3)
                withdraw_input.clear()
                time.sleep(0.3)
                withdraw_input.send_keys(withdraw_amount)
                time.sleep(0.5)

                # Click Withdraw button
                self.find_element_by_locator('withdraw_button', wait_for_clickable=True).click()
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
                        actual_message = self.find_element_by_locator('transaction_message')
                        actual_message_text = wait.until(EC.presence_of_element_located(
                            (self.get_by_type(self.locators['transaction_message']['type']),
                             self.locators['transaction_message']['value'])
                        )).text
                        self.assertEqual(expected_message, actual_message_text)
                        print(f"Message verification: PASSED - '{actual_message_text}'")
                    except AssertionError as e:
                        print(f"Message verification: FAILED - Expected: '{expected_message}', Actual: '{actual_message_text}'")
                        self.verificationErrors.append(str(e))
                    except Exception as e:
                        print(f"Error getting message: {str(e)}")

                # Verify balance
                try:
                    actual_balance = self.find_element_by_locator('balance_display').text
                    self.assertEqual(expected_balance, actual_balance)
                    print(f"Balance verification: PASSED - '{actual_balance}'")
                except AssertionError as e:
                    print(f"Balance verification: FAILED - Expected: '{expected_balance}', Actual: '{actual_balance}'")
                    self.verificationErrors.append(str(e))

                time.sleep(1)

    def is_element_present(self, how, what):
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException:
            return False
        return True

    def is_alert_present(self):
        try:
            self.driver.switch_to.alert
        except NoAlertPresentException:
            return False
        return True

    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally:
            self.accept_next_alert = True

    def tearDown(self):
        self.driver.quit()
        if self.verificationErrors:
            print("\n=== Verification Errors Summary ===")
            for error in self.verificationErrors:
                print(f"- {error}")
        self.assertEqual([], self.verificationErrors)


if __name__ == "__main__":
    unittest.main()
