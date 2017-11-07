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
from core.state import State
from core.components.ui import build_text_item
from core.components.ui.graphicbox import GraphicBox
from core.components.ui.layout import Layout, GridLayout
from core.components.ui.textarea import TextArea
from core.components.ui.textinput import TextInput

# Create a logger for optional handling of debug messages.
from core.tools import scale

logger = logging.getLogger(__name__)


class DebugMenuState(Layout, State):
    """
    Menu for the world state
    """
    draw_borders = False
    background_filename = "gfx/backgrounds/autumn.png"
    animate_contents = True
    empty_box = "< map name >"

    def startup(self, *args, **kwargs):
        super(DebugMenuState, self).startup(*args, **kwargs)

        # load and scale the background
        background = None
        if self.background_filename:
            background = tools.load_image(self.background_filename)

        # load and scale the menu borders
        border = None
        if self.draw_borders:
            border = tools.load_and_scale(self.borders_filename)

        # set the helper to draw the background
        self.window = GraphicBox(border, background, (12, 222, 222))
        self.window.rect = pygame.Rect(0, 0, 700, 700)
        self.add_widget(self.window)

        # widget to show map names
        self.filenames = GridLayout()
        self.filenames.line_spacing = scale(7)
        self.filenames.rect2 = tools.scaled_rect(115, 8, 150, 130)
        self.add_widget(self.filenames)

        # text widget to show input
        font = tools.load_default_font()
        self.font_color = (255, 255, 255)
        self.text_area = TextArea(font, self.font_color, (96, 96, 96))
        self.text_area.animated = False
        self.text_area.rect = tools.scaled_rect(20, 23, 80, 100)
        self.text_area.text = self.empty_box
        self.add_widget(self.text_area)

        # widget for getting input
        self.key_input = TextInput()
        self.key_input.rect2 = tools.scaled_rect(7, 40, 100, 100)
        self.add_widget(self.key_input)

        self.update_filename_list()

    def scan_maps(self):
        """ Scan the resources folder for maps.  Return a sorted list of paths.

        :return:
        """
        folder = tools.transform_resource_filename('maps')
        return sorted(glob.glob(join(folder, '*.tmx')))

    def update_filename_list(self):
        change_map = self.game.get_state_name('WorldState').change_map
        self.filenames.clear_widgets()
        for path in self.scan_maps():
            map_name = basename(path)[:-4]
            text = self.key_input.string_input
            # if input is empty, add all the maps. otherwise filter by the input string
            if text == '' or text in map_name.upper():
                item = build_text_item(map_name, partial(change_map, path))
                self.filenames.add_widget(item)
