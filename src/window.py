# window.py
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

from gi.repository import Adw, Gtk, GLib, Gio
from scrummy.ingredient_row import IngredientRow
from scrummy.new_meal_dialog import NewMealDialog
from scrummy.new_ingredient_dialog import NewIngredientDialog
from scrummy.meal import Meal
from scrummy.ingredient import Ingredient
from scrummy import PREFIX

@Gtk.Template(resource_path=f'{PREFIX}/window.ui')
class ScrummyWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'ScrummyWindow'

    ingredients_list = Gtk.Template.Child()
    split_view = Gtk.Template.Child()
    sidebar = Gtk.Template.Child()
    main_nav_page = Gtk.Template.Child()
    unsorted_food = Gtk.Template.Child()
    add_ingredient_btn = Gtk.Template.Child()
    ingredient_search_entry = Gtk.Template.Child()
    eat_btn = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_meal_action = Gio.SimpleAction(name="add_meal")
        self.add_meal_action.connect("activate", self.add_meal_dialog)
        self.add_action(self.add_meal_action)

        self.add_ingredient_action = Gio.SimpleAction(name="add_ingredient")
        self.add_ingredient_action.connect(
            "activate",
            self.add_ingredient_dialog
        )
        self.add_action(self.add_ingredient_action)

        # Dummy UI elements -- TODO remove later
        self.ingredients_list.add(IngredientRow('Beans', 'Use by 25/10/2025'))
        self.ingredients_list.add(IngredientRow('Eggs', 'Use by 01/11/2025'))
        self.ingredients_list.add(IngredientRow('Rice', 'Use by 01/01/2027'))

        self.refresh_main_content()

    def refresh_main_content(self):
        selected_item = self.sidebar.get_selected_item()
        page_title = selected_item.get_title()

        if selected_item == self.unsorted_food:
            ingredient_search_label = _("Search items")
            # TRANSLATORS: please use U+2026 (…) rather than 3 dots "...", if
            # it's appropriate/applicable to your language.
            add_ingredient_btn_label = _("Add _Item…")

            page_title = page_title.replace("_", "")
            self.eat_btn.set_visible(False)
        else:
            ingredient_search_label = _("Search ingredients")
            # TRANSLATORS: please use U+2026 (…) rather than 3 dots "...", if
            # it's appropriate/applicable to your language.
            add_ingredient_btn_label = _("Add _Ingredient…")

            self.eat_btn.set_visible(True)

        self.main_nav_page.set_title(page_title)

        self.ingredient_search_entry.set_placeholder_text(ingredient_search_label)
        self.add_ingredient_btn.set_label(add_ingredient_btn_label)

        print(type(self.sidebar.get_items()))
        print(list(self.sidebar.get_items()))

        self.split_view.set_show_content(True);

    @Gtk.Template.Callback()
    def on_sidebar_activated(self, index, user_data):
        self.refresh_main_content()

    def add_meal_dialog(self, action: Gio.Action, parameter: GLib.Variant):
        def add_meal(name: str):
            meal = Meal(name)
            print(meal)

        dialog = NewMealDialog(add_meal)
        dialog.present(self)

    def add_ingredient_dialog(
        self,
        action: Gio.Action,
        parameter: GLib.Variant
    ):
        def add_ingredient(name: str, date: 'datetime'):
            ingredient = Ingredient(name, date)
            print(ingredient)

        dialog = NewIngredientDialog(add_ingredient)
        dialog.present(self)
