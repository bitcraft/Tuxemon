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
from itertools import product

import pygame as pg

from core.components.ui.widget import Widget


class GraphicBox(Widget):
    """ Generic class for drawing graphical boxes

    Draws a border and can fill in the box with a _color from the border file,
    an external file, or a solid _color.

    box = GraphicBox('border.png')
    box.draw(surface, rect)

    The border graphic must contain 9 tiles laid out in a box.
    """

    def __init__(self, border=None, background=None, color=None, fill_tiles=False):
        """

        :param border: Image used to draw border
        :param background: Image to be used as background
        :param color: Color to fill background
        :param fill_tiles: If True, use tile from center of border image to fill
        """
        super(GraphicBox, self).__init__()
        self._background = background
        self._color = color
        self._fill_tiles = fill_tiles
        self._tiles = list()
        self._tile_size = 0, 0
        self._rect = pg.Rect(0, 0, 0, 0)
        if border:
            self.set_border(border)

    def calc_inner_rect(self, rect):
        """ Return rect representing area inside the borders

        :param rect:
        :return:
        """
        if self._tiles:
            tw, th = self._tile_size
            return rect.inflate(- tw * 2, -th * 2)
        else:
            return rect

    def set_border(self, image):
        iw, ih = image.get_size()
        tw, th = iw // 3, ih // 3
        self._tile_size = tw, th
        self._tiles = [image.subsurface((x, y, tw, th))
                       for x, y in product(range(0, iw, tw), range(0, ih, th))]

    def draw(self, surface):
        self.update_rect_from_parent()

        rect = self.rect
        inner = self.calc_inner_rect(rect)

        # fill center with a _background surface
        if self._background:
            surface.blit(pg.transform.scale(self._background, inner.size), inner)

        # fill center with solid _color
        elif self._color:
            surface.fill(self._color, inner)

        # fill center with tiles from the border file
        elif self._fill_tiles:
            tw, th = self._tile_size
            p = product(range(inner.left, inner.right, tw),
                        range(inner.top, inner.bottom, th))
            [surface.blit(self._tiles[4], pos) for pos in p]

        # draw the border
        if self._tiles:
            surface_blit = surface.blit
            tile_nw, tile_w, tile_sw, tile_n, tile_c, tile_s, tile_ne, tile_e, tile_se = self._tiles
            left, top = rect.topleft
            tw, th = self._tile_size

            # draw top and bottom tiles
            for x in range(inner.left, inner.right, tw):
                if x + tw >= inner.right:
                    area = 0, 0, tw - (x + tw - inner.right), th
                else:
                    area = None
                surface_blit(tile_n, (x, top), area)
                surface_blit(tile_s, (x, inner.bottom), area)

            # draw left and right tiles
            for y in range(inner.top, inner.bottom, th):
                if y + th >= inner.bottom:
                    area = 0, 0, tw, th - (y + th - inner.bottom)
                else:
                    area = None
                surface_blit(tile_w, (left, y), area)
                surface_blit(tile_e, (inner.right, y), area)

            # draw corners
            surface_blit(tile_nw, (left, top))
            surface_blit(tile_sw, (left, inner.bottom))
            surface_blit(tile_ne, (inner.right, top))
            surface_blit(tile_se, (inner.right, inner.bottom))
