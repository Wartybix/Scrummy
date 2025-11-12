# sidebar_section_model.py
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

from gi.repository import Adw, Gio
from scrummy.meal import Meal
import datetime

def compare_meals(a: Meal, b: Meal) -> int:
    a_title = a.get_title()
    b_title = b.get_title()

    if a_title < b_title:
        return -1
    elif a_title == b_title:
        return 0
    else:
        return 1

class SidebarSectionModel():
    def __init__(self, sidebar: Adw.Sidebar, **kwargs):
        super().__init__(**kwargs)

        self.sidebar = sidebar
        self.offset = len(sidebar.get_sections()) # For 'unsorted food' etc.
        self.sections = dict()

    def add_meal(self, meal: Meal) -> None:
        bb_date = meal.get_bb_date()
        sections_keys = self.sections.keys()

        if bb_date not in sections_keys:
            self.sections[bb_date] = Gio.ListStore()
            sidebar_section = Adw.SidebarSection()
            sidebar_section.bind_model(self.sections[bb_date], lambda x: x)

            if bb_date:
                # TODO: dynamic localisation etc.
                section_title = _("Eat by {}").format(bb_date.strftime("%d/%m/%Y"))
                sections_sorted = sorted([
                    datetime.datetime.min if x is None else x for x in self.sections
                ])
                section_index = sections_sorted.index(bb_date) + self.offset
            else:
                section_title = _("Undated")
                section_index = 0 + self.offset

            sidebar_section.set_title(section_title)

            self.sidebar.insert(sidebar_section, section_index)

        self.sections[bb_date].insert_sorted(meal, compare_meals)

    def remove_meal(self, meal: Meal) -> None:
        bb_date = meal.get_bb_date()
        section_index = meal.get_section_index()

        self.sections[bb_date].remove(section_index)

    def update_meal_position(self, meal: Meal, old_date: datetime.datetime) -> None:
        section_index = meal.get_section_index()
        self.sections[old_date].remove(section_index)

        self.add_meal(meal)

        self.sidebar.set_selected(meal.get_index())
