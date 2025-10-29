# new_meal_dialog.py
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

@Gtk.Template(resource_path="/io/github/wartybix/Scrummy/new_meal_dialog.ui")
class NewMealDialog(Adw.Dialog):
    """ An action row representing an ingredient / food item """
    __gtype_name__ = "NewMealDialog"

    entry_row = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @Gtk.Template.Callback()
    def submit(self, widget):
        if self.entry_row.get_text_length() == 0:
            return

        print(f'submitted: {self.entry_row.get_text()}')
        self.close()
