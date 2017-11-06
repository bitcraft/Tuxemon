# -*- coding: utf-8 -*-
#
# Tuxemon
# Copyright (C) 2014, William Edwards <shadowapex@gmail.com>,
#                     Benjamin Bean <superman2k5@gmail.com>
#
# This file is part of Tuxemon.
#
# Tuxemon is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Tuxemon is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Tuxemon.  If not, see <http://www.gnu.org/licenses/>.
#
# Contributor(s):
#
# Leif Theden <leif.theden@gmail.com>
#
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
            tools.open_dialog(self.game, [translator.translate('not_implemented')])

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
        folder = tools.transform_resource_filename('maps')
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

        # backspace key
        self.menu_items.add(MenuItem(self.shadow_text("<="), None, None, self.backspace))

        # button to confirm the input and close the dialog
        self.menu_items.add(MenuItem(self.shadow_text("END"), None, None, self.confirm))

    def confirm(self):
        pass

    def reload_map(self):
        pass

    def save_state(self):
        pass

    def load_state(self):
        pass
