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
        self.user_information = UserInformation()
        self.purchases = purchases
        self.products = products
        self._update_user_information(user=user, purchases=self.purchases, products=self.products)

    def _update_user_information(self, user: str, purchases: pd.DataFrame, products: pd.DataFrame):
        all_users_purchases_df = functions.merge_purchases_products(purchases=purchases, products=products)
        user_purchases_df = all_users_purchases_df[all_users_purchases_df['user'] == user]
        self.user_information.name = user
        self.user_information.drinks = len(user_purchases_df)
        self.user_information.money = user_purchases_df['price'].sum()
        self.user_information.favorite_drink, self.user_information.favorite_drink_ratio = \
            self._determine_favorite_drink(user_purchases=user_purchases_df)
        self.user_information.drinks_per_day = self._calculate_drinks_per_day(user_purchases=user_purchases_df)

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



@dataclasses.dataclass()
class ProductInformation:
    code: str = None
    desc: str = None
    price: int = 0


class ProductStatistics:

    def __init__(self, product_nr: str, purchases: pd.DataFrame, products: pd.DataFrame):
        self.product_information = ProductInformation()
        self._update_product_information(product_nr=product_nr, purchases=purchases, products=products)

    def _update_product_information(self, product_nr: str, purchases: pd.DataFrame, products: pd.DataFrame):
        all_purchases_df = functions.merge_purchases_products(purchases=purchases, products=products)
        product_purchases_df = all_purchases_df[all_purchases_df['nr'] == product_nr]
        self.product_information.code = product_purchases_df['code'][0]

