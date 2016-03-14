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

    def __init__(self, config=None):
        self.driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true', '--ssl-protocol=tlsv1'])
        self.driver.implicitly_wait(5)
        self.verificationErrors = []
        self.accept_next_alert = True
        
        self.login_flg = False
        self.base_url = None
        self.username = None
        self.password = None
        self.username_selector = None
        self.password_selector = None 
        self.login_btn_selector = None
        self.login_path = None
        self.set_config(config)

    def set_config(self, config):
        if config is not None and isinstance(config, dict):
            if 'base_url' in config:
                self.base_url = config['base_url']
            if 'username' in config:
                self.username = config['username']
            if 'password' in config:
                self.password = config['password']
            if 'username_selector' in config:
                self.username_selector = config['username_selector']
            if 'password_selector' in config:
                self.password_selector = config['password_selector']
            if 'login_btn_selector' in config:
                self.login_btn_selector = config['login_btn_selector']
            if 'login_path' in config:
                self.login_path = config['login_path']

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

    def clear(self, selector, element=None):
        self.find(selector, element).clear()

    def send_keys(self, selector, keys, element=None):
        self.find(selector, element).send_keys(keys)

    def click(self, selector, element=None):
        self.find(selector, element).click()

    def is_login(self):
        return self.login_flg

    def login(self, login_path=None, username_selector=None, username=None, password_selector=None, password=None, login_btn_selector=None):
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
            self.clear(us)
            self.send_keys(us, u)
            self.clear(ps)
            self.send_keys(ps, p)
            self.click(lbs)
            self.login_flg = True
        except Exception, e:
            self.quit()
            raise e

    def logout(self, logout_path, logout_btn_selector=None):
        try:
            lp = logout_path
            lbs = logout_btn_selector
            self.get_page(lp)
            if lbs is not None:
                self.click(lbs)
            self.login_flg = False
        except Exception, e:
            self.quit()

    def quit(self):
        self.driver.quit()
        self.login_flg = False

