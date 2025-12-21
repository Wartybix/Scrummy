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
from scrummy.move_to_dialog import MoveToDialog
from scrummy import PREFIX
from typing import Optional, List
from gettext import ngettext
import json

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
    content_viewstack = Gtk.Template.Child()
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
    window_viewstack = Gtk.Template.Child()
    unsorted_food_section = Gtk.Template.Child()

    # FIXME: blank toasts with items with '&' sign

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

        self.eat_selected_ingredients_action = Gio.SimpleAction(
            name="eat_selected_ingredients"
        )
        self.eat_selected_ingredients_action.connect(
            "activate",
            self.eat_selected_ingredients
        )
        self.add_action(self.eat_selected_ingredients_action)

        self.move_selected_ingredients_action = Gio.SimpleAction(
            name="move_selected_ingredients"
        )
        self.move_selected_ingredients_action.connect(
            "activate",
            self.show_move_to_dialog
        )
        self.move_selected_ingredients_action.set_enabled(False)
        self.add_action(self.move_selected_ingredients_action)

        self.open_file_action = Gio.SimpleAction(name="open_file")
        self.open_file_action.connect("activate", self.open_file_dialog)
        self.add_action(self.open_file_action)

        self.new_file_action = Gio.SimpleAction(name="new_file")
        self.new_file_action.connect("activate", self.new_file_dialog)
        self.add_action(self.new_file_action)

        self.selected_ingredients = []
        self.current_file = None

        self.settings = self.get_application().get_settings()
        working_filepath = self.settings.get_string('working-filepath')

        if working_filepath:
            self.current_file = Gio.File.new_for_path(working_filepath)
            if self.current_file.query_exists():
                self.window_viewstack.set_visible_child_name("split_view_page")
                self.open_file(self.current_file)
            else:
                print("working file does not exist!") # TODO: change to dialog

        # TODO: watch for changes to file

        self.refresh_main_content()

    @Gtk.Template.Callback()
    def on_split_view_notify_collapsed(self, split_view, user_data):
        if not split_view.get_collapsed():
            print("notify collapsed")
            self.refresh_main_content()

    def purge(self) -> None:
        sections = self.sidebar.get_sections()

        self.sidebar.remove_all()
        self.sidebar.prepend(self.unsorted_food_section)

        # TODO: Don't forget to clear history when this is implemented too

        self.unsorted_food.clear_all()
        self.sidebar.set_selected(0)
        self.sidebar_section_model = SidebarSectionModel(self.sidebar)

    def refresh_can_move_to(self):
        all_meals = self.sidebar.get_items()
        self.move_selected_ingredients_action.set_enabled(len(all_meals) > 1)

    def open_file_dialog(
        self,
        action: Gio.Action,
        parameter: GLib.Variant
    ) -> None:
        # Create new file selection dialog, using "open" mode
        native = Gtk.FileDialog()
        file_filter = Gtk.FileFilter()

        file_filter.add_mime_type('application/json')

        file_filter.set_name(_('JSON Files'))

        native.set_default_filter(file_filter)
        native.set_title(_('Open Meals Data'))

        native.open(self, None, self.on_open_response)

    def on_open_response(
        self,
        dialog: Gtk.FileDialog,
        result: Gio.AsyncResult
    ) -> None:
        file = dialog.open_finish(result)

        if file is not None:
            self.open_file(file)

    def open_file(self, file: Gio.File) -> None:
        file.load_contents_async(None, self.open_file_complete)

    def decode_ingredient(self, data: dict) -> Ingredient:
        print(f"raw data: {data}")
        ymd = data["date"]

        if ymd:
            print(data["date"])
            year, month, day = data["date"]

            date = GLib.DateTime.new_local(
                year,
                month,
                day,
                0,
                0,
                0
            )
        else:
            date = None

        return Ingredient(
            data["name"],
            date,
            self.move_selected_ingredients_action
        )

    def decode_meal(self, data: dict) -> Meal:
        meal = Meal(data["name"], Gio.ListStore(), False)

        for ingredient_json in data["ingredients"]:
            ingredient = self.decode_ingredient(ingredient_json)
            meal.add_ingredient(ingredient)

        return meal

    def open_file_complete(
        self,
        file: Gio.File,
        result: Gio.AsyncResult
    ) -> None:
        contents = file.load_contents_finish(result)

        if not contents[0]:
            path = file.peek_path()
            print(f"Unable to open {path}: {contents[1]}")
            return

        try:
            text = contents[1].decode("utf-8")
        except UnicodeError as err:
            path = file.peek_path()
            print(f"Unable to load the contents of {path}: the file is not encoded with UTF-8")
            return

        # TODO: limit size of json file to be read
        # TODO: error dialog

        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            print(e)

        unsorted = []
        meals = []

        for item_json in data["unsorted"]:
            item = self.decode_ingredient(item_json)
            unsorted.append(item)

        for meal_json in data["meals"]:
            meal = self.decode_meal(meal_json)
            meals.append(meal)

        self.purge()

        for item in unsorted:
            self.unsorted_food.add_ingredient(item)

        for meal in meals:
            self.sidebar_section_model.add_meal(meal)

        self.current_file = file

        self.window_viewstack.set_visible_child_name("split_view_page")
        self.refresh_main_content()
        self.split_view.set_show_content(False)
        self.refresh_can_move_to()

        self.settings.set_string("working-filepath", file.get_path())

    def new_file_dialog(
        self,
        action: Gio.Action,
        parameter: GLib.Variant
    ) -> None:
        native = Gtk.FileDialog()
        file_filter = Gtk.FileFilter()

        file_filter.add_mime_type('application/json')

        file_filter.set_name(_('JSON Files'))

        native.set_default_filter(file_filter)
        native.set_title(_('Save Meals Data'))

        # TRANSLATORS: this is used for the default file name in the 'new meal'
        # file dialog. e.g. 'meals.json'.
        initial_name_base = _("meals")
        initial_name = f"{initial_name_base}.json"
        native.set_initial_name(initial_name)

        native.save(self, None, self.on_new_file_response)

    def on_new_file_response(
        self,
        dialog: Gtk.FileDialog,
        result: Gio.AsyncResult
    ) -> None:
        file = dialog.save_finish(result)

        if file is None:
            return

        self.purge()
        self.current_file = file

        self.window_viewstack.set_visible_child_name("split_view_page")
        self.move_selected_ingredients_action.set_enabled(False)
        self.refresh_main_content()
        self.split_view.set_show_content(False)

        self.settings.set_string("working-filepath", file.get_path())

        self.save_to_file()

    def save_to_file(self) -> None:
        if not self.current_file:
            print("Warning: tried to save without an open file.")
            return

        print("Saving...") # TODO: check for redundancies & remove
        to_save = {"unsorted": [], "meals": []}

        unsorted_items = self.unsorted_food.serialize()["ingredients"]
        to_save["unsorted"] = unsorted_items

        meals = self.sidebar.get_items()
        start_index = self.sidebar_section_model.offset
        for i in range(start_index, len(meals)):
            to_save["meals"].append(meals[i].serialize())

        text = json.dumps(to_save)

        bytes = GLib.Bytes.new(text.encode('utf-8'))

        # Start the asynchronous operation to save the data into the file
        self.current_file.replace_contents_bytes_async(
            bytes,
            None,
            False,
            Gio.FileCreateFlags.NONE,
            None,
            self.save_file_complete
        )

        # TODO: wait for async save finish before window close etc

    def save_file_complete(
        self,
        file: Gio.File,
        result: Gio.AsyncResult
    ) -> None:
        res = file.replace_contents_finish(result)

        if not res:
            print(f"Unable to save {display_name}")

    def show_move_to_dialog(
        self,
        action: Gio.Action,
        parameter: GLib.Variant
    ) -> None:
        self.do_show_move_to_dialog(self.selected_ingredients)

    def do_show_move_to_dialog(self, ingredients: List[Ingredient]) -> None:
        selected_meal = self.sidebar.get_selected_item()
        all_meals = self.sidebar.get_items()

        dialog = MoveToDialog(
            lambda meal: self.do_move(ingredients, meal),
            all_meals,
            selected_meal
        )
        dialog.present(self)

    def do_move(self, ingredients: List[Ingredient], dest_meal: Meal) -> None:
        source_meal = self.sidebar.get_selected_item()

        self.do_remove_ingredients(ingredients)

        dest_old_date = dest_meal.get_bb_date()

        for ingredient in ingredients:
            dest_meal.add_ingredient(ingredient)

        if dest_meal != self.unsorted_food:
            self.sidebar_section_model.update_meal_position(
                dest_meal,
                dest_old_date
            )

        self.sidebar.set_selected(source_meal.get_index())

        self.save_to_file()

    def eat_selected_ingredients(
        self,
        action: Gio.Action,
        parameter: GLib.Variant
    ) -> None:
        self.do_eat_ingredients(self.selected_ingredients)

    def do_remove_ingredients(self, ingredients: List[Ingredient]) -> None:
        selected_meal = self.sidebar.get_selected_item()

        old_date = selected_meal.get_bb_date()

        for ingredient in ingredients:
            selected_meal.remove_ingredient(ingredient)

        if selected_meal != self.unsorted_food:
            self.sidebar_section_model.update_meal_position(
                selected_meal,
                old_date
            )

        self.set_main_page(len(selected_meal.ingredients) == 0)
        self.set_select_mode(False)

    def do_eat_ingredients(self, ingredients: List[Ingredient]) -> None:
        self.do_remove_ingredients(ingredients)
        selected_meal = self.sidebar.get_selected_item()

        if len(ingredients) == 1:
            toast_msg = _("‘{}’ marked as eaten").format(
                ingredients[0].get_title()
            )
        else:
            if selected_meal == self.unsorted_food:
                toast_msg = ngettext("{} item marked as eaten", "{} items marked as eaten", len(ingredients))
            else:
                toast_msg = ngettext("{} ingredient marked as eaten", "{} ingredients marked as eaten", len(ingredients))
            toast_msg = toast_msg.format(len(ingredients))

        toast = Adw.Toast.new(toast_msg)
        toast.set_button_label(_("Undo")) # TODO: make this button do something
        toast.set_priority(Adw.ToastPriority.HIGH)
        self.toast_overlay.add_toast(toast)

        self.save_to_file()

    @Gtk.Template.Callback()
    def enable_select_mode(self, widget: Gtk.Widget, **kwargs) -> None:
        self.set_select_mode(True)
        self.update_selection_counter()

    @Gtk.Template.Callback()
    def disable_select_mode(self, widget: Gtk.Widget, **kwargs) -> None:
        self.set_select_mode(False)

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

        self.selected_ingredients = []

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

            self.save_to_file()

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

        self.save_to_file()

    def eat_meal(self, action: Gio.Action, parameter: GLib.Variant) -> None:
        # TODO: fix cases where sidebar selected desynced from main view
        selected_item = self.sidebar.get_selected_item()
        self.sidebar_section_model.remove_meal(selected_item)

        if not self.split_view.get_collapsed():
            self.refresh_main_content()

        self.split_view.set_show_content(False)

        self.refresh_can_move_to()

        toast = Adw.Toast.new(
            # TRANSLATORS: {} represents a name of a meal.
            _("‘{}’ marked as eaten").format(selected_item.get_title())
        )
        toast.set_button_label(_("Undo")) # TODO: make this button do something
        toast.set_priority(Adw.ToastPriority.HIGH)
        self.toast_overlay.add_toast(toast)

        self.save_to_file()

    def set_main_page(self, is_empty: bool) -> None:
        page_name = "empty-meal-page" if is_empty else "ingredients-page"
        self.content_viewstack.set_visible_child_name(page_name)
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

            self.eat_btn.set_visible(False)

            empty_status_page_title = _("No Food")
            empty_status_page_desc = _("Add snacks and miscellaneous food here")
        else:
            ingredient_search_label = _("Search ingredients")
            # TRANSLATORS: please use U+2026 (…) rather than 3 dots "...", if
            # it's appropriate/applicable to your language.
            add_ingredient_btn_label = _("Add _Ingredient…")

            self.eat_btn.set_visible(True)

            empty_status_page_title = _("Empty Meal") # TODO: change to 'no ingredients'
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

    @Gtk.Template.Callback()
    def on_sidebar_activated(self, index: int, user_data: any) -> None:
        print("sidebar activated")
        self.refresh_main_content()
        self.split_view.set_show_content(True)

    def add_meal_dialog(self, action: Gio.Action, parameter: GLib.Variant) -> None:
        def add_meal(name: str) -> None:
            meal = Meal(name, Gio.ListStore(), False)

            self.sidebar_section_model.add_meal(meal)

            self.move_selected_ingredients_action.set_enabled(True)

            self.save_to_file()

        dialog = NewMealDialog(add_meal)
        dialog.present(self)

    def add_ingredient_dialog(
        self,
        action: Gio.Action,
        parameter: GLib.Variant
    ) -> None:
        def add_ingredient(name: str, date: Optional[GLib.DateTime]) -> None:
            ingredient = Ingredient(
                name,
                date,
                self.move_selected_ingredients_action
            )
            selected_item = self.sidebar.get_selected_item()

            old_date = selected_item.get_bb_date()

            selected_item.add_ingredient(ingredient)
            self.set_main_page(False)

            if selected_item != self.unsorted_food:
                self.sidebar_section_model.update_meal_position(
                    selected_item,
                    old_date
                )

            self.save_to_file()

        dialog = NewIngredientDialog(add_ingredient)
        dialog.present(self)
