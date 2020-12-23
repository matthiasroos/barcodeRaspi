
import logging
import unittest.mock

import pandas as pd
import pytest

import src.app
import tests.test_getraenkeapp


@pytest.fixture(autouse=False)
def mock_app():
    with unittest.mock.patch.multiple('src.app.App', __abstractmethods__=set()), \
         unittest.mock.patch('wx.App', autospec=True), \
         unittest.mock.patch('wx.SystemSettings', autospec=True), \
         unittest.mock.patch('wx.Font', autospec=True):
        app = src.app.App()
        products = [[1, '1111111111111', 'xxxx', 0.60, 20],
                    [2, '2222222222222', 'yyyy', 0.80, 0]]
        app.file_contents.products = pd.DataFrame(products, columns=tests.test_getraenkeapp.columns_products)
        purchases = [['2019-12-10T12:20:00', 'aaa', '1111111111111', False],
                     ['2019-12-10T16:30:00', 'bbb', '2222222222222', False],
                     ['2019-12-10T16:35:00', 'bbb', '2222222222222', False]]
        app.file_contents.purchases = pd.DataFrame(purchases, columns=tests.test_getraenkeapp.columns_purchases)
        app.file_contents.users = None
    return app


def test_create_new_product_success(mock_app):

    new_item_df = mock_app.create_new_product(values={'nr': 3,
                                                      'code': '333333333333',
                                                      'desc': 'zzzz',
                                                      'price': 0.10,
                                                      'stock': 50})

    pd.testing.assert_frame_equal(new_item_df, pd.DataFrame([[3, '333333333333', 'zzzz', 0.10, 50]],
                                                            columns=tests.test_getraenkeapp.columns_products))


def test_create_new_product_error(mock_app, caplog):
    caplog.set_level(level=logging.INFO)

    with unittest.mock.patch('wx.MessageDialog', autospec=True):
        new_item_df = mock_app.create_new_product(values={'nr': 3,
                                                          'code': '3333333333333',
                                                          'desc': 'zzzz',
                                                          'price': 'abc',
                                                          'stock': 50})

    assert new_item_df is None
    assert caplog.record_tuples == [
        ('App', logging.ERROR, "error message: Error: could not convert string to float: 'abc'")]


def test_get_product_for_code_correct_code(mock_app):

    price, desc = mock_app.get_product_for_code(code='1111111111111')

    assert price == 0.60
    assert desc == 'xxxx'


def test_get_product_for_code_invalid_code(mock_app):

    price, desc = mock_app.get_product_for_code(code='3333333333333')

    assert price is None
    assert desc == 'invalid code'


def test_get_product_for_code_code_too_short(mock_app):

    price, desc = mock_app.get_product_for_code(code='444')

    assert price is None
    assert desc is None
