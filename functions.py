
import datetime
import hashlib
import os
import socket
import struct
import time
import typing

import git
import numpy as np
import pandas as pd

USERS_FILE = "user.txt"
PRODUCTS_FILE = "produkt.txt"
PURCHASES_FILE = "purchase.txt"


def check_environment_ONLY_PROD(func):
    def wrapper(*args, **kwargs):
        if not ('BARCODE_DEV' in os.environ or 'BARCODE_TEST' in os.environ):
            return func(*args, **kwargs)
        else:
            return True
    return wrapper


def check_environment_TEST_PROD(func):
    def wrapper(*args, **kwargs):
        if 'BARCODE_DEV' not in os.environ:
            return func(*args, **kwargs)
        else:
            return True
    return wrapper


def getMD5Hash(filename: str):
    hasher = hashlib.md5()
    with open(filename, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
    return hasher


@check_environment_TEST_PROD
def checkNetwork(host="8.8.8.8", port=53, timeout=3):
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
    except git.InvalidGitRepositoryError as exception:
        print('Invalid Git Repository')
        return False


@check_environment_ONLY_PROD
def git_push(path_repo: str, commit_message: str = 'purchase via getraenkeKasse.py') -> bool:
    try:
        repo_local = git.Repo(path_repo)
        repo_local.git.add(PURCHASES_FILE)
        repo_local.git.add(PRODUCTS_FILE)
        repo_local.index.commit(commit_message)
        origin = repo_local.remote(name='origin')
        origin.push()
        return True
    except git.GitCommandError as exception:
        print(exception)
        return False


def check_for_file(file):
    if not os.path.isfile(file):
        raise Exception(f'{file} not found!')


def read_users() -> list:
    """"
    Read users from usersFile
    """
    check_for_file(USERS_FILE)
    file_users = open(USERS_FILE, "r")
    users = []
    for line in file_users:
        users.append(line.rstrip())
    file_users.close()
    return users


def read_products() -> pd.DataFrame:
    """"
    Read products from productsFile
    """
    check_for_file(PRODUCTS_FILE)
    products_df = pd.read_csv(PRODUCTS_FILE, header=None)
    products_df.columns = ['nr', 'code', 'desc', 'price', 'stock']
    products_df['code'] = products_df['code'].astype(str)
    products_df['price'] = products_df['price'].astype(float)
    return products_df


def calc_length_code(products_df: pd.DataFrame) -> set:
    """"""
    length = set()
    for index, row in products_df.iterrows():
        tmpLen = len(str(row['code']))
        if tmpLen > 0:
            length.add(tmpLen)
    return length


def check_column_nr_in_file(file):
    check_for_file(file)
    df = pd.read_csv(file, header=None)
    nr = len(df.columns)
    return nr


def read_purchases() -> pd.DataFrame:
    check_for_file(PURCHASES_FILE)
    try:
        purchases_df = pd.read_csv(PURCHASES_FILE, header=None)
        purchases_df.columns = ['timestamp', 'user', 'code', 'paid']
        purchases_df['code'] = purchases_df['code'].astype(str)
        purchases_df['paid'] = purchases_df['paid'].astype(bool)
    except pd.errors.EmptyDataError:
        purchases_df = pd.DataFrame([], columns=['timestamp', 'user', 'code', 'paid'])
    return purchases_df


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


def add_purchase(purchases: pd.DataFrame, user: str, code: str):
    new_purchase = pd.DataFrame([[datetime.datetime.now().isoformat(), user, code, False]],
                                columns=['timestamp', 'user', 'code', 'paid'])
    purchases = purchases.append(new_purchase, ignore_index=True)
    return purchases


def write_csv_file(file, df: pd.DataFrame):
    check_for_file(file)
    df.to_csv(file, header=False, index=False)


def transform_purchases():
    check_for_file(PURCHASES_FILE)
    try:
        purchases_df = pd.read_csv(PURCHASES_FILE, header=None)
        purchases_df.columns = ['timestamp', 'user', 'code']
        purchases_df['paid'] = False
        purchases_df['paid'] = purchases_df['paid'].astype(str)
        filePurchases_new = open(PURCHASES_FILE, 'w+')
        for _, row in purchases_df.iterrows():
            line = f"{row['timestamp']},{row['user']},{row['code']},{row['paid']}\n"
            filePurchases_new.writelines(line)
        filePurchases_new.close()
    except pd.errors.EmptyDataError:
        pass


# TO DO: rewrite function
def retransform_purchases():
    purchases_df = pd.DataFrame([], columns=['timestamp', 'user', 'code', 'paid'])
    if not os.path.isfile('purchase_new.txt'):
        raise Exception("purchases_new.txt not found!")
    try:
        purchases_df = pd.read_csv('purchase_new.txt', header=None)
        purchases_df.columns = ['timestamp', 'user', 'code', 'paid']
        purchases_df['code'] = purchases_df['code'].astype(str)
        purchases_df['paid'] = purchases_df['paid'].astype(bool)
    except pd.errors.EmptyDataError:
        pass
    filePurchases_old = open('purchase_old.txt', 'w+')
    for index, row in purchases_df.iterrows():
        line = row['timestamp'] + ',' + row['user'] + ',' + row['code'] + '\n'
        filePurchases_old.writelines(line)
    filePurchases_old.close()


def transform_products():
    check_for_file(PRODUCTS_FILE)
    try:
        products_df = pd.read_csv(PRODUCTS_FILE, header=None)
        products_df.columns = ['nr', 'code', 'desc', 'price']
        filePurchases_new = open(PRODUCTS_FILE, 'w+')
        for _, row in products_df.iterrows():
            line = f"{row['nr']},{row['code']},{row['desc']},{row['price']},0\n"
            filePurchases_new.writelines(line)
        filePurchases_new.close()
    except pd.errors.EmptyDataError:
        pass
