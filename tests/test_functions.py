
import io
import unittest.mock
import freezegun
import pandas as pd
import pytest

import functions


def test_git_pull0():
    with unittest.mock.patch('git.Repo') as mock_git_repo:
        status = functions.git_pull('./.')
    mock_git_repo.assert_called_once_with('./.')
    assert status is True


def test_git_pull1():
    status = functions.git_pull('./.')
    assert status is False


def test_read_users0_file_not_found():
    with unittest.mock.patch('os.path.isfile', return_value=False) as mocked_os, \
            pytest.raises(Exception) as exc:
        functions.read_users()
    mocked_os.assert_called_once_with('user.txt')
    assert 'USERS_FILE not found!' in str(exc.value)


def test_read_users1():
    expected_users_list = ['aaa', 'bbb', 'ccc']
    with unittest.mock.patch('os.path.isfile', return_value=True) as mocked_os,\
            unittest.mock.patch('builtins.open', unittest.mock.mock_open(read_data='aaa\nbbb\nccc')) as mocked_open:
        users_list = functions.read_users()
    mocked_os.assert_called_once_with('user.txt')
    mocked_open.assert_called_once_with('user.txt', 'r')
    assert users_list == expected_users_list


def test_read_products0_file_not_found():
    with unittest.mock.patch('os.path.isfile', return_value=False) as mocked_os, \
            pytest.raises(Exception) as exc:
        functions.read_products()
    mocked_os.assert_called_once_with('produkt.txt')
    assert 'PRODUCTS_FILE not found!' in str(exc.value)


def test_read_products1():
    file_content = """1,1111111111111,xxxx,0.60\n2,2222222222222,yyyy,0.80"""
    expected_df = pd.DataFrame([['1', '1111111111111', 'xxxx', 0.60, 'N/A'],
                                ['2', '2222222222222', 'yyyy', 0.80, 'N/A']],
                               columns=['nr', 'code', 'desc', 'price', 'alcohol'])
    with unittest.mock.patch('os.path.isfile', return_value=True) as mocked_os,\
            unittest.mock.patch('builtins.open', unittest.mock.mock_open(read_data=file_content)) as mocked_open:
        prod_df = functions.read_products()
    mocked_os.assert_called_once_with('produkt.txt')
    mocked_open.assert_called_once_with('produkt.txt', 'r')
    assert prod_df.equals(expected_df)


@pytest.mark.parametrize(['input_df', 'expected_set'],
                         [(pd.DataFrame([1, 22, '', 4444], columns=['code']), {1, 2, 4}),
                          (pd.DataFrame(['1', '22', '', '4444'], columns=['code']), {1, 2, 4})])
def test_calc_length_code(input_df, expected_set):
    output_set = functions.calc_length_code(input_df)
    assert output_set == expected_set


def test_read_purchases0_file_not_found():
    with unittest.mock.patch('os.path.isfile', return_value=False) as mocked_os, \
            pytest.raises(Exception) as exc:
        functions.read_purchases()
    mocked_os.assert_called_once_with('purchase.txt')
    assert 'PURCHASES_FILE not found!' in str(exc.value)


def test_read_purchases1_empty_file():
    # TO DO: write unit test if file is empty
    pass


def test_read_purchases2():
    file_content = """2019-12-10T12:20:00,aaa,111111111111\n2019-12-10T16:30:00,bbb,222222222222\n
2019-12-10T16:35:00,bbb,222222222222"""
    df_from_file = pd.read_csv(io.StringIO(file_content), header=None)
    expected_df = pd.DataFrame([['2019-12-10T12:20:00', 'aaa', '111111111111'],
                                ['2019-12-10T16:30:00', 'bbb', '222222222222'],
                                ['2019-12-10T16:35:00', 'bbb', '222222222222']],
                               columns=['timestamp', 'user', 'code'])
    with unittest.mock.patch('os.path.isfile', return_value=True) as mocked_os, \
            unittest.mock.patch('pandas.read_csv', return_value=df_from_file):
        purchases_df = functions.read_purchases()
    mocked_os.assert_called_once_with('purchase.txt')
    assert purchases_df.equals(expected_df)


def test_merge_purchases_products():
    purchases_df = pd.DataFrame([['2019-12-10T12:20:00', 'aaa', '111111111111'],
                                 ['2019-12-10T16:30:00', 'bbb', '222222222222'],
                                 ['2019-12-10T16:35:00', 'bbb', '222222222222']],
                                columns=['timestamp', 'user', 'code'])
    products_df = pd.DataFrame([[1, '111111111111', 'xxxx', 0.60, None],
                                [2, '222222222222', 'yyyy', 1.20, None]],
                               columns=['nr', 'code', 'desc', 'price', 'alcohol'])
    expected_df = pd.DataFrame([['2019-12-10T12:20:00', 'aaa', '111111111111', 1, 'xxxx', 0.60, None],
                                ['2019-12-10T16:30:00', 'bbb', '222222222222', 2, 'yyyy', 1.20, None],
                                ['2019-12-10T16:35:00', 'bbb', '222222222222', 2, 'yyyy', 1.20, None]],
                               columns=['timestamp', 'user', 'code', 'nr', 'desc', 'price', 'alcohol'])
    users_purchases_df = functions.merge_purchases_products(purchases=purchases_df, products=products_df)
    assert users_purchases_df.equals(expected_df)


def test_summarize_user_purchases_standalone():
    input_df = pd.DataFrame([['2019-12-10T12:20:00', 'aaa', '111111111111', 1, 'xxxx', 0.60, None],
                             ['2019-12-10T16:30:00', 'bbb', '222222222222', 2, 'yyyy', 1.20, None],
                             ['2019-12-10T16:35:00', 'bbb', '222222222222', 2, 'yyyy', 1.20, None],
                             ['2019-12-10T16:40:00', 'aaa', '222222222222', 2, 'yyyy', 1.20, None],
                             ['2019-12-10T16:45:00', 'aaa', '333333333333', 3, 'yzzz', 1.50, None]],
                            columns=['timestamp', 'user', 'code', 'nr', 'desc', 'price', 'alcohol'])
    expected_df = pd.DataFrame([['aaa', 3, 3.30], ['bbb', 2, 2.40]], columns=['name', 'drinks', 'money'])
    with unittest.mock.patch('functions.merge_purchases_products') as mocked_purchases:
        mocked_purchases.return_value = input_df
        output_df = functions.summarize_user_purchases(purchases=None, products=None)
    assert output_df.equals(expected_df)


def test_summarize_user_purchases_integration():
    purchases_df = pd.DataFrame([['2019-12-10T12:20:00', 'aaa', '111111111111'],
                                 ['2019-12-10T16:30:00', 'bbb', '222222222222'],
                                 ['2019-12-10T16:35:00', 'bbb', '222222222222'],
                                 ['2019-12-10T16:40:00', 'aaa', '222222222222'],
                                 ['2019-12-10T16:45:00', 'aaa', '333333333333']],
                                columns=['timestamp', 'user', 'code'])
    products_df = pd.DataFrame([[1, '111111111111', 'xxxx', 0.60, None],
                                [2, '222222222222', 'yyyy', 1.20, None],
                                [3, '333333333333', 'yzzz', 1.50, None]],
                               columns=['nr', 'code', 'desc', 'price', 'alcohol'])
    expected_df = pd.DataFrame([['aaa', 3, 3.30], ['bbb', 2, 2.40]], columns=['name', 'drinks', 'money'])
    output_df = functions.summarize_user_purchases(purchases=purchases_df, products=products_df)
    assert output_df.equals(expected_df)


def test_save_purchase0_file_not_found():
    with unittest.mock.patch('os.path.isfile', return_value=False) as mocked_os, \
            pytest.raises(Exception) as exc:
        functions.save_purchase(user='test', code='1111111111111')
    mocked_os.assert_called_once_with('purchase.txt')
    assert 'PURCHASES_FILE not found!' in str(exc.value)


@freezegun.freeze_time('2020-02-29 12:00:00')
def test_save_purchase1():
    with unittest.mock.patch('os.path.isfile', return_value=True), \
            unittest.mock.patch('builtins.open', unittest.mock.mock_open(), create=True) as mocked_open:
        functions.save_purchase(user='test', code='1111111111111')
    mocked_open.assert_called_once_with(functions.PURCHASES_FILE, 'a')
    mocked_open.return_value.writelines.assert_called_once_with('2020-02-29T12:00:00,test,1111111111111\n')


def test_transform_purchases():
    input_df = pd.DataFrame([['2019-12-10T12:20:00', 'aaa', '111111111111'],
                             ['2019-12-10T16:30:00', 'bbb', '222222222222'],
                             ['2019-12-10T16:35:00', 'bbb', '222222222222']],
                            columns=['timestamp', 'user', 'code'])
    with unittest.mock.patch('functions.read_purchases', return_value=input_df), \
            unittest.mock.patch('builtins.open', unittest.mock.mock_open(), create=True) as mocked_open:
        functions.transform_purchases()
        mocked_open.assert_called_once_with('purchase_new.txt', 'w+')
        mocked_open.mock_calls = [unittest.mock.call.writelines('2019-12-10T12:20:00,aaa,111111111111,False\n'),
                                  unittest.mock.call.writelines('2019-12-10T16:30:00,bbb,222222222222,False\n'),
                                  unittest.mock.call.writelines('2019-12-10T16:35:00,bbb,222222222222,False\n')]
