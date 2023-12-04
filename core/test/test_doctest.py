import doctest

from core.helper import date_serv


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(date_serv))
    return tests
