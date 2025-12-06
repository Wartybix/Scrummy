# ingredient_row.py
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

from gi.repository import Adw, Gtk, GLib
from scrummy import PREFIX
from typing import Optional
from scrummy.shared import min_date
from scrummy.new_ingredient_dialog import NewIngredientDialog

# TODO: low coupling high cohesion... move everything calling window code into
# a passed function?

def show_edit_dialog(
    ingredient: 'Ingredient',
    action_name: str,
    parameter: GLib.Variant
) -> None:
    window = ingredient.get_ancestor(Adw.ApplicationWindow)

    def do_edit(name: str, date: Optional[GLib.DateTime]) -> None:
        selected_meal = window.sidebar.get_selected_item()
        old_date = selected_meal.get_bb_date()

        ingredient.set_title(name)
        ingredient.set_bb_date(date)

        selected_meal.update()

        if selected_meal != window.unsorted_food:
            sidebar_section_model = window.sidebar_section_model
            sidebar_section_model.update_meal_position(selected_meal, old_date)

    dialog = NewIngredientDialog(
        do_edit,
        ingredient.get_title(),
        ingredient.get_bb_date()
    )

    dialog.present(window)

def duplicate(
    ingredient: 'Ingredient',
    action_name: str,
    parameter: GLib.Variant
) -> None:
    new_ingredient = ingredient.copy()

    window = ingredient.get_ancestor(Adw.ApplicationWindow)
    selected_meal = window.sidebar.get_selected_item()

    selected_meal.add_ingredient(new_ingredient)


@Gtk.Template(resource_path=f"{PREFIX}/ingredient.ui")
class Ingredient(Adw.ActionRow):
    """ An action row representing an ingredient / food item """
    __gtype_name__ = "Ingredient"

    end_viewstack = Gtk.Template.Child()
    menu_button = Gtk.Template.Child()
    check_button = Gtk.Template.Child()

    def __init__(self, title: str, bb_date: Optional[GLib.DateTime], **kwargs):
        super().__init__(**kwargs)

        self.set_title(title)
        self.set_bb_date(bb_date)

        self.frozen = False

        self.install_action('ingredient.edit', None, show_edit_dialog)
        self.install_action('ingredient.duplicate', None, duplicate)

    def set_bb_date(self, bb_date: GLib.DateTime) -> None:
        self.bb_date = bb_date

        if bb_date:
            date_str = bb_date.format("%x")
            self.set_subtitle(_("Use by {}").format(date_str))
        else:
            self.set_subtitle(_("Undated"))

    def get_bb_date(self) -> Optional[GLib.DateTime]:
        return self.bb_date

    def get_bb_sort_date(self) -> GLib.DateTime:
        if self.bb_date:
            return self.bb_date
        else:
            return min_date

    def set_selectable(self, is_selectable: bool) -> None:
        self.end_viewstack.set_visible_child(
            self.check_button if is_selectable else self.menu_button
        )

        self.check_button.set_sensitive(is_selectable)
        self.check_button.set_active(False)

    @Gtk.Template.Callback()
    def on_selection_toggled(self, check_button: Gtk.CheckButton) -> None:
        if not check_button.get_sensitive():
            # Don't do anything if check button is not sensitive.
            return

        # TODO: low coupling high cohesion... change to passed function
        window = self.get_ancestor(Adw.ApplicationWindow)

        if check_button.get_active():
            window.add_selection(self)
        else:
            window.remove_selection(self)

    def set_selected(self, is_selected: bool) -> None:
        self.check_button.set_active(is_selected)

    def copy(self) -> 'Ingredient':
        return Ingredient(self.get_title(), self.bb_date)

    def __str__(self):
        bb_date = self.bb_date
        bb_msg = f"exp. {bb_date.format('%x')}" if bb_date else "undated"

        return f"{self.get_title()} ({bb_msg}) -- {'un' if not self.frozen else ''}frozen"
