
"""
Collection of low-level functions used in different apps,
which enables separation of GUI and logic for better testability.
"""

import datetime
import hashlib
import os
import socket
import struct
import time
from typing import Callable, List, Tuple

import git
import pandas as pd


def check_environment_ONLY_PROD(func) -> Callable:
    """
    Decorator function executing the handed function only in PROD environment

    :param func: function (returning a bool)
    :return:
    """
    def wrapper(*args, **kwargs) -> bool:
        if not ('BARCODE_DEV' in os.environ or 'BARCODE_TEST' in os.environ):
            return func(*args, **kwargs)
        return True
    return wrapper


def check_environment_TEST_PROD(func) -> Callable:
    """
    Decorator function executing the handed function only in TEST and PROD environment

    :param func: function (returning a bool)
    :return:
    """
    def wrapper(*args, **kwargs) -> bool:
        if 'BARCODE_DEV' not in os.environ:
            return func(*args, **kwargs)
        return True
    return wrapper


def check_environment_ONLY_DEV(func) -> Callable:
    """
    Decorator function executing the handed function only in DEV environment

    :param func: function (returning a bool)
    :return:
    """
    def wrapper(*args, **kwargs) -> bool:
        if 'BARCODE_DEV' in os.environ:
            return func(*args, **kwargs)
        return True
    return wrapper


def getMD5Hash(filename: str) -> hashlib:
    """
    Get MD5 hash for a file

    :param filename:
    :return:
    """
    hash_obj = hashlib.md5()
    with open(filename, 'rb') as file:
        buf = file.read()
        hash_obj.update(buf)
    return hash_obj


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


@check_environment_ONLY_PROD
def git_pull(path_repo: str) -> bool:
    try:
        repo = git.Repo(path_repo)
        repo.remotes.origin.pull()
        return True
    except git.GitCommandError as exception:
        print(exception)
        if exception.stdout:
            print("!! stdout was:")
            print(exception.stdout)
        if exception.stderr:
            print("!! stderr was:")
            print(exception.stderr)
        return False
    except git.InvalidGitRepositoryError:
        print('Invalid Git Repository')
        return False


@check_environment_ONLY_PROD
def git_push(path_repo: str, files: List[str], commit_message: str) -> bool:
    try:
        repo_local = git.Repo(path_repo)
        for file in files:
            repo_local.git.add(file)
        repo_local.index.commit(commit_message)
        origin = repo_local.remote(name='origin')
        origin.push()
        return True
    except git.GitCommandError as exception:
        print(exception)
        return False


def check_for_file(file) -> None:
    if not os.path.isfile(file):
        raise Exception(f'{file} not found!')


def read_users(users_file: str):
    """"
    Read users from usersFile
    """
    check_for_file(users_file)
    with open(users_file, "r") as file_users:
        for line in file_users:
            yield line.rstrip()


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
