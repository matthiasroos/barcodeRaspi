
import git
import io
import pandas as pd
import pytest
import unittest.mock

import functions


def test_gitPull0():
    with unittest.mock.patch('git.Repo') as mock_git_repo:
        status = functions.gitPull('./.')
    mock_git_repo.assert_called_once_with('./.')
    assert status is True


def test_gitPull1():
    status = functions.gitPull('./.')
    assert status is False


def test_readUsers0():
    with unittest.mock.patch('os.path.isfile', return_value=False) as mocked_os, \
            pytest.raises(Exception) as exc:
        functions.readUsers()
    mocked_os.assert_called_once_with('user.txt')
    assert 'usersFile not found!' in str(exc.value)


def test_readUsers1():
    expected_users_list = ['aaa', 'bbb', 'ccc']
    with unittest.mock.patch('os.path.isfile', return_value=True) as mocked_os,\
            unittest.mock.patch('builtins.open', unittest.mock.mock_open(read_data='aaa\nbbb\nccc')) as mocked_open:
        users_list = functions.readUsers()
    mocked_os.assert_called_once_with('user.txt')
    mocked_open.assert_called_once_with('user.txt', 'r')
    assert users_list == expected_users_list


def test_readProducts0():
    with unittest.mock.patch('os.path.isfile', return_value=False) as mocked_os, \
            pytest.raises(Exception) as exc:
        functions.readProducts()
    mocked_os.assert_called_once_with('produkt.txt')
    assert 'productsFile not found!' in str(exc.value)


def test_readProducts1():
    file_content = """1,1111111111111,xxxx,0.60\n2,2222222222222,yyyy,0.80"""
    expected_df = pd.DataFrame([['1', '1111111111111', 'xxxx', 0.60, 'N/A'],
                                ['2', '2222222222222', 'yyyy', 0.80, 'N/A']],
                               columns=['nr', 'code', 'desc', 'price', 'alcohol'])
    with unittest.mock.patch('os.path.isfile', return_value=True) as mocked_os,\
            unittest.mock.patch('builtins.open', unittest.mock.mock_open(read_data=file_content)) as mocked_open:
        prod_df = functions.readProducts()
    mocked_os.assert_called_once_with('produkt.txt')
    mocked_open.assert_called_once_with('produkt.txt', 'r')
    assert prod_df.equals(expected_df)


@pytest.mark.parametrize(['input_df', 'expected_set'],
                         [(pd.DataFrame([1, 22, '', 4444], columns=['code']), {1, 2, 4}),
                          (pd.DataFrame(['1', '22', '', '4444'], columns=['code']), {1, 2, 4})])
def test_calcLengthCode(input_df, expected_set):
    output_set = functions.calcLengthCode(input_df)
    assert output_set == expected_set


def test_getPurchases0():
    with unittest.mock.patch('os.path.isfile', return_value=False) as mocked_os, \
            pytest.raises(Exception) as exc:
        functions.getPurchases()
    mocked_os.assert_called_once_with('purchase.txt')
    assert 'purchasesFile not found!' in str(exc.value)


def test_getPurchases1():
    df_from_file = pd.read_csv(io.StringIO(''), header=None)
    products_df = pd.DataFrame([[1, '111111111111', 'xxxx', 0.60, None],
                                [2, '222222222222', 'yyyy', 1.20, None]],
                               columns=['nr', 'code', 'desc', 'price', 'alcohol'])
    expected_df = pd.DataFrame([], columns=['timestamp', 'user', 'code', 'nr', 'desc', 'price', 'alcohol'])
    with unittest.mock.patch('os.path.isfile', return_value=False) as mocked_os, \
            unittest.mock.patch('pandas.read_csv') as mocked_readcsv, \
            unittest.mock.patch('functions.readProducts') as mocked_readProducts, \
            pytest.raises(Exception) as exc:
        mocked_readcsv.return_value = df_from_file
        mocked_readProducts.return_value = products_df
        usersPurchases_df = functions.getPurchases()
    mocked_os.assert_called_once_with('purchase.txt')
    assert usersPurchases_df.equals(expected_df)


def test_getPurchases2():
    file_content = """2019-12-10T12:20:00,aaa,111111111111\n2019-12-10T16:30:00,bbb,222222222222\n
2019-12-10T16:35:00,bbb,222222222222"""
    df_from_file = pd.read_csv(io.StringIO(file_content), header=None)
    products_df = pd.DataFrame([[1, '111111111111', 'xxxx', 0.60, None],
                                [2, '222222222222', 'yyyy', 1.20, None]],
                               columns=['nr', 'code', 'desc', 'price', 'alcohol'])
    expected_df = pd.DataFrame([['2019-12-10T12:20:00', 'aaa', '111111111111', 1, 'xxxx', 0.60, None],
                                ['2019-12-10T16:30:00', 'bbb', '222222222222', 2, 'yyyy', 1.20, None],
                                ['2019-12-10T16:35:00', 'bbb', '222222222222', 2, 'yyyy', 1.20, None]],
                               columns=['timestamp', 'user', 'code', 'nr', 'desc', 'price', 'alcohol'])
    with unittest.mock.patch('os.path.isfile') as mocked_os, \
        unittest.mock.patch('pandas.read_csv') as mocked_readcsv, \
            unittest.mock.patch('functions.readProducts') as mocked_readProducts:
        mocked_os.return_value = True
        mocked_readcsv.return_value = df_from_file
        mocked_readProducts.return_value = products_df
        usersPurchases_df = functions.getPurchases()
    mocked_os.assert_called_once_with('purchase.txt')
    assert usersPurchases_df.equals(expected_df)


def test_getUserPurchases():
    users_purchases_df = pd.DataFrame([['2020-01-24T17:13:35', 'aaa', '1111111111111', 1.0],
                                      ['2020-01-24T17:13:36', 'aaa', '2222222222222', 1.5],
                                      ['2020-01-24T17:13:36', 'bbb', '1111111111111', 1.2]],
                                      columns=['timestamp', 'user', 'code', 'price'])
    nr, money = functions.getUserPurchases(users_purchases_df, 'aaa')
    assert nr == 2
    assert money == 2.5


def test_summarizeUserPurchases():
    input_df = pd.DataFrame([['2019-12-10T12:20:00', 'aaa', '111111111111', 1, 'xxxx', 0.60, None],
                             ['2019-12-10T16:30:00', 'bbb', '222222222222', 2, 'yyyy', 1.20, None],
                             ['2019-12-10T16:35:00', 'bbb', '222222222222', 2, 'yyyy', 1.20, None],
                             ['2019-12-10T16:40:00', 'aaa', '222222222222', 2, 'yyyy', 1.20, None],
                             ['2019-12-10T16:45:00', 'aaa', '333333333333', 3, 'yzzz', 1.50, None]],
                            columns=['timestamp', 'user', 'code', 'nr', 'desc', 'price', 'alcohol'])
    expected_df = pd.DataFrame([['aaa', 3, 3.30], ['bbb', 2, 2.40]], columns=['name', 'drinks', 'money'])
    with unittest.mock.patch('functions.getPurchases') as mocked_purchases:
        mocked_purchases.return_value = input_df
        output_df = functions.summarizeUserPurchases()
    assert output_df.equals(expected_df)
