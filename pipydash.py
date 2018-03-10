from os import environ
import time
import logging

import yaml
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

logging.basicConfig(level=logging.INFO)


class PiPyDash:
    def __init__(self):
        self.set_config({})
        self._driver = None

    def set_config(self, config):
        self.__config = config

    def get_config(self):
        return self.__config

    @staticmethod
    def read_config_file(config_file_path):
        with open(config_file_path) as config_file_handle:
            return yaml.load(config_file_handle)

    def get_firefox_profile(self):
        config = self.get_config()
        profile = webdriver.FirefoxProfile()
        try:
            for k, v in config['options']['firefox_profile']['preferences'].items():
                profile.set_preference(k, v)
        except KeyError:
            logging.info('No firefox_profile defined')
        return profile

    def _load_pages(self):
        driver = self._driver
        try:
            for name, options in self.get_config()['pages'].items():
                self._load_page(name, options)
        except KeyError:
            logging.error('config is missing pages')
        driver.switch_to.window(driver.window_handles[0])
        driver.close()

    def _load_page(self, name, options):
        driver = self._driver
        logging.info('Loading %s' % name)
        driver.execute_script('window.open("about:blank", "%s");' % name)
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(options['url'])
        if 'login' in options:
            try:
                element = WebDriverWait(driver, 15).until(lambda driver: driver.find_element_by_name(options['login']['username_element']))
                element.clear()
                element.send_keys(options['login']['username'])
                element = driver.find_element_by_name(options['login']['password_element'])
                element.clear()
                element.send_keys(options['login']['password'])
                element.send_keys(Keys.RETURN)
            except KeyError:
                logging.error('%s is missing a login information' % name)
        else:
            driver.execute_script('window.open("%s", "%s");' % (options['url'], name))
            # print(driver.window_handles)

    def _cycle_windows(self):
        try:
            delay = self.get_config()['options']['delay']
        except KeyError:
            delay = 10
        driver = self._driver
        for handle in driver.window_handles:
            time.sleep(2)
            driver.switch_to.window(handle)
            driver.execute_script('window.focus();')
            driver.find_element_by_xpath('/html/body').send_keys(Keys.F11)
            driver.maximize_window()

        time.sleep(delay)

    def main(self):
        logging.debug(self.__config)
        profile = self.get_firefox_profile()
        self._driver = webdriver.Firefox(profile)
        self._load_pages()
        self._cycle_windows()
        self._driver.quit()
