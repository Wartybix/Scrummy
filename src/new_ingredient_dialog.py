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

from gi.repository import Adw, Gtk, GLib
from typing import Callable
import datetime
from scrummy import PREFIX

@Gtk.Template(resource_path=f"{PREFIX}/new_ingredient_dialog.ui")
class NewIngredientDialog(Adw.Dialog):
    """ An action row representing an ingredient / food item """
    __gtype_name__ = "NewIngredientDialog"

    name_row = Gtk.Template.Child()
    date_row = Gtk.Template.Child()

    def __init__(self, on_submit: Callable[[Gtk.Widget, str, 'datetime'], None], **kwargs):
        super().__init__(**kwargs)
        self.on_submit = on_submit

    @Gtk.Template.Callback()
    def clear_date(self, widget):
        self.date_row.set_text('');

    @Gtk.Template.Callback()
    def submit(self, widget):
        if self.name_row.get_text_length() == 0:
            return

        name = self.name_row.get_text()

        try:
            bb_date = datetime.datetime.strptime(self.date_row.get_text(), ('%d/%m/%Y'))
        except ValueError:
            bb_date = None

        self.on_submit(name, bb_date)
        self.close()

    @Gtk.Template.Callback()
    def cancel(self, widget):
        self.close()
