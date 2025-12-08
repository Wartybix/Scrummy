# window.py
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

from gi.repository import Adw, Gtk, GLib, Gio
from scrummy.ingredient import Ingredient
from scrummy.new_meal_dialog import NewMealDialog
from scrummy.new_ingredient_dialog import NewIngredientDialog
from scrummy.meal import Meal
from scrummy.sidebar_section_model import SidebarSectionModel
from scrummy import PREFIX
from typing import Optional
from gettext import ngettext

@Gtk.Template(resource_path=f'{PREFIX}/window.ui')
class ScrummyWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'ScrummyWindow'

    ingredients_list = Gtk.Template.Child()
    split_view = Gtk.Template.Child()
    sidebar = Gtk.Template.Child()
    main_nav_page = Gtk.Template.Child()
    unsorted_food = Gtk.Template.Child()
    add_ingredient_btn = Gtk.Template.Child()
    add_ingredient_btn_empty = Gtk.Template.Child()
    ingredient_search_entry = Gtk.Template.Child()
    eat_btn = Gtk.Template.Child()
    viewstack = Gtk.Template.Child()
    search_bar = Gtk.Template.Child()
    bottom_bar_viewstack = Gtk.Template.Child()
    add_ingredient_action_bar = Gtk.Template.Child()
    management_action_bar = Gtk.Template.Child()
    empty_status_page = Gtk.Template.Child()
    toast_overlay = Gtk.Template.Child()
    header_viewstack = Gtk.Template.Child()
    normal_headerbar = Gtk.Template.Child()
    select_mode_headerbar = Gtk.Template.Child()
    select_mode_button = Gtk.Template.Child()
    selection_title = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_meal_action = Gio.SimpleAction(name="add_meal")
        self.add_meal_action.connect("activate", self.add_meal_dialog)
        self.add_action(self.add_meal_action)

        self.eat_meal_action = Gio.SimpleAction(name="eat_meal")
        self.eat_meal_action.connect("activate", self.eat_meal)
        self.add_action(self.eat_meal_action)

        self.duplicate_meal_action = Gio.SimpleAction(name="duplicate_meal")
        self.duplicate_meal_action.connect("activate", self.duplicate_meal)
        self.add_action(self.duplicate_meal_action)

        self.rename_meal_action = Gio.SimpleAction(name="rename_meal")
        self.rename_meal_action.connect("activate", self.rename_meal)
        self.add_action(self.rename_meal_action)

        self.sidebar_section_model = SidebarSectionModel(self.sidebar)

        self.add_ingredient_action = Gio.SimpleAction(name="add_ingredient")
        self.add_ingredient_action.connect(
            "activate",
            self.add_ingredient_dialog
        )
        self.add_action(self.add_ingredient_action)

        self.selected_ingredients = []

        self.refresh_main_content()

    @Gtk.Template.Callback()
    def enable_select_mode(self, widget: Gtk.Widget, **kwargs) -> None:
        self.set_select_mode(True)
        self.update_selection_counter()

    @Gtk.Template.Callback()
    def disable_select_mode(self, widget: Gtk.Widget, **kwargs) -> None:
        self.set_select_mode(False)
        self.selected_ingredients = []

    @Gtk.Template.Callback()
    def ingredients_on_right_click(
        self,
        gesture: Gtk.GestureClick,
        n_press: int,
        x: float,
        y: float
    ) -> None:
        self.do_select_gesture(x, y)

    @Gtk.Template.Callback()
    def ingredients_on_long_press(
        self,
        gesture: Gtk.GestureLongPress,
        x: float,
        y: float
    ) -> None:
        self.do_select_gesture(x, y)

    def do_select_gesture(self, x: float, y: float) -> None:
        self.set_select_mode(True)
        pick = self.ingredients_list.pick(x, y, Gtk.PickFlags.DEFAULT)

        if pick is not Ingredient:
            pick = pick.get_ancestor(Ingredient)

        pick.set_selected(True)

    def set_select_mode(self, enabled: bool) -> None:
        normal_headerbar = self.normal_headerbar
        select_mode_headerbar = self.select_mode_headerbar

        manage_bar = self.management_action_bar
        add_bar = self.add_ingredient_action_bar

        header_viewstack = self.header_viewstack
        bottom_viewstack = self.bottom_bar_viewstack

        visible_headerbar = header_viewstack.get_visible_child()
        select_mode_on = visible_headerbar == select_mode_headerbar

        if select_mode_on == enabled:
            # Don't do anything when the state is the same as before.
            return

        header_viewstack.set_visible_child(
            select_mode_headerbar if enabled else normal_headerbar
        )
        bottom_viewstack.set_visible_child(manage_bar if enabled else add_bar)

        selected_meal = self.sidebar.get_selected_item()
        selected_meal.set_selectable(enabled)

    def add_selection(self, ingredient: Ingredient) -> None:
        self.selected_ingredients.append(ingredient)
        self.update_selection_counter()

    def remove_selection(self, ingredient: Ingredient) -> None:
        self.selected_ingredients.remove(ingredient)
        self.update_selection_counter()

    def update_selection_counter(self) -> None:
        num_selected = len(self.selected_ingredients)

        selected_meal = self.sidebar.get_selected_item()

        if selected_meal == self.unsorted_food:
            title = ngettext("{} Item Selected", "{} Items Selected", num_selected)
        else:
            title = ngettext("{} Ingredient Selected", "{} Ingredients Selected", num_selected)

        title = title.format(num_selected)
        self.selection_title.set_title(title)

        self.selection_title.set_subtitle(self.main_nav_page.get_title())

    def rename_meal(self, action: Gio.Action, parameter: GLib.Variant) -> None:
        selected_meal = self.sidebar.get_selected_item()

        def do_rename(new_name):
            selected_meal.set_title(new_name)
            self.sidebar_section_model.update_meal_position(
                selected_meal,
                selected_meal.get_bb_date()
            )
            self.main_nav_page.set_title(new_name)

        dialog = NewMealDialog(
            do_rename,
            selected_meal.get_title()
        )
        dialog.present(self)

    def duplicate_meal(
        self,
        action: Gio.Action,
        parameter: GLib.Variant
    ) -> None:
        selected_meal = self.sidebar.get_selected_item()
        new_meal = Meal(selected_meal.get_title(), Gio.ListStore(), False)
        new_ingredients = []

        i = 0
        while ingredient := selected_meal.ingredients.get_item(i):
            new_ingredients.append(ingredient.copy())
            i += 1

        new_meal.ingredients.splice(0, 0, new_ingredients)
        new_meal.update_subtitle()

        self.sidebar_section_model.add_meal(new_meal)

        toast = Adw.Toast.new(
            # TRANSLATORS: {} represents a name of a meal.
            _('‘{}’ duplicated').format(new_meal.get_title())
        )
        self.toast_overlay.add_toast(toast)

    def eat_meal(self, action: Gio.Action, parameter: GLib.Variant) -> None:
        # TODO: fix cases where sidebar selected desynced from main view
        selected_item = self.sidebar.get_selected_item()
        self.sidebar_section_model.remove_meal(selected_item)
        self.refresh_main_content()
        self.split_view.set_show_content(False)

        toast = Adw.Toast.new(
            # TRANSLATORS: {} represents a name of a meal.
            _("‘{}’ marked as eaten").format(selected_item.get_title())
        )
        toast.set_button_label(_("Undo")) # TODO: make this button do something
        self.toast_overlay.add_toast(toast)

    def set_main_page(self, is_empty: bool) -> None:
        page_name = "empty-meal-page" if is_empty else "ingredients-page"
        self.viewstack.set_visible_child_name(page_name)
        self.search_bar.set_visible(not is_empty)
        self.bottom_bar_viewstack.set_visible(not is_empty)
        self.select_mode_button.set_visible(not is_empty)

    def refresh_main_content(self) -> None:
        selected_item = self.sidebar.get_selected_item()
        page_title = selected_item.get_title()

        if selected_item == self.unsorted_food:
            ingredient_search_label = _("Search items")
            # TRANSLATORS: please use U+2026 (…) rather than 3 dots "...", if
            # it's appropriate/applicable to your language.
            add_ingredient_btn_label = _("Add _Item…")

            page_title = page_title.replace("_", "")
            self.eat_btn.set_visible(False)

            empty_status_page_title = _("No Food")
            empty_status_page_desc = _("Add snacks and miscellaneous food here")
        else:
            ingredient_search_label = _("Search ingredients")
            # TRANSLATORS: please use U+2026 (…) rather than 3 dots "...", if
            # it's appropriate/applicable to your language.
            add_ingredient_btn_label = _("Add _Ingredient…")

            self.eat_btn.set_visible(True)

            empty_status_page_title = _("Empty Meal")
            empty_status_page_desc = _("Add ingredients to sort this meal in the agenda")

        self.main_nav_page.set_title(page_title)

        self.ingredients_list.bind_model(selected_item.ingredients, lambda x: x)

        empty_meal = len(selected_item.ingredients) == 0
        self.set_main_page(empty_meal)

        self.ingredient_search_entry.set_placeholder_text(ingredient_search_label)
        self.add_ingredient_btn.set_label(add_ingredient_btn_label)
        self.add_ingredient_btn_empty.set_label(add_ingredient_btn_label)
        self.empty_status_page.set_title(empty_status_page_title)
        self.empty_status_page.set_description(empty_status_page_desc)

        self.header_viewstack.set_visible_child(self.normal_headerbar)
        self.bottom_bar_viewstack.set_visible_child(self.add_ingredient_action_bar)
        selected_item.set_selectable(False)
        self.selected_ingredients = []

        print('------------')
        for meal in list(self.sidebar.get_items()):
            print(meal)

        self.split_view.set_show_content(True);

    @Gtk.Template.Callback()
    def on_sidebar_activated(self, index: int, user_data: any) -> None:
        print("sidebar activated")
        self.refresh_main_content()

    def add_meal_dialog(self, action: Gio.Action, parameter: GLib.Variant) -> None:
        def add_meal(name: str) -> None:
            meal = Meal(name, Gio.ListStore(), False)

            self.sidebar_section_model.add_meal(meal)

            print('------------')
            for meal in list(self.sidebar.get_items()):
                print(meal)

        dialog = NewMealDialog(add_meal)
        dialog.present(self)

    def add_ingredient_dialog(
        self,
        action: Gio.Action,
        parameter: GLib.Variant
    ) -> None:
        def add_ingredient(name: str, date: Optional[GLib.DateTime]) -> None:
            ingredient = Ingredient(name, date)
            selected_item = self.sidebar.get_selected_item()

            old_date = selected_item.get_bb_date()

            selected_item.add_ingredient(ingredient)
            self.set_main_page(False)

            if selected_item != self.unsorted_food:
                self.sidebar_section_model.update_meal_position(selected_item, old_date)

        dialog = NewIngredientDialog(add_ingredient)
        dialog.present(self)
