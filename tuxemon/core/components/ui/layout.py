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

import math

import pygame

from core.components.ui.widget import Widget


class Layout(Widget):
    """
    Layouts contain widgets and position them.
    """
    pass


class MenuLayout(Layout):
    """
    Sprite Group to be used for menus.

    Includes functions for moving a cursor around the screen
    """
    orientation = 'horizontal'
    columns = 1

    def determine_cursor_movement(self, *args):
        """ Given an event, determine a new selected item offset

        You must pass the currently selected object
        The return value will be the newly selected object index

        :param index: Index of the item in the list
        :param event: pygame.Event
        :returns: New menu item offset
        """
        if self.orientation == 'horizontal':
            return self._determine_cursor_movement_horizontal(*args)
        else:
            raise RuntimeError

    def _determine_cursor_movement_horizontal(self, index, event):
        """ Given an event, determine a new selected item offset

        You must pass the currently selected object
        The return value will be the newly selected object index

        This is for menus that are laid out horizontally first:
           [1] [2] [3]
           [4] [5]

        Works pretty well for most menus, but large grids may require
        handling them differently.

        :param index: Index of the item in the list
        :param event: pygame.Event
        :returns: New menu item offset
        """
        # sanity check:
        # if there are 0 or 1 enabled items, then ignore movement
        enabled = len([i for i in self if i.enabled])
        if enabled < 2:
            return 0

        if event.type == pygame.KEYDOWN:

            # in order to accommodate disabled menu items,
            # the mod incrementer will loop until a suitable
            # index is found...one that is not disabled.
            items = len(self)
            mod = 0

            # horizontal movement: left and right will inc/dec mod by one
            if self.columns > 1:
                if event.key == pygame.K_LEFT:
                    mod -= 1

                elif event.key == pygame.K_RIGHT:
                    mod += 1

            # vertical movement: up/down will inc/dec the mod by adjusted
            # value of number of items in a column
            rows, remainder = divmod(items, self.columns)
            row, col = divmod(index, self.columns)

            # down key pressed
            if event.key == pygame.K_DOWN:
                if remainder:
                    if row == rows:
                        mod += remainder

                    elif col < remainder:
                        mod += self.columns
                    else:
                        if row == rows - 1:
                            mod += self.columns + remainder
                        else:
                            mod += self.columns

                else:
                    mod = self.columns

            # up key pressed
            elif event.key == pygame.K_UP:
                if remainder:
                    if row == 0:
                        if col < remainder:
                            mod -= remainder
                        else:
                            mod += self.columns * (rows - 1)
                    else:
                        mod -= self.columns

                else:
                    mod -= self.columns

            original_index = index
            seeking_index = True
            # seeking_index once false, will exit the loop
            while seeking_index and mod:
                index += mod

                # wrap the cursor position
                if index < 0:
                    index = items - abs(index)
                if index >= items:
                    index -= items

                # while looking for a suitable index, we've looked over all choices
                # just raise an error for now, instead of infinite looping
                # TODO: some graceful way to handle situations where cannot find an index
                if index == original_index:
                    raise RuntimeError

                seeking_index = not self.children[index].enabled

        return index


class RelativeLayout(Layout):
    """
    Drawing operations are relative to the group's rect
    """
    rect = pygame.Rect(0, 0, 0, 0)
    _init_rect = pygame.Rect(0, 0, 0, 0)

    def __init__(self, **kwargs):
        super(RelativeLayout, self).__init__()
        self._default_layer = kwargs.get('default_layer', 0)

        self._spritelayers = {}
        self._spritelist = []
        self.spritedict = {}
        self.lostsprites = []

    def add_widget(self, widget, index=0):
        super(RelativeLayout, self).add_widget(widget)
        self.spritedict[widget] = self._init_rect

    def calc_absolute_rect(self, rect):
        self.update_rect_from_parent()
        return rect.move(self.rect.topleft)

    def update_rect_from_parent(self):
        try:
            self.rect = self.parent()
        except TypeError:
            self.rect = pygame.Rect(self.parent.rect)

    def draw(self, surface):
        self.update_rect_from_parent()
        topleft = self.rect.topleft

        spritedict = self.spritedict
        surface_blit = surface.blit
        dirty = self.lostsprites
        self.lostsprites = []
        dirty_append = dirty.append

        for s in self.children:
            if s.image is None:
                continue

            if not getattr(s, 'visible', True):
                continue

            r = spritedict[s]
            newrect = surface_blit(s.image, s.rect.move(topleft))
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


class GridLayout(RelativeLayout, MenuLayout):
    """
    Sprite group which can be configured to arrange the children
    sprites into columns.
    """
    orientation = 'horizontal'  # default, and only implemented
    expand = True               # will fill all space of parent, if false, will be more compact

    def __init__(self, **kwargs):
        super(GridLayout, self).__init__(**kwargs)
        self._needs_arrange = False
        self._columns = 1
        self.line_spacing = None

    @property
    def columns(self):
        return self._columns

    @columns.setter
    def columns(self, value):
        self._columns = value
        self._needs_arrange = True

    def calc_bounding_rect(self):
        if self._needs_arrange:
            self._arrange_menu_items()
            self._needs_arrange = False
        return super(GridLayout, self).calc_bounding_rect()

    def add_widget(self, item, **kwargs):
        """ Add something to the grid

        do not add iterables to this function.  use 'extend'

        :param item: stuff to add
        :returns: None
        """
        super(GridLayout, self).add_widget(item, **kwargs)
        self._needs_arrange = True

    def remove(self, *items):
        super(GridLayout, self).remove(*items)
        self._needs_arrange = True

    def draw(self, surface):
        if self._needs_arrange:
            self._arrange_menu_items()
            self._needs_arrange = False
        super(GridLayout, self).draw(surface)

    def _arrange_menu_items(self):
        """ Iterate through menu items and position them in the menu
        Defaults to a multi-column layout with items placed horizontally first.

        :returns: None
        """
        if not len(self):
            return

        # max_width = 0
        max_height = 0
        for item in self.children:
            # max_width = max(max_width, item.rect.width)
            max_height = max(max_height, item.rect.height)

        self.update_rect_from_parent()
        width, height = self.rect.size

        items_per_column = math.ceil(len(self) / self.columns)

        if self.expand:
            # fill available space
            line_spacing = self.line_spacing
            if not line_spacing:
                line_spacing = height // items_per_column
        else:
            line_spacing = int(max_height * 1.2)

        column_spacing = width // self.columns

        # TODO: pagination API

        for index, item in enumerate(self.children):
            oy, ox = divmod(index, self.columns)
            item.rect.topleft = ox * column_spacing, oy * line_spacing
