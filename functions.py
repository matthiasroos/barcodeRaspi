
import datetime
import git
import hashlib
import numpy as np
import os
import pandas as pd
import socket
import struct
import time
import typing

usersFile = "user.txt"
productsFile = "produkt.txt"
purchasesFile = "purchase.txt"


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


def gitPull(path_repo: str) -> bool:
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


def gitPush(path_repo: str):
    try:
        repoLocal = git.Repo(path_repo)
        repoLocal.git.add(purchasesFile)
        repoLocal.index.commit("purchase via getraenkeKasse.py")
        origin = repoLocal.remote(name='origin')
        origin.push()
    except git.GitCommandError as exception:
        print(exception)


def readUsers() -> list:
    """"
    Read users from usersFile
    """
    if not os.path.isfile(usersFile):
        raise Exception("usersFile not found!")
    fileUsers = open(usersFile, "r")
    users = []
    for line in fileUsers:
        users.append(line.rstrip())
    fileUsers.close()
    return users


def readProducts() -> pd.DataFrame:
    """"
    Read products from productsFile
    """
    if not os.path.isfile(productsFile):
        raise Exception("productsFile not found!")
    fileProducts = open(productsFile, "r")
    prod_list = list()
    prod_dict = {}
    for line in fileProducts:
        ll = line.split(",")
        ll[3] = ll[3][:-1]
        ll.append('N/A')
        prod_list.append(ll)
        prod_dict[ll[1]] = float(ll[3])
    fileProducts.close()
    prod_df = pd.DataFrame(prod_list, columns=['nr', 'code', 'desc', 'price', 'alcohol'])
    prod_df['code'] = prod_df['code'].astype(str)
    prod_df['price'] = prod_df['price'].astype(float)
    return prod_df


def calcLengthCode(products_df: pd.DataFrame) -> set:
    """"""
    length = set()
    for index, row in products_df.iterrows():
        tmpLen = len(str(row['code']))
        if tmpLen > 0:
            length.add(tmpLen)
    return length


def getPurchases() -> pd.DataFrame:
    if not os.path.isfile(purchasesFile):
        raise Exception("purchasesFile not found!")
    usersPurchases_df = pd.read_csv(purchasesFile, header=None)
    usersPurchases_df.columns = ['timestamp', 'user', 'code']
    usersPurchases_df['code'] = usersPurchases_df['code'].astype(str)
    products_df = readProducts()
    usersPurchases_df = usersPurchases_df.merge(products_df, on='code', how='left', sort=False)
    return usersPurchases_df


def getUserPurchases(users_purchases_df: pd.DataFrame, user: str) -> typing.Tuple[np.int64, np.float64]:
    user_df = users_purchases_df[users_purchases_df['user'] == user]
    nr = user_df['timestamp'].count()
    money = user_df['price'].sum()
    return nr, money


def summarizeUserPurchases() -> pd.DataFrame:
    usersPurchases_df = getPurchases()
    usersPurchases_df = usersPurchases_df.groupby()
    unique_users = users_purchases_df['user'].unique()

    nr, money = functions.getUserPurchases(users_purchases_df, user)
    summary_purchases_df = pd.DataFrame()
    return summary_purchases_df


def savePurchase(user: str, code: str):
    if not os.path.isfile(purchasesFile):
        raise Exception("purchasesFile not found!")
    filePurchases = open(purchasesFile, "a")
    line = datetime.datetime.now().isoformat() + "," + user + "," + code + "\n"
    filePurchases.writelines(line)
    filePurchases.close()
