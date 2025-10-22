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

@Gtk.Template(resource_path="/io/github/wartybix/Scrummy/ingredient_row.ui")
class IngredientRow(Adw.ActionRow):
    """ An action row representing an ingredient / food item """
    __gtype_name__ = "IngredientRow"

    def __init__(self, title, subtitle, **kwargs):
        super().__init__(**kwargs)

        self.set_title(title)
        self.set_subtitle(subtitle)
