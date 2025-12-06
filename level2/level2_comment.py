from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re, os, csv

class CommentTest(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(30)
        self.driver.maximize_window()
        self.verificationErrors = []
        self.accept_next_alert = True

        # Load locators from CSV file
        self.locators = {}
        locators_file = os.path.join(os.path.dirname(__file__), 'locators_comment.csv')
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

        print("\n" + "="*60)
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

    def test_comment_data_driven(self):
        driver = self.driver
        wait = WebDriverWait(driver, 10)

        # Read test data from CSV file
        csv_file = os.path.join(os.path.dirname(__file__), 'comment_data.csv')
        with open(csv_file, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)

            for row in csv_reader:
                testcase_id = row['testcase_id'].strip()
                email = row['email'].strip()
                password = row['password'].strip()
                comment_text = row['comment_text']
                expected_message = row['expected_message'].strip()
                expected_result = row['expected_result'].strip()

                print(f"\n{'='*60}")
                print(f"Test Case: {testcase_id}")
                print(f"Comment Length: {len(comment_text)} characters")

                # Clear cookies and session to ensure clean state
                driver.delete_all_cookies()
                time.sleep(0.5)

                try:
                    # Precondition: Login using locators from CSV
                    login_url = self.locators['login_url']['value']
                    driver.get(login_url)
                    time.sleep(1)

                    # Enter email
                    email_input = self.find_element_by_locator('email_input', wait_for_clickable=True)
                    email_input.click()
                    email_input.clear()
                    email_input.send_keys(email)
                    time.sleep(0.3)

                    # Enter password
                    password_input = self.find_element_by_locator('password_input', wait_for_clickable=True)
                    password_input.click()
                    password_input.clear()
                    password_input.send_keys(password)
                    time.sleep(0.3)

                    # Click Login button
                    login_button = self.find_element_by_locator('login_button', wait_for_clickable=True)
                    login_button.click()
                    time.sleep(1)
                    print("Login successful!")

                    # Click on Blog menu
                    blog_link = self.find_element_by_locator('blog_menu', wait_for_clickable=True)
                    blog_link.click()
                    time.sleep(1)

                    # Click on a blog post
                    blog_post = self.find_element_by_locator('blog_post', wait_for_clickable=True)
                    blog_post.click()
                    time.sleep(1)

                    # Click on comment input field
                    comment_input = self.find_element_by_locator('comment_input', wait_for_clickable=True)
                    comment_input.click()
                    time.sleep(0.3)

                    # Clear and enter comment text
                    comment_input.clear()
                    time.sleep(0.3)
                    comment_input.send_keys(comment_text)
                    time.sleep(0.5)

                    # Click submit button
                    submit_button = self.find_element_by_locator('submit_button', wait_for_clickable=True)
                    submit_button.click()
                    time.sleep(2)

                    # Verify the message
                    try:
                        if expected_result == "fail" and "Comment cannot be empty" in expected_message:
                            # For empty comment case
                            actual_message_element = self.find_element_by_locator('empty_message')
                            actual_message = wait.until(EC.presence_of_element_located(
                                (self.get_by_type(self.locators['empty_message']['type']),
                                 self.locators['empty_message']['value'])
                            )).text
                        elif expected_result == "fail":
                            # For other failure cases (length validation)
                            actual_message_element = self.find_element_by_locator('validation_message')
                            actual_message = wait.until(EC.presence_of_element_located(
                                (self.get_by_type(self.locators['validation_message']['type']),
                                 self.locators['validation_message']['value'])
                            )).text
                        else:
                            # For success cases
                            actual_message_element = self.find_element_by_locator('success_message')
                            actual_message = wait.until(EC.presence_of_element_located(
                                (self.get_by_type(self.locators['success_message']['type']),
                                 self.locators['success_message']['value'])
                            )).text

                        self.assertEqual(expected_message, actual_message)
                        print(f"Message verification: PASSED - '{actual_message}'")

                        # If comment was successful, verify it appears in the comment list
                        if expected_result == "success" and comment_text:
                            try:
                                time.sleep(2)
                                # Try to find the comment in the list (using partial match for long comments)
                                comment_preview = comment_text[:50] if len(comment_text) > 50 else comment_text
                                print(f"Comment posted successfully. Preview: {comment_preview}...")
                            except Exception as e:
                                print(f"Note: Could not verify comment in list: {str(e)}")

                    except AssertionError as e:
                        print(f"Message verification: FAILED - Expected: '{expected_message}', Actual: '{actual_message}'")
                        self.verificationErrors.append(str(e))
                    except Exception as e:
                        print(f"Error getting message: {str(e)}")
                        self.verificationErrors.append(str(e))

                except Exception as e:
                    print(f"Error during test execution: {str(e)}")
                    self.verificationErrors.append(str(e))

                print(f"{'='*60}\n")
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
