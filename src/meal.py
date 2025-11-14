# meal.py
#
# Copyright 2025 Wartybix
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from scrummy.ingredient import Ingredient
from scrummy import PREFIX
from typing import List, Optional
from gettext import ngettext
from gi.repository import Adw, Gtk, Gio
import datetime

def compare_ingredients(a: Ingredient, b: Ingredient) -> int:
    a_bb_sort_date = a.get_bb_sort_date()
    b_bb_sort_date = b.get_bb_sort_date()

    if a_bb_sort_date < b_bb_sort_date:
        return -1
    elif a_bb_sort_date == b_bb_sort_date:
        a_title = a.get_title()
        b_title = b.get_title()

        if a_title < b_title:
            return -1
        elif a_title == b_title:
            return 0
        else:
            return 1
    else:
        return 1

class Meal(Adw.SidebarItem):
    """ Sidebar item representing a meal """
    __gtype_name__ = "Meal"

    def __init__(
        self,
        name: str="",
        ingredients: Gio.ListStore=Gio.ListStore(),
        misc_meal: bool=True,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.ingredients = ingredients
        self.misc_meal = misc_meal
        self.cached_bb_date = None
        self.cache_outdated = True

        self.avatar = Adw.Avatar.new(16, name, True)
        self.avatar.set_icon_name("restaurant-symbolic")

        if not misc_meal:
            self.set_prefix(self.avatar)

        self.set_title(name)
        self.update_subtitle()

    def set_title(self, name) -> None:
        super().set_title(name)
        self.avatar.set_text(name)

    def update_subtitle(self) -> None:
        num_ingredients = len(self.ingredients)
        if self.misc_meal:
            subtitle = ngettext("{} Item", "{} Items", num_ingredients)
        else:
            subtitle = ngettext("{} Ingredient", "{} Ingredients", num_ingredients)

        self.set_subtitle(
            subtitle.format(num_ingredients)
        )

    def get_bb_date(self) -> Optional[datetime.datetime]:
        if not self.cache_outdated:
            return self.cached_bb_date

        ingredient_dates = set(map(
            lambda x: x.get_bb_date(), self.ingredients
        ))

        if not ingredient_dates or None in ingredient_dates:
            self.cached_bb_date = None
        else:
            self.cached_bb_date = min(ingredient_dates)

        self.cache_outdated = False
        return self.cached_bb_date

    def add_ingredient(self, ingredient: Ingredient) -> None:
        self.ingredients.insert_sorted(ingredient, compare_ingredients)
        self.update_subtitle()
        self.cache_outdated = True

    def remove_ingredient(self, ingredient: Ingredient) -> None:
        self.ingredients -= ingredient
        self.cache_outdated = True

    def __str__(self):
        msg = f"{self.get_title()} (exp. {self.get_bb_date()})"

        if self.ingredients:
            for ingredient in self.ingredients:
                msg += f'\n\t{ingredient}'
        else:
            msg += f'\n\t[No ingredients]'

        return msg
