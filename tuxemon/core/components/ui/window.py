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

import pygame as pg

from core import prepare, state, tools
from core.components.ui.graphicbox import GraphicBox
from core.components.ui.widget import Widget


class Window(Widget):
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
    transparent = False
    force_draw = True

    def __init__(self):
        self.children = list()
        self.parent = None
        self.disabled = False
        self.state = "closed"         # closed, opening, normal, disabled, closing
        super(Window, self).__init__()

        self._anchors = dict()        # used to position the menu/state
        self.rect = self.rect.copy()  # do not remove!

        self.load_graphics()

    def process_event(self, event):
        """ Process pygame input events

        The menu cursor is handled here, as well as the ESC and ENTER keys.

        This will also toggle the 'in_focus' of the menu item

        :type event: pg.Event
        :returns: None
        """
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE and self.escape_key_exits:
                self.close()
                return None

        return super(Window, self).process_event(event)

    def load_graphics(self):
        """ Loads all the graphical elements of the window
        """
        if not self.transparent:
            # load and scale the background
            background = None
            if self.background_filename:
                background = tools.load_image(self.background_filename)

            # load and scale the menu borders
            border = None
            if self.draw_borders:
                border = tools.load_and_scale(prepare.DEFAULT_BORDERS)

            # set the helper to draw the background and border
            gb = GraphicBox(border, background, self.background_color)
            gb.rect = self.rect.copy()
            self.add_widget(gb)

    def fit_border(self):
        """ Resize the window border to fit the contents of the menu

        :return:
        """
        # get bounding box of menu items and the cursor
        center = self.rect.center
        rect1 = self.menu_items.calc_bounding_rect()
        rect2 = self.menu_sprites.calc_bounding_rect()
        rect1 = rect1.union(rect2)

        # expand the bounding box by the border and some padding
        # TODO: do not hardcode these values
        # border is 12, padding is the rest
        rect1.width += tools.scale(18)
        rect1.height += tools.scale(19)
        rect1.topleft = 0, 0

        # set our rect and adjust the centers to match
        self.rect = rect1
        self.rect.center = center

        # move the bounding box taking account the anchors
        self.position_rect()

    def calc_internal_rect(self):
        """ Calculate the area inside the borders, if any.
        If no borders are present, a copy of the window rect will be returned

        :returns: Rect representing space inside borders, if any
        :rtype: pygame.Rect
        """
        # return self._renderer.calc_inner_rect(self.rect)
        return self.rect.copy()

    def position_rect(self):
        """ Reposition rect taking in account the anchors
        """
        for attribute, value in self._anchors.items():
            setattr(self.rect, attribute, value)

    def anchor(self, attribute, value):
        """ Set an anchor for the menu window

        You can pass any string value that is used in a pygame rect,
        for example: "center", "topleft", and "right".

        When changes are made to the window or it is being opened
        or sized, then these values passed as anchors will override
        others.  The order of which each anchor is applied is not
        necessarily going to match the order they were set, as the
        implementation relies on a dictionary.

        Take care to make sure values do not overlap.

        :param attribute:
        :param value:
        :return:
        """
        if value is None:
            del self._anchors[attribute]
        else:
            self._anchors[attribute] = value

    def on_open(self):
        """ Hook is called after opening animation has finished

        :return:
        """
        pass

    def resume(self):
        if self.state == "closed":
            def show_items():
                self.state = "normal"
                self._show_contents = True
                # self.on_menu_selection_change()
                self.on_open()

            self.state = "opening"
            # self.reload_items()
            self.refresh_layout()

            ani = self.animate_open()
            # if ani:
            #     if self.animate_contents:
            #         self._show_contents = True
            #         # TODO: make some "dirty" or invalidate layout API
            #         # this will make sure items are arranged as menu opens
            #         ani.update_callback = partial(setattr, self.menu_items, "_needs_arrange", True)
            #     ani.callback = show_items
            # else:
            #     self.state = "normal"
            #     show_items()

            # elif self.state == "normal":
            #     self.reload_items()
            #     self.refresh_layout()
            #     self.on_menu_selection_change()

    def close(self):
        if self.state in ["normal", "opening"]:
            self.state = "closing"
            ani = self.animate_close()
            if ani:
                ani.callback = self.game.pop_state
            else:
                self.game.pop_state()

    def animate_open(self):
        """ Called when menu is going to open

        Menu will not receive input during the animation
        Menu will only play this animation once

        Must return either an Animation or Task to attach callback
        Only modify state of the menu Rect
        Do not change important state attributes

        :returns: Animation or Task
        :rtype: core.components.animation.Animation
        """
        return None

    def animate_close(self):
        """ Called when menu is going to open

        Menu will not receive input during the animation
        Menu will play animation only once
        Menu will be popped after animation finished

        Must return either an Animation or Task to attach callback
        Only modify state of the menu Rect
        Do not change important state attributes

        :returns: Animation or Task
        :rtype: core.components.animation.Animation
        """
        return None
