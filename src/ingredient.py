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
import datetime

@Gtk.Template(resource_path=f"{PREFIX}/ingredient.ui")
class Ingredient(Adw.ActionRow):
    """ An action row representing an ingredient / food item """
    __gtype_name__ = "Ingredient"

    def __init__(self, title: str, bb_date: Optional[datetime.datetime], **kwargs):
        super().__init__(**kwargs)

        self.set_title(title)
        self.bb_date = bb_date

        # TODO: change based on localisations
        if bb_date:
            date_str = bb_date.strftime("%d/%m/%Y")
            self.set_subtitle(_("Use by {}").format(date_str))
        else:
            self.set_subtitle(_("Undated"))

        self.frozen = False

    def get_bb_sort_date(self) -> datetime.datetime:
        return self.bb_date if self.bb_date else datetime.datetime.min

    def __str__(self):
        return f"{self.get_title()} (exp. {self.bb_date}) -- {'un' if not self.frozen else ''}frozen"
