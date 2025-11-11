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

from gi.repository import Adw, Gtk
from scrummy import PREFIX
from typing import Optional

@Gtk.Template(resource_path=f"{PREFIX}/ingredient_row.ui")
class IngredientRow(Adw.ActionRow):
    """ An action row representing an ingredient / food item """
    __gtype_name__ = "IngredientRow"

    def __init__(self, title: str, date: Optional['date'], **kwargs):
        super().__init__(**kwargs)

        self.set_title(title)
        self.date = date

        # TODO: change based on localisations
        if date:
            date_str = date.strftime("%d/%m/%Y")
            self.set_subtitle(_("Use by {}").format(date_str))
        else:
            self.set_subtitle(_("Undated"))

        self.frozen = False

    def __str__(self):
        return f"{self.get_title()} (exp. {self.date}) -- {'un' if not self.frozen else ''}frozen"
