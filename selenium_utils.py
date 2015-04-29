# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import datetime, time

class SeleniumUtils(object):

    def __init__(self, username_selector, password_selector, login_btn_selector, login_path, config=None):
        self.driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true', '--ssl-protocol=tlsv1'])
        self.driver.implicitly_wait(5)
        self.verificationErrors = []
        self.accept_next_alert = True

        self.username_selector = username_selector
        self.password_selector = password_selector
        self.login_btn_selector = login_btn_selector
        self.login_path = login_path
        
        self.login_flg = False
        self.base_url = None
        self.username = None
        self.password = None
        self.set_config(config)

    def set_config(self, config):
        if config is not None:
            self.base_url = config['base_url']
            self.username = config['username']
            self.password = config['password']

    def get_page(self, path):
        self.driver.get(self.base_url + path)

    def wait(self, sec):
        return WebDriverWait(self.driver, sec)
       
    def attr(self, element, name):
        result = None
        result = element.get_attribute(name)
        return result

    def _get_target(self, element):
        result = self.driver
        if element is not None:
            result = element
        return result

    def finds(self, selector, element=None):
        result = None
        target = self._get_target(element)
        result = target.find_elements_by_css_selector(selector)
        return result

    def find(self, selector, element=None):
        result = None
        target = self._get_target(element)
        result = target.find_element_by_css_selector(selector)
        return result

    def send_keys(self, selector, keys, element=None):
        self.find(selector, element).send_keys(keys)

    def click(self, selector, element=None):
        self.find(selector, element).click()

    def login(self, login_path=None, username_selector=None, username=None, password_selector=None, password=None, login_btn_selector=None):
        #print "login"
        try:
            lp = self.login_path
            if login_path is not None:
                lp = login_path
            us = self.username_selector
            if username_selector is not None:
                us = username_selector
            u = self.username
            if username is not None:
                u = username
            ps = self.password_selector
            if password_selector is not None:
                ps = password_selector
            p = self.password
            if password is not None:
                p = password
            lbs = self.login_btn_selector
            if login_btn_selector is not None:
                lbs = login_btn_selector

            self.get_page(lp)
            #print self.driver.current_url
            self.send_keys(us, u)
            self.send_keys(ps, p)
            self.click(lbs)
            self.login_flg = True
            #print "login end"
        except Exception, e:
            self.quit()
            raise e

    def quit(self):
        self.driver.quit()
        self.login_flg = False

