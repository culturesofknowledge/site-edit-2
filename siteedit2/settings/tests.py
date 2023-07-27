from siteedit2.settings.base import *  # noqa

ALLOWED_HOSTS = ['0.0.0.0', 'localhost', 'pycharm-py']

# there will have some exception messages if STATIC_ROOT not exist
STATIC_ROOT = '/static'

TEST_WEB_HOST = 'pycharm-py'
SELENIUM_HOST_PORT = 'chrome:4444'

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SELENIUM_CHROME_LOCAL_DRIVER = False
