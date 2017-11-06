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
from core.components.menu.interface import MenuItem
from core.components.ui import build_text_item
from core.components.ui.graphicbox import GraphicBox
from core.components.ui.layout import Layout, MenuLayout
from core.components.ui.menu import Menu
from core.components.ui.textarea import TextArea
from core.state import State

# Create a logger for optional handling of debug messages.
logger = logging.getLogger(__name__)


def add_menu_items(state, items):
    for key, callback in items:
        label = translator.translate(key).upper()
        image = state.shadow_text(label)
        item = MenuItem(image, label, None, callback)
        state.add(item)


class DebugMenuState(Layout, State):
    """
    Menu for the world state
    """
    draw_borders = False
    background_filename = "gfx/backgrounds/autumn.png"
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

        # add_menu_items(self, menu_items_map)
        self.change_map()

        # load and scale the _background
        background = None
        if self.background_filename:
            background = tools.load_image(self.background_filename)

        # load and scale the menu borders
        border = None
        if self.draw_borders:
            border = tools.load_and_scale(self.borders_filename)

        # set the helper to draw the _background
        self.window = GraphicBox(border, background, (12, 222, 222))
        self.window.rect = pygame.Rect(0, 0, 700, 700)
        self.add_widget(self.window, -1)

    def scan_maps(self):
        """ Scan the resources folder for maps to open

        :return:
        """
        folder = tools.transform_resource_filename('maps')
        return sorted(glob.glob(join(folder, '*.tmx')))

    def process_event(self, event):
        event = super(DebugMenuState, self).process_event(event)
        self.update_filename_list()
        return event

    def update_filename_list(self):
        change_map = self.game.get_state_name('WorldState').change_map
        for path in self.scan_maps():
            # if input is empty, add all the maps
            # otherwise, filter by the input string
            map_name = basename(path)[:-4]
            input = self.key_input.string_input
            if input == '' or input in map_name.upper():
                item = build_text_item(map_name, partial(change_map, path))
                self.filenames.add_widget(item)

        self.filenames.check_bounds()


    def change_map(self):
        self.filenames = MenuLayout()
        self.filenames.line_spacing = tools.scale(7)
        self.filenames.rect = tools.scaled_rect(115, 8, 150, 130)
        self.add_widget(self.filenames)

        # area where the input will be shown
        font = tools.load_default_font()

        self.font_color = (0, 0, 0)
        self.text_area = TextArea(font, self.font_color, (96, 96, 96))
        self.text_area.animated = False
        self.text_area.rect = tools.scaled_rect(20, 23, 80, 100)
        self.text_area.text = self.empty_box
        self.add_widget(self.text_area)

        self.key_input = Menu()
        self.key_input.menu_items.columns = len(self.chars) // 6
        self.key_input.rect = tools.scaled_rect(7, 40, 100, 100)
        self.add_widget(self.key_input)

        add_widget = self.key_input.menu_items.add_widget
        for char in self.chars:
            # add individual character
            item = build_text_item(char, partial(self.key_input.add_input_buffer, char))
            add_widget(item)

        # backspace key
        item = build_text_item("<=", self.key_input.backspace)
        add_widget(item)

        # button to confirm the input and close the dialog
        item = build_text_item("END", self.confirm())
        add_widget(item)

    def confirm(self):
        pass

    def reload_map(self):
        pass

    def save_state(self):
        pass

    def load_state(self):
        pass
