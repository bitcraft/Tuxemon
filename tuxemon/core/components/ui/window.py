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
from __future__ import division
from __future__ import print_function

import math
from functools import partial

import pygame

from core import state, prepare, tools
from core.components.animation import remove_animations_of
from core.components.menu.interface import MenuCursor, MenuItem
from core.components.ui.draw import GraphicBox
from core.components.ui.layout import RelativeLayout, GridLayout
from core.components.ui.text import TextArea


class Window(state.State):
    """ Graphical window
    A window is a type of state.  Top windows will have input focus.

    Windows...:
      * are typically decorated and contain text or a menu
      * may cover the entire screen
      * do not need decoration
      * graphical elements in the window are drawn relative to the upper left corner
    """

    # Window Defaults
    escape_key_exits = True           # escape key closes window
    shrink_to_items = False           # fit the border to contents
    background_filename = None        # File to load for image background
    background_color = 248, 248, 248  # The window's background color
    background = None                 # filename for image used to draw the background
    draw_borders = True
    borders_filename = "gfx/dialog-borders01.png"

    def startup(self, *args, **kwargs):
        self.rect = self.rect.copy()  # do not remove!

    def load_graphics(self):
        """ Loads all the graphical elements of the window
        """
        if not self.transparent:
            # load and scale the _background
            background = None
            if self.background_filename:
                background = tools.load_image(self.background_filename)

            # load and scale the menu borders
            border = None
            if self.draw_borders:
                border = tools.load_and_scale(self.borders_filename)

            # set the helper to draw the background and border
            self.window = GraphicBox(border, background, self.background_color)
