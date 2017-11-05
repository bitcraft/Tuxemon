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
    chars = u"ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    animate_contents = True
    empty_box = "< map name >"

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
        self.text_area.rect = tools.scaled_rect(20, 23, 80, 100)
        self.text_area.text = self.empty_box
        self.sprites.add(self.text_area)

        self.filenames = VisualSpriteList(parent=self.calc_filenames_rect)
        self.filenames.columns = 1
        self.filenames.line_spacing = tools.scale(7)

        # add_menu_items(self, menu_items_map)
        self.change_map()
        self.update_text_area()

    def process_event(self, event):
        super(DebugMenuState, self).process_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.backspace()
                return

            if event.key == pygame.K_DOWN:
                pass

            char = event.unicode.upper()
            if char in self.chars:
                for index, item in enumerate(self.menu_items):
                    if char == item.label:
                        self.change_selection(index)
                        self.add_input_char(char)
                        return
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
        # surface.fill((10, 0, 0), self.filenames.rect)

    def scan_maps(self):
        """ Scan the resources folder for maps to open

        :return:
        """
        folder = transform_resource_filename('maps')
        return sorted(glob.glob(join(folder, '*.tmx')))

    def update_text_area(self):
        if self.input_string == '':
            self.text_area.text = self.empty_box
        else:
            self.text_area.text = self.input_string
        self.update_filename_list()

    def update_filename_list(self):
        self.filenames.empty()
        change_map = self.game.get_state_name('WorldState').change_map
        for path in self.scan_maps():
            # if input is empty, add all the maps
            # otherwise, filter by the input string
            map_name = basename(path)[:-4]
            if self.input_string == '' or self.input_string in map_name.upper():
                image = self.shadow_text(map_name)
                item = MenuItem(image, path, None, partial(change_map, path))
                self.filenames.add(item)

    def calc_internal_rect(self):
        """ Character input area

        :return:
        """
        return tools.scaled_rect(7, 40, 100, 100)

    def calc_filenames_rect(self):
        """ Filenames area

        :return:
        """
        return tools.scaled_rect(115, 8, 150, 130)

    def change_map(self):
        self.menu_items.columns = len(self.chars) // 6
        self.menu_items.empty()
        for char in self.chars:
            self.build_item(char, partial(self.add_input_char, char))

    def reload_map(self):
        pass

    def save_state(self):
        pass

    def load_state(self):
        pass
