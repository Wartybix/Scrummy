# ingredient.py
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

from typing import Optional

class Ingredient:
    def __init__(self, name: str, bb_date: 'datetime'):
        self.name = name
        self.bb_date = bb_date
        self.frozen = False

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def set_bb_date(self, bb_date):
        self.bb_date = bb_date

    def get_bb_date(self):
        return self.bb_date

    def set_frozen(self, is_frozen: bool):
        self.frozen = is_frozen

    def get_frozen(self):
        return self.frozen

    def __str__(self):
        return f"{self.name} (exp. {self.bb_date}) -- {'un' if not self.frozen else ''}frozen"
