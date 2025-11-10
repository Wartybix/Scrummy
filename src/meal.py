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
from typing import List
from gi.repository import Adw, Gtk, GObject

class Meal(Adw.SidebarItem):
    """ Sidebar item representing a meal """
    __gtype_name__ = "Meal"

    def __init__(self, ingredients: List['Ingredient']=[], **kwargs):
        self.ingredients = ingredients

    def set_name(self, name):
        self.name = name

    def get_name(self, name):
        return self.name

    def add_ingredient(self, ingredient: 'Ingredient'):
        self.ingredients += ingredient

    def remove_ingredient(self, ingredient: 'Ingredient'):
        self.ingredients -= ingredient

    def __str__(self):
        msg = self.name
        if self.ingredients:
            for ingredient in self.ingredients:
                msg += f'\n\t{ingredient}'
        else:
            msg += f'\n\t[No ingredients]'

        return msg
