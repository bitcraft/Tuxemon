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

from core import prepare, tools
from core.components.animation import Animation
from core.components.animation import Task
from core.components.animation import remove_animations_of
from core.group import Group
from core.rect import Rect

logger = logging.getLogger(__name__)


class Widget(object):
    """ Widgets are graphical elements

    * Widgets can contain other widgets
    * Widgets can define the layout of their children, but not themselves
    * Widgets can draw anywhere, but should stay in bounds
    """

    def __init__(self):
        self.parent = None  # type: Widget
        self.enabled = True
        self.disabled = False
        self.visible = True
        self.transparent = True
        self.padding = 0  # used to compensate for window borders
        self.children = list()  # type: List[Widget]
        self.animations = Group()
        self._in_focus = False
        self._in_refresh = False
        self._needs_refresh = True

        # bounds: screen space region where widget is expected to draw
        # bounds are set by the parents
        self._bounds = None  # type: Rect
        self.fit_bounds()

        # irect: rect, relative to bounds; "internal rect"
        # irect position is set by parent or widget
        # irect size should not be changed by parent
        self.irect = Rect(0, 0, 0, 0)

        # rect: screen space region where widget was last drawn
        # rect is set by the widget
        # rect should not be changed by parent
        self.rect = None  # type: Rect

        # anchors: used to position rect inside the bounds
        # may be set by parents or widget
        self._anchors = dict()  # used to position the menu/state

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

    @property
    def bounds(self):
        return self._bounds

    @bounds.setter
    def bounds(self, rect):
        if not self._bounds == rect:
            self._bounds = Rect(rect)
            for child in self.children:
                child.fit_bounds()

    def toggle_focus(self):
        self._in_focus = not self._in_focus

    @property
    def in_focus(self):
        return self._in_focus

    @in_focus.setter
    def in_focus(self, value):
        self._in_focus = bool(value)

    # def _walk(self, restrict=False, loopback=False, index=None):
    #     # We pass index only when we are going on the parent
    #     # so don't yield the parent as well.
    #     if index is None:
    #         index = len(self.children)
    #         yield self
    #
    #     for child in reversed(self.children[:index]):
    #         for walk_child in child._walk(restrict=True):
    #             yield walk_child
    #
    #     # If we want to continue with our parent, just do it.
    #     if not restrict:
    #         parent = self.parent
    #         try:
    #             if parent is None or not isinstance(parent, Widget):
    #                 raise ValueError
    #             index = parent.children.index(self)
    #         except ValueError:
    #             # Self is root, if we want to loopback from the first element:
    #             if not loopback:
    #                 return
    #             # If we started with root (i.e. index==None), then we have to
    #             # start from root again, so we return self again. Otherwise, we
    #             # never returned it, so return it now starting with it.
    #             parent = self
    #             index = None
    #         for walk_child in parent._walk(loopback=loopback, index=index):
    #             yield walk_child

    def walk(self, restrict=False, loopback=False):
        return iter(self.children)

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

            # if event is None, then child widget has used event
            # so break to prevent propagation of the event
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
        # TODO: Eventually roll this into a game clock/scheduler
        ani = Animation(*targets, **kwargs)
        self.animations.add(ani)
        return ani

    def task(self, *args, **kwargs):
        """ Create a task for this widget

        Tasks are processed even while widget is disabled
        If you want to pass positional arguments, use functools.partial

        :param args: function to be called
        :param kwargs: kwargs passed to the function
        :returns: core.components.animation.Task
        """
        # TODO: Eventually roll this into a game clock/scheduler
        task = Task(*args, **kwargs)
        self.animations.add(task)
        return task

    def remove_animations_of(self, target):
        """ Given and object, remove any animations modify the target object

        :type target: any
        :returns: None
        """
        # TODO: Eventually roll this into a game clock/scheduler
        remove_animations_of(target, self.animations)

    def update(self, time_delta):
        # TODO: Eventually roll this into a game clock/scheduler
        self.animations.update(time_delta)
        for child in list(self.children):
            child.update(time_delta)

    def fit_bounds(self):
        """ Adjust own bounds from parent's inner rect

        Calling this will change bounds if they were set manually.

        Do not override.  Use _fit_bounds instead.

        """
        logger.debug("{} fit bounds".format(self))

        self._fit_bounds()
        self.trigger_refresh()
        for child in self.children:
            child.fit_bounds()

    def _fit_bounds(self):
        """ Adjust own bounds from parent's inner rect

        Calling this will change bounds if they were set manually.

        :return:
        """
        if self.parent:
            self._bounds = self.parent.calc_internal_rect()
        else:
            self._bounds = Rect((0, 0), prepare.SCREEN_SIZE)

    def trigger_refresh(self):
        """ Call to set a refresh at next opportunity.
        
        Best to call this after the widget's position or bounds changes.
        
        :return: None
        """
        logger.debug("{} TRIGGERED".format(self))
        self._needs_refresh = True

    def check_refresh(self):
        """ If layout is stale, refresh it and the children
        
        Best to call this before drawing operations, or before
        the layout is manipulated in some way
        """
        if self._needs_refresh and not self._in_refresh:

            # prevent recursion if refresh is triggered during refresh
            self._in_refresh = True

            # force refresh
            self._refresh_layout()

            for child in self.children:
                child.trigger_refresh()

            self._needs_refresh = False
            self._in_refresh = False

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
        pass

    def draw(self, surface):
        """ Cause this and all children to draw themselves to the surface

        Add drawing operations will be limited to the bounds of this widget

        Do not override.  Use _draw instead.

        :param surface: Surface to draw on
        :type surface: pygame.surface.Surface

        :returns: None
        """
        self.trigger_refresh()
        self.check_refresh()
        self._draw(surface)

        with tools.clip_context(surface, self._bounds):
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

        Do not override.  Use _calc_internal_rect instead.

        :returns: Rect representing space inside borders, if any
        :rtype: Rect
        """
        self.check_refresh()
        return self._calc_internal_rect()

    def _calc_internal_rect(self):
        """

        :rtype: Rect
        """
        return self._bounds.inflate(-self.padding, -self.padding)

    def calc_bounding_rect(self):
        """ Return a rect that contains this and all children

        This uses the widget irect, which may be larger than the bounds

        Screen space

        :rtype: Rect
        """
        self.check_refresh()
        root = self.translate_irect()
        if self.children:
            kinder = [i.calc_bounding_rect() for i in self.children]
            return root.unionall(kinder)
        else:
            return root

    def translate_irect(self):
        return self.irect.move(self.bounds.topleft)

    def calc_final_rect(self):
        """ Calculate the area in the game window where menu is shown

        This value is the __desired__ location and size, and should not change
        over the lifetime of the widget.  It is used to generate animations.

        :rtype: Rect
        """
        original = self.rect.copy()
        self.refresh_layout()
        rect = self.rect.copy()
        self.refresh_layout()
        self.rect = original
        return rect

    def add_widget(self, widget, index=None):
        """ Add a widget to this wiget as a child

        :type widget: Widget
        :type index: int

        :return:
        """
        logger.debug("{} adding widget".format(self))
        if widget.parent:
            raise RuntimeError('cannot add widget because it is already contained by another')

        widget.parent = self
        widget.fit_bounds()

        if self.disabled:
            widget.disabled = True

        if index is None:
            self.children.append(widget)
        else:
            self.children.insert(index, widget)

        self.trigger_refresh()

    def remove_widget(self, widget):
        """ Remove widget from this one

        :type widget: Widget

        :return:
        """
        logger.debug("{} removing widget".format(self))
        widget.parent = None
        self.children.remove(widget)
        self.trigger_refresh()

    def clear_widgets(self):
        """ Remove all the widgets contained

        :return:
        """
        for widget in list(self.children):
            self.remove_widget(widget)

    def position_rect(self):
        """ Reposition irect taking in account the anchors

        This will adjust the internal position of the rect

        :return: True if the rect was changed
        :rtype: bool
        """
        old = self.irect.copy()

        for attribute, value in self._anchors.items():
            setattr(self.irect, attribute, value)

        if not self.rect == old:
            self.trigger_refresh()

    def anchor(self, attribute, value):
        """ Set an anchor for the menu window

        You can pass any string value that is used in a rect,
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
