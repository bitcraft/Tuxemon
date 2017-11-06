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
# William Edwards <shadowapex@gmail.com>
# Leif Theden <leif.theden@gmail.com>
#
#
from __future__ import division

import pygame

import core.components.ui.font
from core.components.ui.widget import Widget


class TextArea(Widget):
    """ Area of the screen that can draw text
    """
    animated = True

    def __init__(self, font, font_color, bg=(192, 192, 192)):
        super(TextArea, self).__init__()
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.drawing_text = False
        self.font = font
        self.font_color = font_color
        self.font_bg = bg
        self._rendered_text = None
        self._text_rect = None
        self._image = None
        self._text = None

    def __iter__(self):
        return self

    def __len__(self):
        return len(self._text)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        if value != self._text:
            self._text = value

        if self.animated:
            self._start_text_animation()
        else:
            self.image = core.components.ui.font.shadow_text(self.font, self.font_color, self.font_bg, self._text)

    def __next__(self):
        if self.animated:
            try:
                dirty, dest, scrap = next(self._iter)
                self._image.fill((0, 0, 0, 0), dirty)
                self._image.blit(scrap, dest)
            except StopIteration:
                self.drawing_text = False
                raise
        else:
            raise StopIteration

    next = __next__

    def _start_text_animation(self):
        self.drawing_text = True
        self.image = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        self._iter = core.components.ui.font.iter_render_text(self._text, self.font, self.font_color,
                                                              self.font_bg, self.image.get_rect())
