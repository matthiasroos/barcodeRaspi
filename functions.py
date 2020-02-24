
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


def getMD5Hash(filename: str):
    hasher = hashlib.md5()
    with open(filename, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
    return hasher


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


def git_push(path_repo: str) -> bool:
    try:
        repo_local = git.Repo(path_repo)
        repo_local.git.add(PURCHASES_FILE)
        repo_local.index.commit("purchase via getraenkeKasse.py")
        origin = repo_local.remote(name='origin')
        origin.push()
        return True
    except git.GitCommandError as exception:
        print(exception)
        return False


def read_users() -> list:
    """"
    Read users from usersFile
    """
    if not os.path.isfile(USERS_FILE):
        raise Exception('USERS_FILE not found!')
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
    if not os.path.isfile(PRODUCTS_FILE):
        raise Exception('PRODUCTS_FILE not found!')
    file_products = open(PRODUCTS_FILE, "r")
    prod_list = list()
    prod_dict = {}
    for line in file_products:
        ll = line.split(",")
        ll[3] = ll[3][:-1]
        ll.append('N/A')
        prod_list.append(ll)
        prod_dict[ll[1]] = float(ll[3])
    file_products.close()
    prod_df = pd.DataFrame(prod_list, columns=['nr', 'code', 'desc', 'price', 'alcohol'])
    prod_df['code'] = prod_df['code'].astype(str)
    prod_df['price'] = prod_df['price'].astype(float)
    return prod_df


def calc_length_code(products_df: pd.DataFrame) -> set:
    """"""
    length = set()
    for index, row in products_df.iterrows():
        tmpLen = len(str(row['code']))
        if tmpLen > 0:
            length.add(tmpLen)
    return length


def read_purchases() -> pd.DataFrame:
    if not os.path.isfile(PURCHASES_FILE):
        raise Exception('PURCHASES_FILE not found!')
    try:
        purchases_df = pd.read_csv(PURCHASES_FILE, header=None)
        purchases_df.columns = ['timestamp', 'user', 'code']
        purchases_df['code'] = purchases_df['code'].astype(str)
    except pd.errors.EmptyDataError:
        purchases_df = pd.DataFrame([], columns=['timestamp', 'user', 'code'])
    return purchases_df


def get_purchases() -> pd.DataFrame:
    usersPurchases_df = read_purchases()
    products_df = read_products()
    usersPurchases_df = usersPurchases_df.merge(products_df, on='code', how='left', sort=False)
    return usersPurchases_df


def get_user_purchases(users_purchases_df: pd.DataFrame, user: str) -> typing.Tuple[np.int64, np.float64]:
    user_df = users_purchases_df[users_purchases_df['user'] == user]
    nr = user_df['timestamp'].count()
    money = user_df['price'].sum()
    return nr, money


def summarize_user_purchases() -> pd.DataFrame:
    usersPurchases_df = get_purchases()
    summary_purchases_df = usersPurchases_df.groupby('user').agg({'code': 'count', 'price': 'sum'})
    summary_purchases_df.reset_index(inplace=True)
    summary_purchases_df.columns = ['name', 'drinks', 'money']
    return summary_purchases_df


def save_purchase(user: str, code: str):
    if not os.path.isfile(PURCHASES_FILE):
        raise Exception("purchasesFile not found!")
    filePurchases = open(PURCHASES_FILE, "a")
    line = datetime.datetime.now().isoformat() + "," + user + "," + code + "\n"
    filePurchases.writelines(line)
    filePurchases.close()


def transform_purchases():
    purchases_df = get_purchases()
    purchases_df['paid'] = False
    purchases_df['paid'] = purchases_df['paid'].astype(str)
    filePurchases_new = open('purchase_new.txt', 'w+')
    for _, row in purchases_df.iterrows():
        line = row['timestamp']+','+row['user']+','+row['code']+','+row['paid']+'\n'
        filePurchases_new.writelines(line)
    filePurchases_new.close()


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
