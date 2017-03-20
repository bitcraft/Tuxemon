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

import logging

import pygame as pg

from core.components.animation import Animation
from core.components.animation import Task
from core.components.animation import remove_animations_of

# Create a logger for optional handling of debug messages.
logger = logging.getLogger(__name__)
logger.debug("{} successfully imported".format(__name__))


class Widget(object):
    """ Widgets are graphical elements

    * Widgets can contain other widgets
    * Widgets can define the layout of their children, but not themselves
    """
    rect = pg.Rect(0, 0, 0, 0)

    def __init__(self):
        self.parent = None
        self.disabled = False
        self.children = list()
        self.animations = pg.sprite.Group()
        self._needs_refresh = True

    def __len__(self):
        kinder = list(self.walk())
        return len(kinder) - 1

    def __nonzero__(self):
        kinder = len(self) - 1
        return bool(kinder)

    def __getitem__(self, item):
        kinder = list(self.walk())
        return kinder[item]

    def __iter__(self):
        return self.walk()

    def __contains__(self, item):
        kinder = list(self.walk())
        return item in kinder

    def _walk(self, restrict=False, loopback=False, index=None):
        # We pass index only when we are going on the parent
        # so don't yield the parent as well.
        if index is None:
            index = len(self.children)
            yield self

        for child in reversed(self.children[:index]):
            for walk_child in child._walk(restrict=True):
                yield walk_child

        # If we want to continue with our parent, just do it.
        if not restrict:
            parent = self.parent
            try:
                if parent is None or not isinstance(parent, Widget):
                    raise ValueError
                index = parent.children.index(self)
            except ValueError:
                # Self is root, if we want to loopback from the first element:
                if not loopback:
                    return
                # If we started with root (i.e. index==None), then we have to
                # start from root again, so we return self again. Otherwise, we
                # never returned it, so return it now starting with it.
                parent = self
                index = None
            for walk_child in parent._walk(loopback=loopback, index=index):
                yield walk_child

    def walk(self, restrict=False, loopback=False):
        gen = self._walk(restrict, loopback)
        yield next(gen)
        for node in gen:
            if node is self:
                return
            yield node

    # def walk(self):
    #     """ Return children (and children of children) in render order
    #     """
    #     q = self.children.copy()
    #     i = list()
    #     while q:
    #         child = q.pop()
    #         q.extend(child.children)
    #         i.append(child)
    #
    #     for child in i:
    #         yield child

    def process_event(self, event):
        """ Processes events that were passed from the main event loop.

        This function can choose to return the event, or any other in
        response to the event passed.  If the same, or any other event
        is returned, then it will be passed down to other states.

        :param event: A pygame key event from pygame.event.get()
        :type event: PyGame Event
        :returns: Pygame Event or None
        :rtype: pygame Event

        """
        return event

    def animate(self, *targets, **kwargs):
        """ Animate something in this widget

        Animations are processed even while state is inactive

        :param targets: targets of the Animation
        :type targets: any
        :param kwargs: Attributes and their final value
        :returns: core.components.animation.Animation
        """
        ani = Animation(*targets, **kwargs)
        self.animations.add(ani)
        return ani

    def task(self, *args, **kwargs):
        """ Create a task for this widget

        Tasks are processed even while state is inactive
        If you want to pass positional arguments, use functools.partial

        :param args: function to be called
        :param kwargs: kwargs passed to the function
        :returns: core.components.animation.Task
        """
        task = Task(*args, **kwargs)
        self.animations.add(task)
        return task

    def remove_animations_of(self, target):
        """ Given and object, remove any animations that it is used with

        :param target: any
        :returns: None
        """
        remove_animations_of(target, self.animations)

    def update(self, time_delta):
        for child in self.walk():
            if child is not self:
                child.update(time_delta)

        self.animations.update(time_delta)

    def draw(self, surface):
        """ Cause this and all children to draw themselves to the surface

        The actual method that draws is Widget._draw

        :param surface: Surface to draw on
        :type surface: pygame.Surface

        :rtype: None
        :returns: None
        """
        if self._needs_refresh:
            self.refresh_layout()

        for child in self.walk():
            if child is not self:
                child.draw(surface)

        self._draw(surface)

    def _draw(self, surface):
        """ Draw only this widget to the surface

        :param surface:
        :return:
        """
        pass

    def calc_bounding_rect(self):
        """ Return a rect that contains this and all children

        :rtype: pg.Rect
        """
        kinder = list(self.walk())
        if not kinder:
            return self.rect
        elif len(kinder) == 1:
            return pg.Rect(kinder[0].rect)
        else:
            return kinder[0].rect.unionall([s.rect for s in kinder[1:]])

    def add_widget(self, widget, index=0):
        """ Add a widget to this window as a child

        :param widget:
        :param index:
        :return:
        """
        if widget.parent:
            raise RuntimeError('cannot add widget because it is already contained by another')

        widget.parent = self

        if self.disabled:
            widget.disabled = True

        self.children.insert(index, widget)
        self._needs_refresh = True

    def remove_widget(self, widget):
        """ Remove widget from this one

        :param widget:
        :return:
        """
        self.children.remove(widget)
        self._needs_refresh = True
        widget.parent = None

    def clear_widgets(self):
        """ Remove all the widgets contained

        :return:
        """
        for widget in self.children.copy():
            self.remove_widget(widget)
        self._needs_refresh = True

    def refresh_layout(self):
        """ Fit border to contents and hide/show cursor

        :return:
        """
        x = 0
        y = 0
        for child in self.walk():
            if child is not self:
                child.rect.topleft = child.to_relative(x, y)
                x += 50
                y += 30

    def to_relative(self, x, y):
        """ Transform the coords to relative coordinates

        :return: int, int
        """
        xx, yy = self.parent.rect.topleft
        return x + xx, y + yy

        # self._needs_refresh = False
        # self.menu_items.expand = not self.shrink_to_items
        #
        # # check if we have items, but they are all disabled
        # disabled = all(not i.enabled for i in self.menu_items)
        #
        # if self.menu_items and not disabled:
        #     self.show_cursor()
        # else:
        #     self.hide_cursor()
        #
        # if self.shrink_to_items:
        #     self.fit_border()
