
"""
Collection of low-level functions used in different apps,
which enables separation of GUI and logic for better testability.
"""

import cProfile
import datetime
import functools
import logging
import os
import pstats
import socket
import struct
import time
from typing import Callable, Iterable, List, Optional, Tuple

import pandas as pd

logger = logging.getLogger()


def check_environment_ONLY_PROD(func) -> Callable:
    """
    Decorator function executing the handed function only in PROD environment

    :param func: function (returning a bool)
    :return:
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> bool:
        if not ('BARCODE_DEV' in os.environ or 'BARCODE_TEST' in os.environ):

            result = func(*args, **kwargs)

            return result
        logger.info('DEV or TEST: function %s not executed', func.__name__)
        return True
    return wrapper


def check_environment_TEST_PROD(func) -> Callable:
    """
    Decorator function executing the handed function only in TEST and PROD environment

    :param func: function (returning a bool)
    :return:
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> bool:
        if 'BARCODE_DEV' not in os.environ:

            result = func(*args, **kwargs)

            return result
        logger.info('DEV: function %s not executed', func.__name__)
        return True
    return wrapper


def check_environment_DEV_TEST(func) -> Callable:
    """


    :param func:
    :return:
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> bool:
        if ('BARCODE_DEV' in os.environ) or ('BARCODE_TEST' in os.environ):

            result = func(*args, **kwargs)

            return result
        return True

    return wrapper


def check_environment_ONLY_DEV(func) -> Callable:
    """
    Decorator function executing the handed function only in DEV environment

    :param func: function (returning a bool)
    :return:
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> bool:
        if 'BARCODE_DEV' in os.environ:

            result = func(*args, **kwargs)

            return result
        logger.info('TEST: function %s not executed', func.__name__)
        return True
    return wrapper


def runtime_profile(active: bool = False) -> Callable:
    """

    :param active: flag if decorator is active
    :return:
    """
    def decorator(func) -> Callable:
        """

        :param func: decorated function
        :return:
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if active is False:
                return func(*args, **kwargs)

            profile_ = cProfile.Profile()
            profile_.enable()
            result = func(*args, **kwargs)
            profile_.disable()

            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            output_file = f'{func.__name__}.profile-{timestamp}'
            with open(output_file, 'w') as file_handle:
                ps = pstats.Stats(profile_, stream=file_handle)
                ps.strip_dirs()
                ps.sort_stats(pstats.SortKey.CUMULATIVE)
                ps.print_stats()
            return result

        return wrapper
    return decorator


@check_environment_TEST_PROD
def checkNetwork(host="8.8.8.8", port=53, timeout=3) -> bool:
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(ex)
        return False


def getTimefromNTP():
    addrNTP = '0.de.pool.ntp.org'
    REFERENCE_TIME_1970 = 2208988800  # Reference time
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = b'\x1b' + 47 * b'\0'
    client.sendto(data, (addrNTP, 123))
    data, address = client.recvfrom(1024)
    t = 0
    if data:
        t = struct.unpack('!12I', data)[10]
        t -= REFERENCE_TIME_1970
    return time.ctime(t), t


def check_for_file(file, raise_exec=True) -> Optional[bool]:
    """
    Check if the file exists.

    Return True if it exists, False if not.
    An exception is raised in the latter case, if raise_exec is True.

    :param file: name of the file
    :param raise_exec: flag if
    :return:
    """
    if not os.path.isfile(file):
        if raise_exec is True:
            raise Exception(f'{file} not found!')
        return False
    return True


def read_users(users_file: str) -> List[str]:
    """"
    Read users from file.

    :param users_file: file containing user names
    :return: list containing the users
    """
    check_for_file(users_file)
    users_list = []
    with open(users_file, "r") as file_users:
        for line in file_users:
            users_list.append(line.rstrip())
    return users_list


def format_dataframe(data_df: pd.DataFrame, types: dict) -> pd.DataFrame:
    for key, value in types.items():
        data_df[key] = data_df[key].astype(value)
    return data_df


def read_csv_file(file: str, columns: List[str], column_types: dict) -> pd.DataFrame:
    check_for_file(file)
    try:
        data_df = pd.read_csv(file, header=None)
        data_df.columns = columns
        data_df = format_dataframe(data_df=data_df, types=column_types)
    except pd.errors.EmptyDataError:
        data_df = pd.DataFrame([], columns=columns)
    return data_df


def calc_length_code(products_df: pd.DataFrame) -> set:
    """
    Create set containing the length of the product codes
    """
    return {len(row['code']) for _, row in products_df.iterrows() if len(row['code']) > 0}


def check_column_nr_in_file(file) -> int:
    check_for_file(file)
    df = pd.read_csv(file, header=None)
    nr = len(df.columns)
    return nr


def merge_purchases_products(purchases: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    usersPurchases_df = purchases.merge(products, on='code', how='left', sort=False)
    return usersPurchases_df


def summarize_user_purchases(purchases: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    usersPurchases_df = merge_purchases_products(purchases=purchases, products=products)
    filtered_usersPurchases_df = usersPurchases_df[~usersPurchases_df['paid']]
    summary_purchases_df = filtered_usersPurchases_df.groupby('user').agg({'code': 'count', 'price': 'sum'})
    summary_purchases_df.reset_index(inplace=True)
    summary_purchases_df.columns = ['name', 'drinks', 'money']
    return summary_purchases_df


def add_purchase(purchases: pd.DataFrame, user: str, code: str) -> pd.DataFrame:
    new_purchase = pd.DataFrame([[datetime.datetime.now().isoformat(), user, code, False]],
                                columns=['timestamp', 'user', 'code', 'paid'])
    purchases = purchases.append(new_purchase, ignore_index=True)
    return purchases


def write_csv_file(file, df: pd.DataFrame) -> None:
    check_for_file(file)
    df.to_csv(file, header=False, index=False)


def transform_purchases(purchases_file: str) -> None:
    check_for_file(purchases_file)
    try:
        purchases_df = pd.read_csv(purchases_file, header=None)
        purchases_df.columns = ['timestamp', 'user', 'code']
        purchases_df['code'] = purchases_df['code'].astype(str)
        purchases_df['paid'] = False
        purchases_df['paid'] = purchases_df['paid'].astype(str)
        with open(purchases_file, 'w+') as filePurchases_new:
            for _, row in purchases_df.iterrows():
                line = f"{row['timestamp']},{row['user']},{row['code']},{row['paid']}\n"
                filePurchases_new.writelines(line)
    except pd.errors.EmptyDataError:
        pass


def retransform_purchases(purchases_file: str) -> None:
    check_for_file(purchases_file)
    try:
        purchases_df = pd.read_csv(purchases_file, header=None)
        purchases_df.columns = ['timestamp', 'user', 'code', 'paid']
        purchases_df['code'] = purchases_df['code'].astype(str)
        purchases_df['paid'] = purchases_df['paid'].astype(bool)
        with open('purchase_old.txt', 'w+') as filePurchases_old:
            for _, row in purchases_df.iterrows():
                line = f"{row['timestamp']},{row['user']},{row['code']}\n"
                filePurchases_old.writelines(line)
    except pd.errors.EmptyDataError:
        pass


def transform_products(products_file: str) -> None:
    check_for_file(products_file)
    try:
        products_df = pd.read_csv(products_file, header=None)
        products_df.columns = ['nr', 'code', 'desc', 'price']
        with open(products_file, 'w+') as filePurchases_new:
            for _, row in products_df.iterrows():
                line = f"{row['nr']},{row['code']},{row['desc']},{row['price']},0\n"
                filePurchases_new.writelines(line)
    except pd.errors.EmptyDataError:
        pass
