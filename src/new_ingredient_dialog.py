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

class RubberBandAmount:
    MONTH = 0
    YEAR = 1

class RubberBandDirection:
    BACKWARDS = 0
    FORWARDS = 1

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
            current_year = GLib.DateTime.new_now_local().get_year()
            entered_year = parsed_date.get_year()

            entry_remainder = entered_year % 100

            range_end = current_year + 50

            century_remainder = range_end % 100
            carry = 0 if entry_remainder < century_remainder else 1
            century = (range_end // 100 - carry) * 100

            corrected_year = century + entry_remainder

            return GLib.DateTime.new_local(
                corrected_year,
                parsed_date.get_month(),
                parsed_date.get_day(),
                0,
                0,
                0.0
            )
        else:
            return default_date()

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

    def rubberband_calendar(
        self,
        amount: RubberBandAmount,
        direction: RubberBandDirection
    ):
        selected_date = self.calendar.get_date()
        selected_year = selected_date.get_year()

        delta = 50 * (1 if direction == RubberBandDirection.BACKWARDS else -1)
        year_bound = GLib.DateTime.new_now_local().get_year() + delta

        if amount == RubberBandAmount.MONTH:
            add_function = selected_date.add_months
        else:
            add_function = selected_date.add_years

        corrected_date = None

        if direction == RubberBandDirection.BACKWARDS:
            if selected_year >= year_bound:
                corrected_date = add_function(-1)
        else:
            if selected_year < year_bound:
                corrected_date = add_function(1)

        if not corrected_date:
            self.set_date_entry(selected_date)
            return

        self.calendar.set_date(corrected_date)

    @Gtk.Template.Callback()
    def calendar_next_month(self, widget: Gtk.Widget) -> None:
        self.rubberband_calendar(
            RubberBandAmount.MONTH,
            RubberBandDirection.BACKWARDS
        )

    @Gtk.Template.Callback()
    def calendar_next_year(self, widget: Gtk.Widget) -> None:
        self.rubberband_calendar(
            RubberBandAmount.YEAR,
            RubberBandDirection.BACKWARDS
        )

    @Gtk.Template.Callback()
    def calendar_prev_month(self, widget: Gtk.Widget) -> None:
        self.rubberband_calendar(
            RubberBandAmount.MONTH,
            RubberBandDirection.FORWARDS
        )

    @Gtk.Template.Callback()
    def calendar_prev_year(self, widget: Gtk.Widget) -> None:
        self.rubberband_calendar(
            RubberBandAmount.YEAR,
            RubberBandDirection.FORWARDS
        )

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
