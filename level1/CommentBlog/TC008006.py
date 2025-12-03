# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re

class TC008006(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(executable_path=r'')
        self.driver.implicitly_wait(30)
        self.base_url = "https://www.google.com/"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_t_c008006(self):
        driver = self.driver
        driver.get("https://ecommerce-playground.lambdatest.io/")
        driver.find_element_by_xpath("//div[@id='widget-navbar-217834']/ul/li[3]/a/div/span").click()
        driver.find_element_by_xpath("//div[@id='mz-article-tab-76210960-0']/div/div/div[5]/div/div/a/img").click()
        driver.find_element_by_id("input-comment").click()
        driver.find_element_by_id("input-comment").clear()
        driver.find_element_by_id("input-comment").send_keys("this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is2")
        driver.find_element_by_id("button-comment").click()
        time.sleep(2)
        driver.find_element_by_xpath("//form[@id='form-comment']/div").click()
        try: self.assertEqual("Thank you for your comment. It has been submitted to the webmaster for approval.", driver.find_element_by_xpath("//form[@id='form-comment']/div").text)
        except AssertionError as e: self.verificationErrors.append(str(e))
        driver.find_element_by_xpath("//li[@id='comment3947']/div/p").click()
        try: self.assertEqual("this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is exactly 1000 characters.this is2", driver.find_element_by_xpath("//li[@id='comment3947']/div/p").text)
        except AssertionError as e: self.verificationErrors.append(str(e))
        driver.find_element_by_xpath("//li[@id='comment3947']/div/h6").click()
        try: self.assertEqual("Loser Lord", driver.find_element_by_xpath("//li[@id='comment3947']/div/h6").text)
        except AssertionError as e: self.verificationErrors.append(str(e))
    
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
