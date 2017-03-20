#!/usr/bin/python
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
from __future__ import absolute_import

from functools import partial

from core import tools
from core.components.ui.menu import Menu
from core.components.menu.interface import MenuItem
from core.components.ui.textarea import TextArea
from core.components.ui.font import shadow_text
from core.components.game_event import input_event

import pygame


class InputMenu(Menu):
    background = None
    draw_borders = False
    touch_aware = True

    chars = u"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890.-!"
    alphabet_length = 26

    def startup(self, *items, **kwargs):
        """

        Accepted Keyword Arguments:
            prompt: String used to let user know what value is being inputted (ie "Name?", "IP Address?")

        :param items:
        :param kwargs:
        :return:
        """
        super(InputMenu, self).startup(*items, **kwargs)
        self.input_string = ""

        # area where the input will be shown
        self.text_area = TextArea(self.font, self.font_color, (96, 96, 96))
        self.text_area.animated = False
        self.text_area.rect = pygame.Rect(tools.scale_sequence([90, 30, 80, 100]))
        self.sprites.add(self.text_area)

        # prompt
        self.prompt = TextArea(self.font, self.font_color, (96, 96, 96))
        self.prompt.animated = False
        self.prompt.rect = pygame.Rect(tools.scale_sequence([50, 20, 80, 100]))
        self.sprites.add(self.prompt)

        self.prompt.text = kwargs.get("prompt", "")

    def calc_internal_rect(self):
        w = self.rect.width - self.rect.width * .8
        h = self.rect.height - self.rect.height * .5
        rect = self.rect.inflate(-w, -h)
        rect.top = self.rect.centery * .7
        return rect

    def initialize_items(self):
        self.menu_items.columns = self.alphabet_length // 2

        st = partial(shadow_text(self.font))

        # add the keys
        for char in self.chars:
            yield MenuItem(self.font, st(char), None, None, partial(self.add_input_char, char))

        # backspace key
        yield MenuItem(st("<="), None, None, self.backspace)

        # button to confirm the input and close the dialog
        yield MenuItem(st("END"), None, None, self.confirm)

    def process_event(self, event):
        super(InputMenu, self).process_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.backspace()

            char = event.unicode
            if char in self.chars:
                self.add_input_char(char)

    def backspace(self):
        self.input_string = self.input_string[:-1]
        self.update_text_area()

    def add_input_char(self, char):
        self.input_string += char
        self.update_text_area()

    def update_text_area(self):
        self.text_area.text = self.input_string

    def confirm(self):
        """ Confirm the input

        This is called when user selects "End".
        An input_event will be emitted with inputted string

        :return: None
        """
        input_event(self.input_string)
        self.game.pop_state(self)
