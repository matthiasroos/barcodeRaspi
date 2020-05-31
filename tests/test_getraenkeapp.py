
import unittest.mock

import freezegun
import pandas as pd
import pytest

import functions
import src.getraenkeKasse.getraenkeapp

columns_purchases = ['timestamp', 'user', 'code', 'paid']
columns_products = ['nr', 'code', 'desc', 'price', 'stock']


def get_stock_for_product(gk: src.getraenkeKasse.getraenkeapp.GetraenkeApp, code: str) -> int:
    return gk.fileContents.products.loc[gk.fileContents.products['code'] == code, 'stock'].item()


def get_purchases_for_user(gk: src.getraenkeKasse.getraenkeapp.GetraenkeApp, user: str) -> pd.DataFrame:
    return gk.fileContents.purchases[gk.fileContents.purchases['user'] == user]


@pytest.fixture(autouse=False)
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
        gk = src.getraenkeKasse.getraenkeapp.GetraenkeApp()
        products = [[1, '1111111111111', 'xxxx', 0.60, 20], [2, '2222222222222', 'yyyy', 0.80, 0]]
        gk.fileContents.products = pd.DataFrame(products, columns=columns_products)
        purchases = [['2019-12-10T12:20:00', 'aaa', '1111111111111', False],
                     ['2019-12-10T16:30:00', 'bbb', '2222222222222', False],
                     ['2019-12-10T16:35:00', 'bbb', '2222222222222', False]]
        gk.fileContents.purchases = pd.DataFrame(purchases, columns=columns_purchases)
        gk.fileContents.users = None
    return gk


def test_set_stock_for_product(mock_getraenkekasse):
    mock_getraenkekasse._set_stock_for_product(nr=1, stock=23)
    assert get_stock_for_product(mock_getraenkekasse, '1111111111111') == 23


@pytest.mark.parametrize('mock_functions', [dict(status_git_pull=True)], indirect=True)
def test_replenish_stock(mock_getraenkekasse, mock_functions):
    mock_git_pull, mock_git_push, mock_write_csv = mock_functions
    mock_getraenkekasse.replenish_stock([[1, 20, 23], [2, 0, 0]])
    assert get_stock_for_product(mock_getraenkekasse, '1111111111111') == 23
    assert get_stock_for_product(mock_getraenkekasse, '2222222222222') == 0
    mock_git_pull.assert_called_once()
    mock_git_push.assert_called_once()
    mock_write_csv.assert_called_once_with(file=src.getraenkeKasse.getraenkeapp.PRODUCTS_FILE, df=mock_getraenkekasse.fileContents.products)


def test_decrease_stock_for_product0(mock_getraenkekasse):
    status = mock_getraenkekasse._decrease_stock_for_product('1111111111111')
    assert status is True
    assert get_stock_for_product(mock_getraenkekasse, '1111111111111') == 19


def test_decrease_stock_for_product1(mock_getraenkekasse):
    status = mock_getraenkekasse._decrease_stock_for_product('2222222222222')
    assert status is False
    assert get_stock_for_product(mock_getraenkekasse, '2222222222222') == 0


def test_set_paid_for_user(mock_getraenkekasse):
    mock_getraenkekasse._set_paid_for_user(user='bbb')
    assert mock_getraenkekasse.fileContents.purchases['paid'].tolist() == [False, True, True]


@pytest.mark.parametrize('mock_functions', [dict(status_git_pull=True)], indirect=True)
def test_pay_for_user(mock_getraenkekasse, mock_functions):
    mock_git_pull, mock_git_push, mock_write_csv = mock_functions
    mock_getraenkekasse.pay_for_user('aaa')
    assert mock_getraenkekasse.fileContents.purchases['paid'].tolist() == [True, False, False]
    mock_git_pull.assert_called_once_with(path_repo='./.')
    mock_git_push.assert_called_once_with(path_repo='./.', files=[src.getraenkeKasse.getraenkeapp.PURCHASES_FILE],
                                          commit_message='pay for user aaa via getraenkeKasse.py')
    mock_write_csv.assert_called_once_with(file=src.getraenkeKasse.getraenkeapp.PURCHASES_FILE,
                                           df=mock_getraenkekasse.fileContents.purchases)


@freezegun.freeze_time('2019-12-10 17:00:00')
@pytest.mark.parametrize('mock_functions', [dict(status_git_pull=True)], indirect=True)
def test_make_purchase_stock_available(mock_getraenkekasse, mock_functions):
    mock_git_pull, mock_git_push, mock_write_csv = mock_functions
    expected_df = pd.DataFrame([['2019-12-10T12:20:00', 'aaa', '1111111111111', False],
                                ['2019-12-10T17:00:00', 'aaa', '1111111111111', False]],
                               columns=columns_purchases, index=[0, 3])
    mock_getraenkekasse.make_purchase(user='aaa', code='1111111111111')
    pd.testing.assert_frame_equal(get_purchases_for_user(gk=mock_getraenkekasse, user='aaa'), expected_df)
    assert get_stock_for_product(mock_getraenkekasse, '1111111111111') == 19
    mock_git_pull.assert_called_once_with(path_repo='./.')
    mock_git_push.assert_called_once_with(path_repo='./.', files=[src.getraenkeKasse.getraenkeapp.PURCHASES_FILE,
                                                                 src.getraenkeKasse.getraenkeapp.PRODUCTS_FILE],
                                          commit_message='purchase via getraenkeKasse.py')
    mock_write_csv.assert_has_calls([unittest.mock.call(file=src.getraenkeKasse.getraenkeapp.PURCHASES_FILE,
                                                        df=mock_getraenkekasse.fileContents.purchases),
                                     unittest.mock.call(file=src.getraenkeKasse.getraenkeapp.PRODUCTS_FILE,
                                                        df=mock_getraenkekasse.fileContents.products)])


@freezegun.freeze_time('2019-12-10 18:00:00')
@pytest.mark.parametrize('mock_functions', [dict(status_git_pull=True)], indirect=True)
def test_make_purchase_stock_empty(mock_getraenkekasse, mock_functions):
    mock_git_pull, mock_git_push, mock_write_csv = mock_functions
    expected_df = pd.DataFrame([['2019-12-10T12:20:00', 'aaa', '1111111111111', False],
                                ['2019-12-10T18:00:00', 'aaa', '2222222222222', False]],
                               columns=columns_purchases, index=[0, 3])
    mock_getraenkekasse.make_purchase(user='aaa', code='2222222222222')
    pd.testing.assert_frame_equal(get_purchases_for_user(gk=mock_getraenkekasse, user='aaa'), expected_df)
    assert get_stock_for_product(mock_getraenkekasse, '2222222222222') == 0
    mock_git_pull.assert_called_once_with(path_repo='./.')
    mock_git_push.assert_called_once_with(path_repo='./.', files=[src.getraenkeKasse.getraenkeapp.PURCHASES_FILE],
                                          commit_message='purchase via getraenkeKasse.py')
    mock_write_csv.assert_called_once_with(file=src.getraenkeKasse.getraenkeapp.PURCHASES_FILE,
                                           df=mock_getraenkekasse.fileContents.purchases)
