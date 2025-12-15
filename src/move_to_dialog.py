# move_to_dialog.py
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
from typing import Callable, List
from scrummy import PREFIX
from scrummy.meal import Meal, Ingredient

def create_row(meal: Meal, current_meal: Meal) -> Adw.ActionRow:
    row = Adw.ActionRow()
    row.set_title(meal.get_title())
    row.set_use_underline(True)

    radio_button = Gtk.CheckButton()
    radio_button.set_valign(Gtk.Align.CENTER)

    row.add_prefix(radio_button)
    row.set_activatable_widget(radio_button)

    row.set_sensitive(meal != current_meal)

    return row


@Gtk.Template(resource_path=f"{PREFIX}/move_to_dialog.ui")
class MoveToDialog(Adw.Dialog):
    """ A dialog to move an ingredient into another meal """
    __gtype_name__ = "MoveToDialog"

    # TODO: allow double click on radio button row?

    main_page = Gtk.Template.Child()
    move_btn = Gtk.Template.Child()
    
    # TODO: add search functionality

    def __init__(
        self,
        on_submit: Callable[[Meal], None],
        all_meals: List[Meal],
        current_meal: Meal,
        **kwargs
    ):
        super().__init__(**kwargs)

        if len(all_meals) < 2:
            raise Exception("This dialog should not be called when there's less than 2 meals!")

        group = Adw.PreferencesGroup()
        initial_radio_btn = None

        for meal in all_meals:        
            row = Adw.ActionRow()
            row.set_title(meal.get_title())

            radio_button = Gtk.CheckButton()
            radio_button.set_valign(Gtk.Align.CENTER)
            
            radio_button.connect("toggled", self.set_selected_meal)
            
            if initial_radio_btn:
                radio_button.set_group(initial_radio_btn)
            else:
                initial_radio_btn = radio_button

            row.add_prefix(radio_button)
            row.set_activatable_widget(radio_button)
                
            row.set_sensitive(meal != current_meal)

            group.add(row)

        self.main_page.add(group)

        self.selected_meal = None
        self.all_meals = all_meals
        self.on_submit = on_submit
        
    def set_selected_meal(self, check_button: Gtk.CheckButton) -> None:
        if not check_button.get_active():
            # Don't do anything if check button has been *unchecked*.
            return
        
        action_row = check_button.get_ancestor(Adw.ActionRow)
        index = action_row.get_index()
        
        self.selected_meal = self.all_meals[index]
        self.move_btn.set_sensitive(True)

    @Gtk.Template.Callback()
    def cancel(self, widget: Gtk.Widget) -> None:
        self.close()

    @Gtk.Template.Callback()
    def submit(self, widget: Gtk.Widget) -> None:
        self.on_submit(self.selected_meal)
        self.close()
