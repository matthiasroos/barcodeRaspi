
import io
import unittest.mock

import freezegun
import pandas as pd
import pytest

import functions
import getraenkeapp


def get_stock_for_product(gk: getraenkeapp.GetraenkeApp, code: str):
    temp = gk.fileContents.products.loc[gk.fileContents.products['code'] == code, 'stock']
    return gk.fileContents.products.loc[gk.fileContents.products['code'] == code, 'stock'].item()


@pytest.fixture
def mock_functions(request, monkeypatch):
    mock_git_pull = unittest.mock.Mock(return_value=request.param['status_git_pull'])
    monkeypatch.setattr(target=functions, name='git_pull', value=mock_git_pull)
    mock_git_push = unittest.mock.Mock(return_value=True)
    monkeypatch.setattr(target=functions, name='git_push', value=mock_git_push)
    mock_write_csv = unittest.mock.Mock(return_value=None)
    monkeypatch.setattr(target=functions, name='write_csv_file', value=mock_write_csv)
    return mock_git_pull, mock_git_push, mock_write_csv


@pytest.fixture(autouse=False)
def mock_getraenkekasse():
    with unittest.mock.patch('wx.App', autospec=True), \
         unittest.mock.patch('wx.SystemSettings', autospec=True), \
         unittest.mock.patch('wx.Font', autospec=True):
        gk = getraenkeapp.GetraenkeApp()
        products = [[1, '1111111111111', 'xxxx', 0.60, 20], [2, '2222222222222', 'yyyy', 0.80, 0]]
        gk.fileContents.products = pd.DataFrame(products, columns=['nr', 'code', 'desc', 'price', 'stock'])
        purchases = [['2019-12-10T12:20:00', 'aaa', '1111111111111', False],
                     ['2019-12-10T16:30:00', 'bbb', '2222222222222', False],
                     ['2019-12-10T16:35:00', 'bbb', '2222222222222', False]]
        gk.fileContents.purchases = pd.DataFrame(purchases, columns=['timestamp', 'user', 'code', 'paid'])
        gk.fileContents.users = None
    return gk


@pytest.mark.parametrize('mock_functions', [dict(status_git_pull=True)], indirect=True)
def test_replenish_stock(mock_getraenkekasse, mock_functions):
    mock_git_pull, mock_git_push, mock_write_csv = mock_functions
    mock_getraenkekasse.replenish_stock([[1, 20, 23], [2, 0, 0]])
    new_value_1 = get_stock_for_product(mock_getraenkekasse, '1111111111111')
    new_value_2 = get_stock_for_product(mock_getraenkekasse, '2222222222222')
    assert new_value_1 == 23, new_value_2 == 0
    mock_git_pull.assert_called_once()
    mock_git_push.assert_called_once()
    mock_write_csv.assert_called_once_with(file=functions.PRODUCTS_FILE, df=mock_getraenkekasse.fileContents.products)


def test_decrease_stock_for_product(mock_getraenkekasse):
    status = mock_getraenkekasse._decrease_stock_for_product('1111111111111')
    new_value = get_stock_for_product(mock_getraenkekasse, '1111111111111')
    assert status is True
    assert new_value == 19

    status = mock_getraenkekasse._decrease_stock_for_product('2222222222222')
    new_value = get_stock_for_product(mock_getraenkekasse, '2222222222222')
    assert status is False
    assert new_value == 0


def test_set_paid_for_user(mock_getraenkekasse):
    mock_getraenkekasse._set_paid_for_user(user='bbb')
    assert mock_getraenkekasse.fileContents.purchases['paid'].tolist() == [False, True, True]
