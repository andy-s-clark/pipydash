from os import environ
import time
import logging

import yaml
from selenium import webdriver
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.keys import Keys

logging.basicConfig(level=logging.INFO)

class PiPyDash:
    def __init__(self):
        self.set_config({})
        self._browser = None

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
        try:
            for name, options in self.get_config()['pages'].items():
                self._load_page(name, options)
        except KeyError:
            logging.error('config is missing pages')
        self._browser.close()

    def _load_page(self, name, options):
        logging.info('Loading %s' % name)
        browser = self._browser
        if 'login' in options:
            try:
                browser.get(options['login']['url'])
                element = ui.WebDriverWait(browser, 15).until(lambda browser: browser.find_element_by_name(options['login']['username_element']))
                element.clear()
                element.send_keys(options['login']['username'])
                element = browser.find_element_by_name(options['login']['password_element'])
                element.clear()
                element.send_keys(options['login']['password'])
                element.send_keys(Keys.RETURN)
                time.sleep(5)
                browser.execute_script('window.open("%s", "%s");' % (options['url'], name))
            except KeyError:
                logging.error('%s is missing a login information' % name)
            print(options['login'])
        else:
            browser.execute_script('window.open("%s", "%s");' % (options['url'], name))

    def _cycle_windows(self):
        try:
            delay = self.get_config()['options']['delay']
        except KeyError:
            delay = 20
        # windows = self._browser.window_handles()
        # print(windows)
        time.sleep(5)

    def main(self):
        logging.debug(self.__config)
        profile = self.get_firefox_profile()
        self._browser = webdriver.Firefox(profile)
        self._load_pages()
        self._cycle_windows()
        self._browser.quit()
