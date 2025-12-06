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
from gi.repository import Adw, Gtk, Gio, Gsk, Graphene, Gdk, GLib
from ctypes import c_uint32

def compare_ingredients(a: Ingredient, b: Ingredient) -> int:
    a_bb_sort_date = a.get_bb_sort_date()
    b_bb_sort_date = b.get_bb_sort_date()

    comparison = a_bb_sort_date.compare(b_bb_sort_date)

    if comparison == 0:
        a_title = a.get_title()
        b_title = b.get_title()

        if a_title < b_title:
            return -1
        elif a_title == b_title:
            return 0
        else:
            return 1
    else:
        return comparison

# Function taken from:
# https://mojoauth.com/hashing/bernsteins-hash-djb2-in-python/
# with some modifications
def djb2_hash(string):
    hash_value = 5381  # Initial hash value
    for char in string:  # Iterate through each character
        hash_value = (hash_value << 5) + hash_value + ord(char)  # Update hash value
        hash_value = c_uint32(hash_value).value # Keep limited to 32 bit unsigned integer
    return hash_value  # Return final hash value
    
# TODO: check there aren't problems when changing timezone.

class Meal(Adw.SidebarItem):
    """ Sidebar item representing a meal """
    __gtype_name__ = "Meal"

    def __init__(
        self,
        name: str="",
        ingredients: Gio.ListStore=Gio.ListStore(),
        misc_meal: bool=True, # TODO: maybe make this an inheritance thing instead?
        **kwargs
    ):
        super().__init__(**kwargs)

        # TODO: simplify ingredients parameter?

        self.ingredients = ingredients
        self.misc_meal = misc_meal
        self.cached_bb_date = None
        self.cache_outdated = True

        self.set_title(name)
        self.update_subtitle()

    def set_title(self, name) -> None:
        super().set_title(name)

        if not self.misc_meal:
            snapshot = Gtk.Snapshot()

            path_builder = Gsk.PathBuilder.new()
            path_builder.add_circle(Graphene.Point().init(1.0, 1.0), 1.0)

            circle = path_builder.to_path()

            colors = [
               "#337fdc", # blue
               "#0f9ac8", # cyan
               "#29ae74", # green
               "#6ab85b", # lime
               "#d29d09", # yellow
               "#d68400", # gold
               "#ed5b00", # orange
               "#e62d42", # raspberry
               "#e33b6a", # magenta
               "#9945b5", # purple
               "#7a59ca", # violet
               "#b08952", # beige
               "#785336", # brown
               "#6e6d71", # gray
            ]

            rgba = Gdk.RGBA()

            color_class = djb2_hash(name) % len(colors)

            rgba.parse(colors[color_class])

            snapshot.append_fill(circle, Gsk.FillRule.WINDING, rgba)

            paintable = snapshot.to_paintable()

            self.set_icon_paintable(paintable)

    def update_subtitle(self) -> None:
        num_ingredients = len(self.ingredients)
        if self.misc_meal:
            subtitle = ngettext("{} Item", "{} Items", num_ingredients)
        else:
            subtitle = ngettext("{} Ingredient", "{} Ingredients", num_ingredients)

        self.set_subtitle(
            subtitle.format(num_ingredients)
        )

    def get_bb_date(self) -> Optional[GLib.DateTime]:
        if not self.cache_outdated:
            return self.cached_bb_date

        ingredient_dates = set(map(
            lambda x: x.get_bb_date(), self.ingredients
        ))

        if not ingredient_dates or None in ingredient_dates:
            self.cached_bb_date = None
        else:
            min_unix = min(set(map(lambda x: x.to_unix(), ingredient_dates)))
            self.cached_bb_date = GLib.DateTime.new_from_unix_local(min_unix)

        self.cache_outdated = False
        return self.cached_bb_date

    def add_ingredient(self, ingredient: Ingredient) -> None:
        self.ingredients.insert_sorted(ingredient, compare_ingredients)
        self.update_subtitle()
        self.cache_outdated = True

    def update(self):
        self.ingredients.sort(compare_ingredients)
        self.cache_outdated = True

    def remove_ingredient(self, ingredient: Ingredient) -> None:
        self.ingredients -= ingredient
        self.cache_outdated = True

    def set_selectable(self, is_selectable: bool) -> None:
        for ingredient in self.ingredients:
            ingredient.set_selectable(is_selectable)

    def __str__(self):
        bb_date = self.get_bb_date()

        bb_msg = f"exp. {bb_date.format('%x')}" if bb_date else "undated"

        msg = f"{self.get_title()} ({bb_msg})"

        if self.ingredients:
            for ingredient in self.ingredients:
                msg += f'\n\t{ingredient}'
        else:
            msg += f'\n\t[No ingredients]'

        return msg
