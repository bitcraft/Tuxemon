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
from pygame.transform import rotozoom
from pygame.transform import scale

from core.components.pyganim import PygAnimation
from core.components.ui.widget import Widget


class Sprite(Widget):
    """ Tuxemon Sprite
    """
    dirty = False
    rect = pg.Rect(0, 0, 0, 0)

    def __init__(self, *args, **kwargs):
        super(Sprite, self).__init__(*args, **kwargs)
        self.visible = True
        self._rotation = 0
        self._image = None
        self._original_image = None
        self._width = 0
        self._height = 0
        self._needs_rescale = False
        self._needs_update = False

    def _draw(self, surface, rect=None):
        """ Draw the sprite to the surface

        This operation does not scale the sprite, so it may exceed
        the size of the area passed.

        :param surface: Surface to be drawn on
        :param rect: Area to contain the sprite
        :return: Area of the surface that was modified
        :rtype: pygame.rect.Rect
        """
        # should draw to surface without generating a cached copy
        if rect is None:
            rect = surface.get_rect()
        return self.__draw(surface, rect)

    def __draw(self, surface, rect):
        self.update_image()
        return surface.blit(self._image, rect)

    @property
    def image(self):
        # should always be a cached copy
        if self._needs_update:
            self.update_image()
            self._needs_update = False
            self._needs_rescale = False
        return self._image

    @image.setter
    def image(self, image):
        if image is None:
            self._original_image = None
            return

        if hasattr(self, 'rect'):
            self.rect.size = image.get_size()
        else:
            self.rect = image.get_rect()
        self._original_image = image
        self._needs_update = True

    def update_image(self):
        if self._needs_rescale:
            w = self.rect.width if self._width is None else self._width
            h = self.rect.height if self._height is None else self._height
            image = scale(self._original_image, (w, h))
            center = self.rect.center
            self.rect.size = w, h
            self.rect.center = center
        else:
            image = self._original_image

        if self._rotation:
            image = rotozoom(image, self._rotation, 1)
            rect = image.get_rect(center=self.rect.center)
            self.rect.size = rect.size
            self.rect.center = rect.center

        self._width, self._height = self.rect.size
        self._image = image

    # width and height are API that may not stay
    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width):
        width = int(round(width, 0))
        if not width == self._width:
            self._width = width
            self._needs_rescale = True
            self._needs_update = True

    # width and height are API that may not stay
    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height):
        height = int(round(height, 0))
        if not height == self._height:
            self._height = height
            self._needs_rescale = True
            self._needs_update = True

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        value = int(round(value, 0)) % 360
        if not value == self._rotation:
            self._rotation = value
            self._needs_update = True


class SpriteGroup(pg.sprite.LayeredUpdates):
    """ Sane variation of a pygame sprite group

    Features:
    * Supports Layers
    * Supports Index / Slice
    * Supports skipping sprites without an image
    * Supports sprites with visible flag
    * Get bounding rect of all children

    Variations from standard group:
    * SpriteGroup.add no longer accepts a sequence, use SpriteGroup.extend
    """
    _init_rect = pg.Rect(0, 0, 0, 0)

    def __init__(self, *args, **kwargs):
        self._spritelayers = dict()
        self._spritelist = list()
        pg.sprite.AbstractGroup.__init__(self)
        self._default_layer = kwargs.get('default_layer', 0)

    def __nonzero__(self):
        return bool(self._spritelist)

    def __getitem__(self, item):
        # patch in indexing / slicing support
        return self._spritelist.__getitem__(item)

    def draw(self, surface):
        spritedict = self.spritedict
        surface_blit = surface.blit
        dirty = self.lostsprites
        self.lostsprites = []
        dirty_append = dirty.append

        for s in self.sprites():
            if getattr(s, "image", None) is None:
                continue

            if not getattr(s, 'visible', True):
                continue

            if isinstance(s.image, PygAnimation):
                s.image.blit(surface, s.rect)
                continue

            r = spritedict[s]
            newrect = surface_blit(s.image, s.rect)
            if r:
                if newrect.colliderect(r):
                    dirty_append(newrect.union(r))
                else:
                    dirty_append(newrect)
                    dirty_append(r)
            else:
                dirty_append(newrect)
            spritedict[s] = newrect
        return dirty

    def extend(self, sprites, **kwargs):
        """ Add a sequence of sprites to the SpriteGroup

        :param sprites: Sequence (list, set, etc)
        :param kwargs:
        :returns: None
        """
        if '_index' in kwargs.keys():
            raise KeyError
        for index, sprite in enumerate(sprites):
            kwargs['_index'] = index
            self.add(sprite, **kwargs)

    def add(self, sprite, **kwargs):
        """ Add a sprite to group.  do not pass a sequence or iterator

        LayeredUpdates.add(*sprites, **kwargs): return None
        If the sprite you add has an attribute _layer, then that layer will be
        used. If **kwarg contains 'layer', then the passed sprites will be
        added to that layer (overriding the sprite._layer attribute). If
        neither the sprite nor **kwarg has a 'layer', then the default layer is
        used to add the sprites.
        """
        layer = kwargs.get('layer')
        if isinstance(sprite, pg.sprite.Sprite):
            if not self.has_internal(sprite):
                self.add_internal(sprite, layer)
                sprite.add_internal(self)
        else:
            pass
            # raise TypeError
