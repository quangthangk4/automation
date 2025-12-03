# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest
import time
import csv
import os

class BookAppointments(unittest.TestCase):
    def setUp(self):
        # Cấu hình Chrome options
        chrome_options = Options()
        
        # TẠO PROFILE RIÊNG để tránh popup password
        user_data_dir = os.path.join(os.getcwd(), "chrome_test_profile")
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        chrome_options.add_argument("--profile-directory=Default")
        
        # Tắt mọi thứ liên quan password manager
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-save-password-bubble')
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
            "profile.password_manager_leak_detection": False
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Khởi tạo driver
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 20)
        self.base_url = "https://www.google.com/"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_book_appointments_data_driven(self):
        driver = self.driver
        wait = self.wait
        
        # Đọc data từ CSV file
        try:
            with open('appointments.csv', 'r', encoding='utf-8') as csvfile:
                csv_reader = csv.DictReader(csvfile)
                
                test_number = 1
                for row in csv_reader:
                    # Lấy data từ mỗi row
                    date_value = row['Date_file']
                    comment_value = row['Comment_file']
                    expected_result = row['Expected Result']
                    
                    print(f"\n{'='*60}")
                    print(f"TEST CASE #{test_number}")
                    print(f"  - Date: {date_value}")
                    print(f"  - Comment: {comment_value}")
                    print(f"  - Expected: {expected_result}")
                    print(f"{'='*60}")
                    
                    try:
                        # Navigate to website
                        driver.get("https://katalon-demo-cura.herokuapp.com/")
                        
                        # Click menu
                        wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@id='menu-toggle']/i"))).click()
                        
                        # Click Login
                        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Login"))).click()
                        
                        # Enter username
                        username_field = wait.until(EC.presence_of_element_located((By.ID, "txt-username")))
                        username_field.clear()
                        username_field.send_keys("John Doe")
                        
                        # Enter password
                        password_field = driver.find_element(By.ID, "txt-password")
                        password_field.clear()
                        password_field.send_keys("ThisIsNotAPassword")
                        
                        # Click login button
                        driver.find_element(By.ID, "btn-login").click()
                        
                        # ĐỢI PAGE LOAD - quan trọng!
                        wait.until(EC.presence_of_element_located((By.ID, "txt_visit_date")))
                        time.sleep(1)
                        
                        # Enter visit date
                        date_field = driver.find_element(By.ID, "txt_visit_date")
                        date_field.clear()
                        date_field.send_keys(date_value)
                        
                        # Enter comment
                        comment_field = driver.find_element(By.ID, "txt_comment")
                        comment_field.clear()
                        comment_field.send_keys(comment_value)
                        
                        # Click book appointment
                        driver.find_element(By.ID, "btn-book-appointment").click()
                        
                        # Wait for confirmation page
                        wait.until(EC.presence_of_element_located((By.XPATH, "//section[@id='summary']/div/div/div/h2")))
                        
                        # Verify result
                        actual_result = driver.find_element(By.XPATH, "//section[@id='summary']/div/div/div/h2").text
                        
                        if expected_result == actual_result:
                            print(f"✓ TEST PASSED")
                            print(f"  Expected: '{expected_result}'")
                            print(f"  Actual:   '{actual_result}'")
                        else:
                            self.verificationErrors.append(f"Test {test_number} failed: Expected '{expected_result}', got '{actual_result}'")
                            print(f"✗ TEST FAILED")
                            print(f"  Expected: '{expected_result}'")
                            print(f"  Actual:   '{actual_result}'")
                        
                        # Logout
                        wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@id='menu-toggle']/i"))).click()
                        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Logout"))).click()
                        time.sleep(1)
                        
                    except Exception as e:
                        error_msg = f"Test {test_number} encountered error: {str(e)}"
                        self.verificationErrors.append(error_msg)
                        print(f"✗ ERROR: {error_msg}")
                        # Take screenshot for debugging
                        driver.save_screenshot(f"error_test_{test_number}.png")
                        print(f"  Screenshot saved: error_test_{test_number}.png")
                    
                    test_number += 1
                    
        except FileNotFoundError:
            print("ERROR: File 'appointments.csv' not found!")
            print("Please create the CSV file in the same directory as this script.")
    
    def is_element_present(self, how, what):
        try: 
            self.driver.find_element(by=how, value=what)
            return True
        except NoSuchElementException: 
            return False
    
    def tearDown(self):
        time.sleep(2)  # Pause để xem kết quả
        self.driver.quit()
        
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY")
        print(f"{'='*60}")
        if self.verificationErrors:
            print(f"❌ {len(self.verificationErrors)} test(s) FAILED:")
            for error in self.verificationErrors:
                print(f"  - {error}")
        else:
            print(f"✅ ALL TESTS PASSED!")
        print(f"{'='*60}\n")

if __name__ == "__main__":
    unittest.main()