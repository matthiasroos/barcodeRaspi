#!/usr/bin/python3

import dataclasses

import pandas as pd

import functions


@dataclasses.dataclass()
class UserInformation:
    name: str = None
    drinks: int = 0
    money: float = 0
    favorite_drink: str = None
    drinks_per_day: float = 0


class UserStatistics:

    def __init__(self, user: str, purchases: pd.DataFrame, products: pd.DataFrame):
        self.user_information = UserInformation()
        self._update_user_information(user=user, purchases=purchases, products=products)

    def _update_user_information(self, user: str, purchases: pd.DataFrame, products: pd.DataFrame):
        all_users_purchases_df = functions.merge_purchases_products(purchases=purchases, products=products)
        user_purchases_df = all_users_purchases_df[all_users_purchases_df['user'] == user]
        self.user_information.name = user
        self.user_information.drinks = len(user_purchases_df)
        self.user_information.money = user_purchases_df['price'].sum()
        self.user_information.favorite_drink = self._determine_favorite_drink(user_purchases=user_purchases_df)
        self.user_information.drinks_per_day = self._calculate_drinks_per_day(user_purchases=user_purchases_df)

    def _determine_favorite_drink(self, user_purchases: pd.DataFrame) -> str:
        pass

    def _calculate_drinks_per_day(self, user_purchases: pd.DataFrame) -> float:
        pass


