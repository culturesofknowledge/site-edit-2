from selenium.webdriver import Keys


def remove_all_text(element):
    element.send_keys(Keys.CONTROL, 'a')
    element.send_keys(Keys.BACKSPACE)
