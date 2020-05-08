
import io
import unittest.mock

import freezegun
import pandas as pd
import pytest

import getraenkeapp


@pytest.fixture
def mock_getraenkekasse():
    gk = getraenkeapp.GetraenkeApp()
    products = [[1, '1111111111111', 'xxxx', 0.60, 20], [2, '2222222222222', 'yyyy', 0.80, 0]]
    gk.fileContents.products = pd.DataFrame(products, columns=['nr', 'code', 'desc', 'price', 'stock'])
    purchases = [['2019-12-10T12:20:00', 'aaa', '111111111111', False],
                 ['2019-12-10T16:30:00', 'bbb', '222222222222', False],
                 ['2019-12-10T16:35:00', 'bbb', '222222222222', False]]
    gk.fileContents.purchases = pd.DataFrame(purchases, columns=['timestamp', 'user', 'code', 'paid'])
    gk.fileContents.users = None
    return gk


def test_decrease_stock_for_product(mock_getraenkekasse):
    status = mock_getraenkekasse._decrease_stock_for_product('1111111111111')
    new_value = mock_getraenkekasse.fileContents.products.loc[
               mock_getraenkekasse.fileContents.products['code'] == '1111111111111', 'stock'].item()
    assert status is True
    assert new_value == 19

    status = mock_getraenkekasse._decrease_stock_for_product('2222222222222')
    new_value = mock_getraenkekasse.fileContents.products.loc[
               mock_getraenkekasse.fileContents.products['code'] == '2222222222222', 'stock'].item()
    assert status is False
    assert new_value == 0


def test_set_paid_for_user(mock_getraenkekasse):
    mock_getraenkekasse._set_paid_for_user(user='bbb')
    assert mock_getraenkekasse.fileContents.purchases['paid'].tolist() == [False, True, True]
