# new_ingredient_dialog.py
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

from gi.repository import Adw, Gtk, GLib, GObject
from typing import Callable
from scrummy import PREFIX

def default_date() -> GLib.DateTime:
    date = GLib.DateTime.new_now_local()
    return GLib.DateTime.new_local(
        date.get_year(),
        date.get_month(),
        date.get_day_of_month(),
        0,
        0,
        0.0
    )

def popup(menu_button: Gtk.MenuButton, user_data: any=None) -> None:
    dialog = menu_button.get_ancestor(NewIngredientDialog)

    parsed_date = dialog.parse_date_entry()

    dialog.set_date_entry(parsed_date)
    dialog.calendar.set_date(parsed_date)

@Gtk.Template(resource_path=f"{PREFIX}/new_ingredient_dialog.ui")
class NewIngredientDialog(Adw.Dialog):
    """ An action row representing an ingredient / food item """
    __gtype_name__ = "NewIngredientDialog"

    name_row = Gtk.Template.Child()
    switch_row = Gtk.Template.Child()
    date_row = Gtk.Template.Child()
    calendar = Gtk.Template.Child()
    date_button = Gtk.Template.Child()

    def __init__(
        self,
        on_submit: Callable[[Gtk.Widget, str, GLib.DateTime], None],
        **kwargs
    ):
        super().__init__(**kwargs)
        self.on_submit = on_submit

        self.date_button.set_create_popup_func(popup)

        self.set_date_entry(default_date())

    def parse_date_entry(self) -> GLib.DateTime:
        parsed_date = GLib.Date.new()
        parsed_date.set_parse(self.date_row.get_text())

        if parsed_date.valid():
            return GLib.DateTime.new_local(
                parsed_date.get_year(),
                parsed_date.get_month(),
                parsed_date.get_day(),
                0,
                0,
                0.0
            )
        else:
            return default_date()

    # TODO: convert '25' -> '2025' etc.

    def set_date_entry(self, date: GLib.DateTime) -> None:
        self.date_row.set_text(date.format('%x'))

    @Gtk.Template.Callback()
    def on_date_focus_change(
        self,
        focus_controller: Gtk.EventControllerFocus,
        pspec: GObject.ParamSpec,
    ) -> None:
        parsed_date = self.parse_date_entry()

        self.set_date_entry(parsed_date)

    @Gtk.Template.Callback()
    def calendar_select_date(self, widget: Gtk.Widget) -> None:
        date = self.calendar.get_date()

        self.set_date_entry(date)

    @Gtk.Template.Callback()
    def submit(self, widget: Gtk.Widget) -> None:
        if self.name_row.get_text_length() == 0:
            return

        name = self.name_row.get_text()

        date_set = self.switch_row.get_active()
        bb_date = self.parse_date_entry() if date_set else None

        self.on_submit(name, bb_date)
        self.close()

    @Gtk.Template.Callback()
    def cancel(self, widget: Gtk.Widget) -> None:
        self.close()
