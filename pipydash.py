from os import environ
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from Xlib.display import Display
import Xlib.protocol
import Xlib.X
import Xlib.XK
import yaml

logging.basicConfig(level=logging.INFO)


class PiPyDash:
    def __init__(self):
        self.set_config({})
        self._driver = None
        self._display = Display()
        self._root = self._display.screen().root

    def set_config(self, config):
        self.__config = config

    def get_config(self):
        return self.__config

    def get_display(self):
        return self._display

    def get_root(self):
        return self._root

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
                element = WebDriverWait(driver, 15).until(
                    lambda until_driver: until_driver.find_element_by_name(options['login']['username_element']))
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

    @staticmethod
    def _get_windows_by_class_info(window_list, class_info):
        target_windows = []
        while len(window_list) != 0:
            window = window_list.pop(0)
            window_class_info = window.get_wm_class()
            if window_class_info is not None and window_class_info == class_info:
                target_windows.append(window)
            children = window.query_tree().children
            if children is not None:
                window_list += children
        return target_windows

    def _send_key_to_window(self, window, key):
        display = self.get_display()
        root = self.get_root()
        keysym = Xlib.XK.string_to_keysym(key)
        keycode = display.keysym_to_keycode(keysym)

        display.set_input_focus(window, Xlib.X.RevertToParent, Xlib.X.CurrentTime)
        event = Xlib.protocol.event.KeyPress(
            time=int(time.time()),
            root=root,
            window=window,
            same_screen=0,
            child=Xlib.X.NONE,
            root_x=0, root_y=0, event_x=0, event_y=0,
            state=0,
            detail=keycode
        )
        display.send_event(window, event, propagate=True)
        event = Xlib.protocol.event.KeyRelease(
            time=int(time.time()),
            root=root,
            window=window,
            same_screen=0,
            child=Xlib.X.NONE,
            root_x=0, root_y=0, event_x=0, event_y=0,
            state=0,
            detail=keycode
        )
        display.send_event(window, event, propagate=True)

    def _cycle_windows(self):
        try:
            delay = self.get_config()['options']['delay']
        except KeyError:
            delay = 10
        display = self.get_display()
        windows = self._get_windows_by_class_info([self.get_root()], ('Navigator', 'Firefox'))
        for window in windows:
            self._send_key_to_window(window, "a")  # F11 Fullscreen doesn't seem to cycle
            display.sync()
        for count in range(0, 3):  # Temporary for debugging
            for window in windows:
                print("%d: %s" % (count, window.get_wm_name()))
                window.raise_window()
                display.sync()
                time.sleep(delay)
        display.close()

    def main(self):
        logging.debug(self.__config)
        profile = self.get_firefox_profile()
        self._driver = webdriver.Firefox(profile)
        self._load_pages()
        self._cycle_windows()
        self._driver.quit()
