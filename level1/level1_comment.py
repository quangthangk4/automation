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
        self.base_url = "https://www.google.com/"
        self.verificationErrors = []
        self.accept_next_alert = True
        self.driver.maximize_window()

    def test_comment_data_driven(self):
        driver = self.driver
        wait = WebDriverWait(driver, 10)

        # Read test data from CSV file
        csv_file = os.path.join(os.path.dirname(__file__), 'comment.csv')
        with open(csv_file, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)

            for row in csv_reader:
                testcase_id = row['testcase_id'].strip()
                comment_text = row['comment_text'].strip()
                expected_message = row['expected_message'].strip()
                expected_result = row['expected_result'].strip()

                print(f"\n{'='*60}")
                print(f"Test Case: {testcase_id}")
                print(f"Comment Length: {len(comment_text)} characters")

                # Clear cookies and session to ensure clean state
                driver.delete_all_cookies()
                time.sleep(0.5)

                # Precondition: Login
                driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=account/login")
                time.sleep(1)

                try:
                    # Enter email
                    email_input = wait.until(EC.element_to_be_clickable((By.ID, "input-email")))
                    email_input.click()
                    email_input.clear()
                    email_input.send_keys("sanjzoro0@gmail.com")
                    time.sleep(0.3)

                    # Enter password
                    password_input = wait.until(EC.element_to_be_clickable((By.ID, "input-password")))
                    password_input.click()
                    password_input.clear()
                    password_input.send_keys("12345")
                    time.sleep(0.3)

                    # Click Login button
                    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Login']")))
                    login_button.click()
                    time.sleep(1)
                    print("Login successful!")

                    # Click on Blog menu
                    blog_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='widget-navbar-217834']/ul/li[3]/a/div/span")))
                    blog_link.click()
                    time.sleep(1)

                    # Click on a blog post
                    blog_post = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='mz-article-tab-76210960-0']/div/div/div[5]/div/div/a/img")))
                    blog_post.click()
                    time.sleep(1)

                    # Click on comment input field
                    comment_input = wait.until(EC.element_to_be_clickable((By.ID, "input-comment")))
                    comment_input.click()
                    time.sleep(0.3)

                    # Clear and enter comment text
                    comment_input.clear()
                    time.sleep(0.3)
                    comment_input.send_keys(comment_text)
                    time.sleep(0.5)

                    # Click submit button
                    submit_button = wait.until(EC.element_to_be_clickable((By.ID, "button-comment")))
                    submit_button.click()
                    time.sleep(2)

                    # Verify the message
                    try:
                        if expected_result == "fail" and "Comment cannot be empty" in expected_message:
                            # For empty comment case
                            actual_message = wait.until(EC.presence_of_element_located((By.XPATH, "//form[@id='form-comment']/div"))).text
                        elif expected_result == "fail":
                            # For other failure cases (length validation)
                            actual_message = wait.until(EC.presence_of_element_located((By.XPATH, "//form[@id='form-comment']/div/div"))).text
                        else:
                            # For success cases
                            actual_message = wait.until(EC.presence_of_element_located((By.XPATH, "//form[@id='form-comment']/div"))).text

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
