# main.py
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

import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Adw
from .window import ScrummyWindow
from scrummy import APPLICATION_ID, PREFIX, VERSION


# TODO: Move flatpak JSON file to build-aux 
# TODO: allow meal to be opened from file manager
# TODO: ctrl+w should close window?
# TODO: plus icons to add buttons

class ScrummyApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(application_id=APPLICATION_ID,
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
                         resource_base_path=PREFIX)
        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('preferences', self.on_preferences_action)

        self.settings = Gio.Settings(schema_id=self.get_application_id())

        self.set_accels_for_action('win.open_file', ['<Ctrl>o'])
        self.set_accels_for_action('win.new_file', ['<Ctrl>n'])

    def get_settings(self) -> Gio.Settings:
        """ Get the application's settings """
        return self.settings

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        win = self.props.active_window
        if not win:
            win = ScrummyWindow(application=self)
            if self.get_application_id() == "io.github.wartybix.Scrummy.Devel":
                win.get_style_context().add_class("devel")

        win.present()

    def on_about_action(self, *args):
        # TODO: Update

        print(APPLICATION_ID)

        """Callback for the app.about action."""
        # about = Adw.AboutDialog(application_name='scrummy',
        #                         application_icon='@APPLICATION_ID@',
        #                         developer_name='Wartybix',
        #                         version='0.1.0',
        #                         developers=['Wartybix'],
        #                         copyright='© 2025 Wartybix')

        about = Adw.AboutDialog.new_from_appdata(
            f"{PREFIX}/{APPLICATION_ID}.metainfo.xml", VERSION
        )

        about.set_version(VERSION)

        about.set_developers(['Wartybix https://github.com/Wartybix/'])

        about.set_copyright('© 2025 Wartybix')

        # Translators: Replace "translator-credits" with your name/username, and optionally an email or URL.
        about.set_translator_credits(_('translator-credits'))

        about.add_other_app(
            "io.github.wartybix.Constrict",
            _("Constrict"),
            _("Compress videos to target sizes")
        )

        about.present(self.props.active_window)

    def on_preferences_action(self, widget, _):
        """Callback for the app.preferences action."""
        print('app.preferences action activated')

    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


def main(version):
    """The application's entry point."""
    app = ScrummyApplication()
    return app.run(sys.argv)
