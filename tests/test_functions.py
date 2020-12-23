
import io
import unittest.mock

import freezegun
import numpy as np
import pandas as pd
import pytest

import functions


def test_read_users0_file_not_found():
    with unittest.mock.patch('os.path.isfile', return_value=False) as mocked_os:
        with pytest.raises(Exception) as exc:
            users = functions.read_users(users_file='test_file')
            next(users)
    mocked_os.assert_called_once_with('test_file')
    assert 'test_file not found!' in str(exc.value)


def test_read_users1():
    expected_users_list = ['aaa', 'bbb', 'ccc']
    with unittest.mock.patch('os.path.isfile', return_value=True) as mocked_os:
        with unittest.mock.patch('builtins.open', unittest.mock.mock_open(read_data='aaa\nbbb\nccc')) as mocked_open:
            gen_users_list = functions.read_users(users_file='test_file')
            users_list = [user for user in gen_users_list]
    mocked_os.assert_called_once_with('test_file')
    mocked_open.assert_called_once_with('test_file', 'r')
    assert users_list == expected_users_list


def test_format_dataframe():
    file_content = """1,1111111111111,xxxx,0.60,20"""
    data_df = pd.read_csv(io.StringIO(file_content), header=None)
    data_df.columns = ['nr', 'code', 'desc', 'price', 'stock']
    types = {'nr': int, 'code': str, 'desc': str, 'price': float, 'stock': int}

    data_df = functions.format_dataframe(data_df=data_df, types=types)

    assert data_df['nr'].dtype == np.int64
    assert data_df['code'].dtype == np.object
    assert data_df['price'].dtype == np.float64


def test_read_csv_file0_file_not_found():
    with unittest.mock.patch('os.path.isfile', return_value=False) as mocked_os:
        with pytest.raises(Exception) as exc:
            functions.read_csv_file(file='test_file', columns=[],
                                    column_types={})
    mocked_os.assert_called_once_with('test_file')
    assert 'test_file not found!' in str(exc.value)


def test_read_csv_file1():
    file_content = """1,1111111111111,xxxx,0.60,20\n2,2222222222222,yyyy,0.80,10"""
    df_from_file = pd.read_csv(io.StringIO(file_content), header=None)
    columns = ['nr', 'code', 'desc', 'price', 'stock']
    expected_df = pd.DataFrame([[1, '1111111111111', 'xxxx', 0.60, 20],
                                [2, '2222222222222', 'yyyy', 0.80, 10]],
                               columns=columns)
    with unittest.mock.patch('os.path.isfile', return_value=True) as mocked_os:
        with unittest.mock.patch('pandas.read_csv', return_value=df_from_file):
            prod_df = functions.read_csv_file(file='test_file',
                                              columns=columns,
                                              column_types={'code': str, 'price': float})
    mocked_os.assert_called_once_with('test_file')
    pd.testing.assert_frame_equal(prod_df, expected_df)


def test_csv_file2_empty_file():
    # TODO: write unit test if file is empty
    pass


@pytest.mark.parametrize(['input_df', 'expected_set'],
                         [(pd.DataFrame(['1', '22', '', '4444'], columns=['code']), {1, 2, 4}),
                          (pd.DataFrame(['1', '22', '', '4444', '0000'], columns=['code']), {1, 2, 4})])
def test_calc_length_code(input_df, expected_set):
    output_set = functions.calc_length_code(input_df)
    assert output_set == expected_set


def test_merge_purchases_products():
    purchases_df = pd.DataFrame([['2019-12-10T12:20:00', 'aaa', '111111111111', False],
                                 ['2019-12-10T16:30:00', 'bbb', '222222222222', False],
                                 ['2019-12-10T16:35:00', 'bbb', '222222222222', False]],
                                columns=['timestamp', 'user', 'code', 'paid'])
    products_df = pd.DataFrame([[1, '111111111111', 'xxxx', 0.60, None],
                                [2, '222222222222', 'yyyy', 1.20, None]],
                               columns=['nr', 'code', 'desc', 'price', 'alcohol'])
    expected_df = pd.DataFrame([['2019-12-10T12:20:00', 'aaa', '111111111111', False, 1, 'xxxx', 0.60, None],
                                ['2019-12-10T16:30:00', 'bbb', '222222222222', False, 2, 'yyyy', 1.20, None],
                                ['2019-12-10T16:35:00', 'bbb', '222222222222', False, 2, 'yyyy', 1.20, None]],
                               columns=['timestamp', 'user', 'code', 'paid', 'nr', 'desc', 'price', 'alcohol'])
    users_purchases_df = functions.merge_purchases_products(purchases=purchases_df, products=products_df)
    pd.testing.assert_frame_equal(users_purchases_df, expected_df)


def test_summarize_user_purchases_standalone():
    input_df = pd.DataFrame([['2019-12-10T12:20:00', 'aaa', '111111111111', True, 1, 'xxxx', 0.60, None],
                             ['2019-12-10T16:30:00', 'bbb', '222222222222', False, 2, 'yyyy', 1.20, None],
                             ['2019-12-10T16:35:00', 'bbb', '222222222222', False, 2, 'yyyy', 1.20, None],
                             ['2019-12-10T16:40:00', 'aaa', '222222222222', False, 2, 'yyyy', 1.20, None],
                             ['2019-12-10T16:45:00', 'aaa', '333333333333', False, 3, 'yzzz', 1.50, None]],
                            columns=['timestamp', 'user', 'code', 'paid', 'nr', 'desc', 'price', 'alcohol'])
    expected_df = pd.DataFrame([['aaa', 2, 2.70], ['bbb', 2, 2.40]], columns=['name', 'drinks', 'money'])
    with unittest.mock.patch('functions.merge_purchases_products') as mocked_purchases:
        mocked_purchases.return_value = input_df
        output_df = functions.summarize_user_purchases(purchases=pd.DataFrame(), products=pd.DataFrame())
    pd.testing.assert_frame_equal(output_df, expected_df)


def test_summarize_user_purchases_integration():
    purchases_df = pd.DataFrame([['2019-12-10T12:20:00', 'aaa', '111111111111', False],
                                 ['2019-12-10T16:30:00', 'bbb', '222222222222', True],
                                 ['2019-12-10T16:35:00', 'bbb', '222222222222', False],
                                 ['2019-12-10T16:40:00', 'aaa', '222222222222', False],
                                 ['2019-12-10T16:45:00', 'aaa', '333333333333', False]],
                                columns=['timestamp', 'user', 'code', 'paid'])
    products_df = pd.DataFrame([[1, '111111111111', 'xxxx', 0.60, None],
                                [2, '222222222222', 'yyyy', 1.20, None],
                                [3, '333333333333', 'yzzz', 1.50, None]],
                               columns=['nr', 'code', 'desc', 'price', 'alcohol'])
    expected_df = pd.DataFrame([['aaa', 3, 3.30], ['bbb', 1, 1.20]], columns=['name', 'drinks', 'money'])
    output_df = functions.summarize_user_purchases(purchases=purchases_df, products=products_df)
    pd.testing.assert_frame_equal(output_df, expected_df)


@freezegun.freeze_time('2020-02-29 16:00:00')
def test_add_purchase():
    columns = ['timestamp', 'user', 'code', 'paid']
    input_df = pd.DataFrame([['2019-12-10T12:20:00', 'aaa', '111111111111', False]], columns=columns)
    expected_df = pd.DataFrame([['2019-12-10T12:20:00', 'aaa', '111111111111', False],
                                ['2020-02-29T16:00:00', 'bbb', '222222222222', False]],
                               columns=columns)
    output_df = functions.add_purchase(purchases=input_df, user='bbb', code='222222222222')
    pd.testing.assert_frame_equal(output_df, expected_df)


def test_transform_purchases():
    input_df = pd.DataFrame([['2019-12-10T12:20:00', 'aaa', '111111111111'],
                             ['2019-12-10T16:30:00', 'bbb', '222222222222'],
                             ['2019-12-10T16:35:00', 'bbb', '222222222222']],
                            columns=['timestamp', 'user', 'code'])
    with unittest.mock.patch('os.path.isfile', return_value=True), \
         unittest.mock.patch('pandas.read_csv', return_value=input_df), \
         unittest.mock.patch('builtins.open', unittest.mock.mock_open(), create=True) as mocked_open:
        functions.transform_purchases(purchases_file='test_file')
        mocked_open.assert_called_once_with('test_file', 'w+')
        expected_calls = [unittest.mock.call().writelines('2019-12-10T12:20:00,aaa,111111111111,False\n'),
                          unittest.mock.call().writelines('2019-12-10T16:30:00,bbb,222222222222,False\n'),
                          unittest.mock.call().writelines('2019-12-10T16:35:00,bbb,222222222222,False\n')]
        mocked_open.assert_has_calls(expected_calls, any_order=False)


def test_retransform_purchases():
    file_content = """2019-12-10T12:20:00,aaa,111111111111,False\n2019-12-10T16:30:00,bbb,222222222222,False\n
2019-12-10T16:35:00,bbb,222222222222,False"""
    df_from_file = pd.read_csv(io.StringIO(file_content), header=None)
    with unittest.mock.patch('os.path.isfile', return_value=True), \
         unittest.mock.patch('pandas.read_csv', return_value=df_from_file), \
         unittest.mock.patch('builtins.open', unittest.mock.mock_open(), create=True) as mocked_open:
        functions.retransform_purchases(purchases_file='test_file')
        mocked_open.assert_called_once_with('purchase_old.txt', 'w+')
        expected_calls = [unittest.mock.call().writelines('2019-12-10T12:20:00,aaa,111111111111\n'),
                          unittest.mock.call().writelines('2019-12-10T16:30:00,bbb,222222222222\n'),
                          unittest.mock.call().writelines('2019-12-10T16:35:00,bbb,222222222222\n')]
        mocked_open.assert_has_calls(expected_calls, any_order=False)


def test_transform_products():
    input_df = pd.DataFrame([[1, '1111111111111', 'xxxx', 0.60],
                             [2, '2222222222222', 'yyyy', 0.80],
                             [3, '3333333333333', 'zzzz', 0.95]],
                            columns=['nr', 'code', 'desc', 'price'])
    with unittest.mock.patch('os.path.isfile', return_value=True), \
         unittest.mock.patch('pandas.read_csv', return_value=input_df), \
         unittest.mock.patch('builtins.open', unittest.mock.mock_open(), create=True) as mocked_open:
        functions.transform_products(products_file='test_file')
        mocked_open.assert_called_once_with('test_file', 'w+')
        expected_calls = [unittest.mock.call().writelines('1,1111111111111,xxxx,0.6,0\n'),
                          unittest.mock.call().writelines('2,2222222222222,yyyy,0.8,0\n'),
                          unittest.mock.call().writelines('3,3333333333333,zzzz,0.95,0\n')]
        mocked_open.assert_has_calls(expected_calls, any_order=False)
