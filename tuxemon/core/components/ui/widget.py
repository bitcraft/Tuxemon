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

import logging

from core import prepare
from core.components.animation import Animation
from core.components.animation import Task
from core.components.animation import remove_animations_of
from core.group import Group
from core.rect import Rect

# Create a logger for optional handling of debug messages.
logger = logging.getLogger(__name__)


class Widget(object):
    """ Widgets are graphical elements

    * Widgets can contain other widgets
    * Widgets can define the layout of their children, but not themselves
    * Widgets can draw anywhere, but should stay in bounds

    :ivartype parent: Widget
    """

    def __init__(self):
        self.parent = None  # type: Widget
        self.enabled = True
        self.disabled = False
        self.transparent = True
        self.expand = True  # fill all space of parent
        self.padding = 0  # used to compensate for window borders
        self.bounds = Rect(0, 0, 0, 0)  # set by parent where drawing should happen
        self.bounds = None
        self.rect = Rect(0, 0, 0, 0)  # dimensions of content
        self.inner = None  # where children are drawn
        self.children = list()  # type: List[Widget]
        self.animations = Group()
        self._in_focus = False
        self._in_refresh = False
        self._anchors = dict()  # used to position the menu/state
        self._needs_refresh = True

    def __repr__(self):
        return "<Widget: {}>".format(self.__class__.__name__)

    def __len__(self):
        return len(list(self.walk()))

    def __nonzero__(self):
        return bool(len(self))

    def __getitem__(self, item):
        return list(self.walk())[item]

    def __iter__(self):
        return self.walk()

    def __contains__(self, item):
        return item in list(self.walk())

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
        return iter(self.children)

        # gen = self._walk(restrict, loopback)
        # next(gen)  # this is always self
        #
        # for node in gen:
        #     if node is self:
        #         return
        #     yield node

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
        :type event: pygame.event.Event
        :rtype: pygame.event.Event

        """
        for child in list(self.children):
            if event is None:
                break

            event = child.process_event(event)

        return event

    def animate(self, *targets, **kwargs):
        """ Animate something in this widget

        Animations are processed even while widget is inactive

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

        :type target: any
        :returns: None
        """
        remove_animations_of(target, self.animations)

    def update(self, time_delta):
        self.animations.update(time_delta)
        self.trigger_refresh()

        for child in list(self.children):
            child.update(time_delta)

    def update_bounds(self):
        """ Adjust own bounds from parent
        
        WIP
        
        :return: 
        """
        logger.debug("{} updating rect".format(self))

        # if has a parent, check the parent
        if self.parent:
            old = self.bounds.copy() if self.bounds else None

            if self.bounds is None:
                # set our rect to the rect of the parent
                self.bounds = self.parent.calc_internal_rect()
            else:
                # cannot copy object b/c animations may be modifying the rect
                inner = self.parent.calc_internal_rect()
                # self.bounds.x = inner.x
                # self.bounds.y = inner.y
                # self.bounds.w = inner.w
                # self.bounds.h = inner.h

            changed = not old == self.bounds

        # no parent, so expand to fill the screen
        else:
            if self.bounds is None:
                self.bounds = Rect((0, 0), prepare.SCREEN_SIZE)
                changed = True
            else:
                changed = False

        if changed:
            logger.debug("RECT, {} {} {}".format(self, self.bounds, self.rect))
            logger.debug("{} trigger refresh update from parent".format(self))
            self.trigger_refresh()

        return changed

    def trigger_refresh(self):
        """ Call to set a refresh at next opportunity.
        
        Best to call this after the widget's position or bounds changes.
        
        :return: None
        """
        logger.debug("{} TRIGGERED".format(self))
        self._needs_refresh = True

    def check_refresh(self):
        """ Check if layout is stale, and if so refresh it
        
        Best to call this before drawing operations, or before
        the layout is manipulated in some way
        
        :returns: True is the layout was refreshed
        :rtype: bool
        """
        if self._needs_refresh and not self._in_refresh:

            if self.bounds is None:
                self.update_bounds()

            # prevent recursion if refresh is checked during refresh
            self._in_refresh = True

            self._refresh_layout()

            for child in self.children:
                child.trigger_refresh()

            self._needs_refresh = False
            self._in_refresh = False

            return True

        return False

    def refresh_layout(self):
        """ Force the layout to refresh self and children
        
        Do not override.  Use _refresh_layout instead.
        
        :return: 
        """
        logger.debug("{} trigger refresh forced".format(self))
        self.trigger_refresh()
        self.check_refresh()
        for child in self.children:
            child.refresh_layout()

    def _refresh_layout(self):
        """ Override if this widget does anything fancy with it's own rect or children

        :return: None
        """
        self.rect.topleft = self.bounds.topleft

    def draw(self, surface):
        """ Cause this and all children to draw themselves to the surface

        Do not override.  Use _draw instead.

        :param surface: Surface to draw on
        :type surface: pygame.surface.Surface

        :rtype: None
        :returns: None
        """
        self.update_bounds()
        self.check_refresh()
        self._draw(surface)

        for child in self.children:
            child.draw(surface)

    def _draw(self, surface):
        """ Draw only this widget to the surface

        :param surface:
        :return:
        """
        pass

    def calc_internal_rect(self):
        """ Calculate the area inside the borders, if any.
        If no padding is present, a copy of the window rect will be returned

        :returns: Rect representing space inside borders, if any
        :rtype: pygame.Rect
        """
        self.check_refresh()
        return self._calc_internal_rect()

    def _calc_internal_rect(self):
        """

        :rtype: pygame.Rect
        """
        return self.bounds.inflate(-self.padding, -self.padding)

    def calc_bounding_rect(self):
        """ Return a rect that contains this and all children

        :rtype: pygame.Rect
        """
        self.check_refresh()
        kinder = list(self.children)

        if not kinder:
            return self.rect
        elif len(kinder) == 1:
            return Rect(kinder[0].rect)
        else:
            return kinder[0].rect.unionall([s.rect for s in kinder[1:]])

    def calc_final_rect(self):
        """ Calculate the area in the game window where menu is shown

        This value is the __desired__ location and size, and should not change
        over the lifetime of the widget.  It is used to generate animations.

        :rtype: pygame.Rect
        """
        if self.bounds is None:
            self.update_bounds()

        original = self.rect.copy()
        self.refresh_layout()
        rect = self.rect.copy()
        self.refresh_layout()
        self.rect = original
        return rect

    def add_widget(self, widget, index=None):
        """ Add a widget to this window as a child

        :type widget: Widget
        :type index: int

        :return:
        """
        if widget.parent:
            raise RuntimeError('cannot add widget because it is already contained by another')

        widget.parent = self

        if self.disabled:
            widget.disabled = True

        if index is None:
            self.children.append(widget)
        else:
            self.children.insert(index, widget)

        logger.debug("{} adding widget".format(self))
        self.trigger_refresh()

    def remove_widget(self, widget):
        """ Remove widget from this one

        :type widget: Widget

        :return:
        """
        self.children.remove(widget)
        logger.debug("{} removing widget".format(self))
        self.trigger_refresh()
        widget.parent = None

    def clear_widgets(self):
        """ Remove all the widgets contained

        :return:
        """
        for widget in list(self.children):
            self.remove_widget(widget)

    def position_rect(self):
        """ Reposition rect taking in account the anchors
        
        :return: True if the rect was changed
        :rtype: bool
        """
        old = self.rect.copy()

        for attribute, value in self._anchors.items():
            setattr(self.rect, attribute, value)

        changed = not old == self.rect
        if changed:
            logger.debug("{} trigger refresh positioning".format(self))
            self.trigger_refresh()

        return changed

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

    def toggle_focus(self):
        self._in_focus = not self._in_focus

    @property
    def in_focus(self):
        return self._in_focus

    @in_focus.setter
    def in_focus(self, value):
        self._in_focus = bool(value)
