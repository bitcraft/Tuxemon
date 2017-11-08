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
"""
notes:

relative layout
widgets will expand by default
their topleft will come from rect2
rect2 is not calculated, it can be a rect or None
if None, topleft will be the inner of parent
if set, it will be the offset for drawing

layouts and programmers can set rect2
if not set, widget will expand into parent
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import glob
import logging
from functools import partial
from os.path import join, basename

from core import tools
from core.components.ui import build_text_item
from core.components.ui.graphicbox import GraphicBox
from core.components.ui.layout import Layout
from core.components.ui.menu import Menu
from core.components.ui.textarea import TextArea
from core.components.ui.textinput import TextInput
from core.state import State
# Create a logger for optional handling of debug messages.
from core.tools import scale

logger = logging.getLogger(__name__)


class DebugMenuState(Layout, State):
    """
    Menu for the world state
    """
    borders_filename = "gfx/dialog-borders01.png"
    background_filename = "gfx/backgrounds/autumn.png"
    animate_contents = True
    empty_box = "< map name >"

    def startup(self, *args, **kwargs):
        super(DebugMenuState, self).startup(*args, **kwargs)

        # load and scale the background/borders
        background = tools.load_image(self.background_filename)
        # border = tools.load_and_scale(self.borders_filename)

        # set the widget to draw the background
        window = GraphicBox(None, background, (12, 222, 222))
        self.add_widget(window)

        # widget for getting input
        self.key_input = TextInput()
        self.key_input.offset = tools.scaled_rect(7, 40, 100, 100)
        self.add_widget(self.key_input)

        # text widget to show input
        font = tools.load_default_font()
        font_color = (255, 255, 255)
        self.text_area = TextArea(font, font_color, (96, 96, 96))
        self.text_area.animated = False
        self.text_area.rect = tools.scaled_rect(20, 23, 80, 100)
        self.text_area.text = self.empty_box
        self.add_widget(self.text_area)

        # widget to show map names
        self.filenames = Menu()
        self.filenames.menu_items.line_spacing = scale(30)
        self.filenames.offset = tools.scaled_rect(115, 8, 150, 130)
        self.update_filename_list()
        self.add_widget(self.filenames)

        self.children.remove(self.filenames)
        self.children.insert(1, self.filenames)

    def scan_maps(self):
        """ Scan the resources folder for maps.  Return a sorted list of paths.

        :return:
        """
        folder = tools.transform_resource_filename('maps')
        return sorted(glob.glob(join(folder, '*.tmx')))

    def update_filename_list(self):
        self.filenames.menu_items.clear_widgets()
        change_map = self.game.get_state_name('WorldState').change_map
        add_widget = self.filenames.menu_items.add_widget
        for path in self.scan_maps():
            map_name = basename(path)[:-4]
            text = self.key_input.string_input
            if text == '' or text in map_name.upper():
                item = build_text_item(map_name, partial(change_map, path))
                add_widget(item)
