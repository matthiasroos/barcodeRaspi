
import time
import unittest.mock

import freezegun
import pandas as pd
import pytest

import functions
import src.getraenkeKasse.getraenkeapp

columns_purchases = ['timestamp', 'user', 'code', 'paid']
columns_products = ['nr', 'code', 'desc', 'price', 'stock']

TEST_PRODUCTS_FILE = 'test_file_1'
TEST_PURCHASES_FILE = 'test_file_2'
TEST_USERS_FILE = 'test_file_3'


def get_stock_for_product(gk: src.getraenkeKasse.getraenkeapp.GetraenkeApp, code: str) -> int:
    return gk.file_contents.products.loc[gk.file_contents.products['code'] == code, 'stock'].item()


def get_purchases_for_user(gk: src.getraenkeKasse.getraenkeapp.GetraenkeApp, user: str) -> pd.DataFrame:
    return gk.file_contents.purchases[gk.file_contents.purchases['user'] == user]


@pytest.fixture(autouse=False)
def mock_functions(monkeypatch):
    mock_write_csv = unittest.mock.Mock(return_value=None)
    monkeypatch.setattr(target=functions, name='write_csv_file', value=mock_write_csv)
    return mock_write_csv


@pytest.fixture(autouse=False)
def mock_getraenkekasse():
    with unittest.mock.patch('wx.App', autospec=True), \
         unittest.mock.patch('wx.SystemSettings', autospec=True), \
         unittest.mock.patch('wx.Font', autospec=True), \
         unittest.mock.patch('src.getraenkeKasse.git.GitRepository', autospec=True), \
         unittest.mock.patch('src.getraenkeKasse.timer.UpdateTimer', autospec=True):
        gk = src.getraenkeKasse.getraenkeapp.GetraenkeApp(button_height=1,
                                                          button_width=1,
                                                          font_size=1,
                                                          offset=1,
                                                          file_names={'products': TEST_PRODUCTS_FILE,
                                                                      'purchases': TEST_PURCHASES_FILE,
                                                                      'users': TEST_USERS_FILE},
                                                          repositories={'kasse': 'test1',
                                                                        'code': 'test2'})
        products = [[1, '1111111111111', 'xxxx', 0.60, 20],
                    [2, '2222222222222', 'yyyy', 0.80, 0]]
        gk.file_contents.products = pd.DataFrame(products, columns=columns_products)
        purchases = [['2019-12-10T12:20:00', 'aaa', '1111111111111', False],
                     ['2019-12-10T16:30:00', 'bbb', '2222222222222', False],
                     ['2019-12-10T16:35:00', 'bbb', '2222222222222', False]]
        gk.file_contents.purchases = pd.DataFrame(purchases, columns=columns_purchases)
        gk.file_contents.users = None
    return gk


def test_set_stock_for_product(mock_getraenkekasse):
    mock_getraenkekasse._set_stock_for_product(nr=1, stock=23)
    assert get_stock_for_product(mock_getraenkekasse, '1111111111111') == 23


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
    assert mock_getraenkekasse.file_contents.purchases['paid'].tolist() == [False, True, True]


def test_save_admin_changes_one_user_paid(mock_getraenkekasse, mock_functions):
    mock_write_csv = mock_functions
    mock_getraenkekasse.repo_kasse.commit.return_value = True
    mock_getraenkekasse.repo_kasse.pull.return_value = True

    mock_getraenkekasse.save_admin_changes(user_paid=['bbb'],
                                           changed_stock=[])

    time.sleep(2)

    pd.testing.assert_frame_equal(get_purchases_for_user(gk=mock_getraenkekasse, user='bbb'),
                                  pd.DataFrame([
                                      ['2019-12-10T16:30:00', 'bbb', '2222222222222', True],
                                      ['2019-12-10T16:35:00', 'bbb', '2222222222222', True]],
                                      columns=columns_purchases, index=[1, 2]))
    mock_getraenkekasse.repo_kasse.commit.assert_called_once_with(
        files=[TEST_PURCHASES_FILE],
        commit_message='pay for user bbb via getraenkeKasse.py')
    mock_getraenkekasse.repo_kasse.push.assert_called_once_with()
    mock_write_csv.assert_has_calls([unittest.mock.call(file=TEST_PURCHASES_FILE,
                                                        df=mock_getraenkekasse.file_contents.purchases)])


def test_save_admin_changes_stock_replenished(mock_getraenkekasse, mock_functions):
    mock_write_csv = mock_functions
    mock_getraenkekasse.repo_kasse.commit.return_value = True
    mock_getraenkekasse.repo_kasse.pull.return_value = True

    mock_getraenkekasse.save_admin_changes(user_paid=[],
                                           changed_stock=[[2, 0, 30]])

    time.sleep(2)

    assert get_stock_for_product(gk=mock_getraenkekasse, code='2222222222222') == 30
    mock_getraenkekasse.repo_kasse.commit.assert_called_once_with(
        files=[TEST_PRODUCTS_FILE],
        commit_message='replenish stock via getraenkeKasse.py')
    mock_getraenkekasse.repo_kasse.push.assert_called_once_with()
    mock_write_csv.assert_has_calls([unittest.mock.call(file=TEST_PRODUCTS_FILE,
                                                        df=mock_getraenkekasse.file_contents.products)])


def test_save_admin_changes_user_paid_and_stock_replenished(mock_getraenkekasse, mock_functions):
    mock_write_csv = mock_functions
    mock_getraenkekasse.repo_kasse.commit.return_value = True
    mock_getraenkekasse.repo_kasse.pull.return_value = True

    mock_getraenkekasse.save_admin_changes(user_paid=['bbb'],
                                           changed_stock=[[2, 0, 30]])

    time.sleep(2)

    pd.testing.assert_frame_equal(get_purchases_for_user(gk=mock_getraenkekasse, user='bbb'),
                                  pd.DataFrame([
                                      ['2019-12-10T16:30:00', 'bbb', '2222222222222', True],
                                      ['2019-12-10T16:35:00', 'bbb', '2222222222222', True]],
                                      columns=columns_purchases, index=[1, 2]))
    assert get_stock_for_product(gk=mock_getraenkekasse, code='2222222222222') == 30
    mock_getraenkekasse.repo_kasse.commit.assert_has_calls([
        unittest.mock.call(files=[TEST_PURCHASES_FILE],
                           commit_message='pay for user bbb via getraenkeKasse.py'),
        unittest.mock.call(files=[TEST_PRODUCTS_FILE],
                           commit_message='replenish stock via getraenkeKasse.py')
    ])
    mock_getraenkekasse.repo_kasse.push.assert_called_once_with()
    mock_write_csv.assert_has_calls([
        unittest.mock.call(file=TEST_PURCHASES_FILE,
                           df=mock_getraenkekasse.file_contents.purchases),
        unittest.mock.call(file=TEST_PRODUCTS_FILE,
                           df=mock_getraenkekasse.file_contents.products)
    ])


@freezegun.freeze_time('2019-12-10 17:00:00')
def test_make_purchase_stock_available(mock_getraenkekasse, mock_functions):
    mock_write_csv = mock_functions
    mock_getraenkekasse.repo_kasse.commit.return_value = True
    mock_getraenkekasse.repo_kasse.pull.return_value = True

    expected_df = pd.DataFrame([['2019-12-10T12:20:00', 'aaa', '1111111111111', False],
                                ['2019-12-10T17:00:00', 'aaa', '1111111111111', False]],
                               columns=columns_purchases, index=[0, 3])

    mock_getraenkekasse.make_purchase(user='aaa', code='1111111111111', count=1)

    time.sleep(2)

    pd.testing.assert_frame_equal(get_purchases_for_user(gk=mock_getraenkekasse, user='aaa'), expected_df)
    assert get_stock_for_product(mock_getraenkekasse, '1111111111111') == 19
    mock_getraenkekasse.repo_kasse.commit.assert_called_once_with(files=[TEST_PURCHASES_FILE,
                                                                         TEST_PRODUCTS_FILE],
                                                                  commit_message='purchase via getraenkeKasse.py')
    mock_getraenkekasse.repo_kasse.push.assert_called_once_with()
    mock_write_csv.assert_has_calls([
        unittest.mock.call(file=TEST_PURCHASES_FILE,
                           df=mock_getraenkekasse.file_contents.purchases),
        unittest.mock.call(file=TEST_PRODUCTS_FILE,
                           df=mock_getraenkekasse.file_contents.products)
    ])


@freezegun.freeze_time('2019-12-10 18:00:00')
def test_make_purchase_stock_empty(mock_getraenkekasse, mock_functions):
    mock_write_csv = mock_functions
    mock_getraenkekasse.repo_kasse.commit.return_value = True
    mock_getraenkekasse.repo_kasse.pull.return_value = True

    expected_df = pd.DataFrame([['2019-12-10T12:20:00', 'aaa', '1111111111111', False],
                                ['2019-12-10T18:00:00', 'aaa', '2222222222222', False]],
                               columns=columns_purchases, index=[0, 3])

    mock_getraenkekasse.make_purchase(user='aaa', code='2222222222222', count=1)

    pd.testing.assert_frame_equal(get_purchases_for_user(gk=mock_getraenkekasse, user='aaa'), expected_df)
    assert get_stock_for_product(mock_getraenkekasse, '2222222222222') == 0
    mock_getraenkekasse.repo_kasse.commit.assert_called_once_with(files=[TEST_PURCHASES_FILE],
                                                                  commit_message='purchase via getraenkeKasse.py')
    mock_getraenkekasse.repo_kasse.push.assert_called_once_with()
    mock_write_csv.assert_called_once_with(file=TEST_PURCHASES_FILE,
                                           df=mock_getraenkekasse.file_contents.purchases)
