import doctest

from core.helper import date_serv, query_serv


def load_tests(loader, tests, ignore):
    doctest_modules = [
        date_serv,
        query_serv,
    ]

    tests.addTests(
        map(doctest.DocTestSuite, doctest_modules)
    )
    return tests
