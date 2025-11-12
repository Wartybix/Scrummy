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

from scrummy.ingredient_row import IngredientRow
from typing import List, Optional
from gettext import ngettext
from gi.repository import Adw, Gtk, Gio

class Meal(Adw.SidebarItem):
    """ Sidebar item representing a meal """
    __gtype_name__ = "Meal"

    def __init__(
        self,
        name: str="",
        ingredients: 'GioListStore'=Gio.ListStore(),
        misc_meal: bool=True,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.set_title(name)
        self.ingredients = ingredients
        self.misc_meal = misc_meal
        self.update_subtitle()

    def update_subtitle(self):
        num_ingredients = len(self.ingredients)
        if self.misc_meal:
            subtitle = ngettext("{} Item", "{} Items", num_ingredients)
        else:
            subtitle = ngettext("{} Ingredient", "{} Ingredients", num_ingredients)

        self.set_subtitle(
            subtitle.format(num_ingredients)
        )

    def get_bb_date(self) -> Optional['datetime']:
        return None

    def add_ingredient(self, ingredient: 'Ingredient'):
        self.ingredients.append(ingredient)
        self.update_subtitle()

    def remove_ingredient(self, ingredient: 'Ingredient'):
        self.ingredients -= ingredient

    def __str__(self):
        msg = self.get_title()

        if self.ingredients:
            for ingredient in self.ingredients:
                msg += f'\n\t{ingredient}'
        else:
            msg += f'\n\t[No ingredients]'

        return msg
