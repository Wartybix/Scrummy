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

@Gtk.Template(resource_path=f"{PREFIX}/ingredient.ui")
class Ingredient(Adw.ActionRow):
    """ An action row representing an ingredient / food item """
    __gtype_name__ = "Ingredient"

    def __init__(self, title: str, bb_date: Optional[GLib.DateTime], **kwargs):
        super().__init__(**kwargs)

        self.set_title(title)
        self.bb_date = bb_date

        # TODO: change based on localisations
        if bb_date:
            date_str = bb_date.format("%x")
            self.set_subtitle(_("Use by {}").format(date_str))
        else:
            self.set_subtitle(_("Undated"))

        self.frozen = False

    def get_bb_date(self) -> Optional[GLib.DateTime]:
        return self.bb_date

    def get_bb_sort_date(self) -> GLib.DateTime:
        if self.bb_date:
            return self.bb_date
        else:
            return min_date

    def copy(self) -> 'Ingredient':
        return Ingredient(self.get_title(), self.bb_date)

    def __str__(self):
        bb_date = self.bb_date
        bb_msg = f"exp. {bb_date.format('%x')}" if bb_date else "undated"

        return f"{self.get_title()} ({bb_msg}) -- {'un' if not self.frozen else ''}frozen"
