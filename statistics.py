#!/usr/bin/python3

import dataclasses
import typing

import pandas as pd

import functions


@dataclasses.dataclass()
class UserInformation:
    name: str = None
    drinks: int = 0
    money: float = 0
    favorite_drink: str = None
    favorite_drink_ratio: float = 0.0
    drinks_per_day: float = 0


class UserStatistics:

    def __init__(self, user: str, purchases: pd.DataFrame, products: pd.DataFrame):
        self.purchases = purchases
        self.products = products
        self.user_information = UserInformation()
        all_users_purchases_df = functions.merge_purchases_products(purchases=self.purchases, products=self.products)
        user_purchases_df = all_users_purchases_df[all_users_purchases_df['user'] == user]
        self._update_user_information(user=user, user_purchases=user_purchases_df)

    def _update_user_information(self, user: str, user_purchases: pd.DataFrame):
        self.user_information.name = user
        self.user_information.drinks = len(user_purchases)
        self.user_information.money = user_purchases['price'].sum()
        self.user_information.favorite_drink, self.user_information.favorite_drink_ratio = \
            self._determine_favorite_drink(user_purchases=user_purchases)
        self.user_information.drinks_per_day = self._calculate_drinks_per_day(user_purchases=user_purchases)

    def _determine_favorite_drink(self, user_purchases: pd.DataFrame) -> typing.Tuple[str, float]:
        user_summary = user_purchases.groupby(by='code').agg({'timestamp': 'count'})
        user_summary.reset_index(inplace=True)
        user_summary.columns = ['code', 'drinks']
        user_summary.sort_values(by='drinks', ascending=False, inplace=True, ignore_index=True)
        favorite_drink_code = user_summary.at[0, 'code']
        favorite_drink_str = self.products[self.products['code'] == favorite_drink_code].reset_index().at[0, 'desc']
        return favorite_drink_str, user_summary.at[0, 'drinks']/sum(user_summary['drinks'])

    def _calculate_drinks_per_day(self, user_purchases: pd.DataFrame) -> float:
        pass

    def get_user_statistic(self):
        user_str = f'{self.user_information.name}\nfavorite drink: {self.user_information.favorite_drink}\n' \
                   f'ratio of fav. drink: {"{:4.3f}".format(self.user_information.favorite_drink_ratio)}'
        return user_str


@dataclasses.dataclass()
class ProductInformation:
    code: str = None
    desc: str = None
    price: int = 0
    favored_by_user: str = None
    ratio_by_user: float = 0.0


class ProductStatistics:

    def __init__(self, product_nr: int, purchases: pd.DataFrame, products: pd.DataFrame):
        self.purchases = purchases
        self.products = products
        self.product_information = ProductInformation()
        all_purchases_df = functions.merge_purchases_products(purchases=self.purchases, products=self.products)
        product_purchases_df = all_purchases_df[all_purchases_df['nr'] == product_nr]
        self._update_product_information(product_nr=product_nr, product_purchases=product_purchases_df)

    def _update_product_information(self, product_nr: int, product_purchases: pd.DataFrame):
        self.product_information.code = self.products[self.products['nr'] == product_nr].reset_index().at[0, 'code']
        self.product_information.desc = self.products[self.products['nr'] == product_nr].reset_index().at[0, 'desc']
        self.product_information.price = self.products[self.products['nr'] == product_nr].reset_index().at[0, 'price']
        if not product_purchases.empty:
            self.product_information.favored_by_user, self.product_information.ratio_by_user = \
                self._determine_favored_by_user(product_purchases=product_purchases)

    def _determine_favored_by_user(self, product_purchases: pd.DataFrame) -> typing.Tuple[str, float]:
        product_summary = product_purchases.groupby(by='user').agg({'timestamp': 'count'})
        product_summary.reset_index(inplace=True)
        product_summary.columns = ['user', 'drinks']
        product_summary.sort_values(by='drinks', ascending=False, inplace=True, ignore_index=True)
        favored_by_user_str = product_summary.at[0, 'user']
        return favored_by_user_str, product_summary.at[0, 'drinks']/sum(product_summary['drinks'])

    def get_product_statistic(self):
        product_str = f'{self.product_information.desc}\nfavored by user: {self.product_information.favored_by_user}\n' \
                      f'ratio of fav. user: {"{:4.3f}".format(self.product_information.ratio_by_user)}'
        return product_str

