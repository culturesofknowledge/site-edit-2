"""
functions for Interactive Emlo-edit website with selenium driver
"""
from typing import Iterable

from selenium.webdriver.common.by import By


def login(driver, username, raw_password):
    find_element_by_css(driver, 'input[name=username]').send_keys(username)
    find_element_by_css(driver, 'input[name=password]').send_keys(raw_password)
    find_element_by_css(driver, 'button').click()


def find_elements_by_css(driver, css_selector):
    return driver.find_elements(by=By.CSS_SELECTOR, value=css_selector)


def find_element_by_css(driver, css_selector):
    return driver.find_element(by=By.CSS_SELECTOR, value=css_selector)


def click_submit(driver):
    driver.find_element(By.CSS_SELECTOR, 'button[type=submit].sticky-btn').click()


def js_click(driver, selector):
    script = f"document.querySelector('{selector}').click(); "
    driver.execute_script(script)


def switch_to_new_window(driver):
    return SwitchToNewWindow(driver)


def fill_val_by_selector_list(driver, selector_list: Iterable[tuple]):
    for selector, val in selector_list:
        ele = driver.find_element(by=By.CSS_SELECTOR, value=selector)
        ele.send_keys(val)


def fill_form_by_dict(driver,
                      model_dict: dict,
                      exclude_fields: Iterable[str] = None):
    if exclude_fields is not None and (exclude_fields := set(exclude_fields)):
        model_dict = ((k, v) for k, v in model_dict if k not in exclude_fields)
    fill_val_by_selector_list(driver, ((f'#id_{k}', v) for k, v in model_dict))


def fill_formset_by_dict(driver, data: dict, formset_prefix, form_idx=0):
    fill_val_by_selector_list(driver, ((f'#id_{formset_prefix}-{form_idx}-{k}', v)
                                       for k, v in data.items()))


class SwitchToNewWindow:
    def __init__(self, driver):
        self.driver = driver
        self.window_handlers = set()

    def __enter__(self):
        self.window_handlers = set(self.driver.window_handles)

    def __exit__(self, exc_type, exc_val, exc_tb):
        new_win_set = set(self.driver.window_handles) - self.window_handlers
        if not new_win_set:
            raise RuntimeError(f'No new windows found [{self.driver.window_handles}] ')
        self.driver.switch_to.window(list(new_win_set)[0])


def is_403(driver):
    return '403 Forbidden' in driver.page_source
