# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import glob
import logging
from functools import partial
from os.path import join, basename

import pygame

from core import tools
from core.components.locale import translator
from core.components.menu import Menu
from core.components.menu.interface import MenuItem
from core.components.sprite import VisualSpriteList
from core.components.ui.text import TextArea
from core.tools import open_dialog, transform_resource_filename

# Create a logger for optional handling of debug messages.
logger = logging.getLogger(__name__)


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
    # shrink_to_items = True  # this menu will shrink, but size is adjusted when opened
    animate_contents = True
    chars = u"ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890.-!"
    alphabet_length = 26

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

        self.input_string = ""

        # area where the input will be shown
        self.text_area = TextArea(self.font, self.font_color, (96, 96, 96))
        self.text_area.animated = False
        self.text_area.rect = pygame.Rect(tools.scale_sequence([90, 30, 80, 100]))
        self.sprites.add(self.text_area)

        self.filenames = VisualSpriteList(parent=self.calc_filenames_rect)
        self.filenames.columns = 1

        # add_menu_items(self, menu_items_map)
        self.change_map()
        self.update_text_area()

    def process_event(self, event):
        super(DebugMenuState, self).process_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.backspace()
                return

            char = event.unicode.upper()
            if char in self.chars:
                self.add_input_char(char)
                return

    def backspace(self):
        self.input_string = self.input_string[:-1]
        self.update_text_area()

    def add_input_char(self, char):
        self.input_string += char
        self.update_text_area()

    def draw(self, surface):
        super(DebugMenuState, self).draw(surface)

        self.filenames.draw(surface)

    def update_text_area(self):
        self.text_area.text = self.input_string
        print(self.input_string)
        folder = transform_resource_filename('maps')
        change_map = self.game.get_state_name('WorldState').change_map
        paths = sorted(glob.glob(join(folder, '*.tmx')))

        self.filenames.empty()

        for path in paths:
            if self.input_string == '':
                map_name = basename(path)[:-4]
                image = self.shadow_text(map_name)
                item = MenuItem(image, path, None, None)
                self.filenames.add(item)

            elif self.input_string in path.upper():
                map_name = basename(path)[:-4]
                image = self.shadow_text(map_name)
                item = MenuItem(image, path, None, None)
                self.filenames.add(item)

    def calc_internal_rect(self):
        w = self.rect.width - self.rect.width * .9
        h = 10
        rect = self.rect.inflate(-w, -h)
        rect.top = self.rect.centery * .1
        return rect

    def calc_filenames_rect(self):
        w = self.rect.width - self.rect.width * .8
        h = self.rect.height * .6
        rect = self.rect.inflate(-w, -h)
        rect.top = self.rect.top + (h * .4)
        return rect

    def change_map(self):
        self.menu_items.columns = len(self.chars)
        # get maps available
        folder = transform_resource_filename('maps')
        change_map = self.game.get_state_name('WorldState').change_map
        paths = sorted(glob.glob(join(folder, '*.tmx')))

        self.menu_items.empty()

        # add the keys
        for char in self.chars:
            print(char)
            self.build_item(char, lambda x: x)

        pass
        # for path in paths:
        #     map_name = basename(path)[:-4]
        #     self.build_item(basename(map_name), partial(change_map, path))

    def reload_map(self):
        pass

    def save_state(self):
        pass

    def load_state(self):
        pass
