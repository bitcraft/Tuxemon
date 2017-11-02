from __future__ import division

import logging
from functools import partial

from os.path import join, basename
import glob
import pygame

from core import prepare
from core.components.locale import translator
from core.components.menu.interface import MenuItem
from core.components.menu.menu import Menu
from core.tools import open_dialog, transform_resource_filename

# Create a logger for optional handling of debug messages.
logger = logging.getLogger(__name__)


def adapter(name, *args):
    from collections import namedtuple
    nt = namedtuple(name, "parameters")

    def func(*args):
        return nt(args)

    return func


def add_menu_items(state, items):
    for key, callback in items:
        label = translator.translate(key).upper()
        image = state.shadow_text(label)
        item = MenuItem(image, label, None, callback)
        state.add(item)


class DebugMenuState(Menu):
    """
    Menu for the world state
    """
    shrink_to_items = True  # this menu will shrink, but size is adjusted when opened
    animate_contents = True

    def startup(self, *args, **kwargs):
        super(DebugMenuState, self).startup(*args, **kwargs)

        def change_state(state, **kwargs):
            return partial(self.game.replace_state, state, **kwargs)

        def exit_game():
            self.game.event_engine.execute_action("quit")

        def not_implemented_dialog():
            open_dialog(self.game, [translator.translate('not_implemented')])

        # Main Menu - Allows users to open the main menu in game.
        menu_items_map = [
            ('debug_change_map', self.change_map),
            ('debug_reload_map', self.reload_map),
            ('debug_save_state', self.save_state),
            ('debug_load_state', self.load_state),
            ('debug_show_state', not_implemented_dialog),
        ]

        add_menu_items(self, menu_items_map)

    def change_map(self):
        # get maps available
        folder = transform_resource_filename('maps')
        change_map = self.game.get_state_name('WorldState').change_map
        paths = sorted(glob.glob(join(folder, '*.tmx')))
        for path in paths:
            map_name = basename(path)[:-4]
            self.build_item(basename(map_name), partial(change_map, path))

    def reload_map(self):
        pass

    def save_state(self):
        pass

    def load_state(self):
        pass