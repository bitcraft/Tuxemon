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

import pygame

from core import tools
from core.components.ui.imagewidget import ImageWidget
from core.components.ui.layout import GridLayout
from core.components.ui.widget import Widget

logger = logging.getLogger(__name__)


class MenuItem(ImageWidget):
    def __init__(self, image, label, description, game_object):
        super(MenuItem, self).__init__(image)
        self.label = label
        self.description = description
        self.game_object = game_object

        # def __repr__(self):
        #     return "<MenuItem: {}>".format(self.label)


class Menu(Widget):
    """ A class to create menu objects.

    :background: String

    :ivar selected_index: The index position of the currently selected menu item.
    :ivar menu_items: A list of available menu items.
    """
    # defaults for the menu
    columns = 1
    menu_select_sound_filename = "sounds/interface/menu-select.ogg"
    default_character_delay = 0.05
    animate_contents = False  # show contents while window opens
    cursor_filename = "gfx/arrow.png"
    cursor_move_duration = .20
    touch_aware = True  # if true, then menu items can be selected with the mouse/touch
    key_aware = True  # if true, then keyboard input will try to find items
    input_timeout = 1  # time to clear the keyboard input buffer
    key_repeat_interval = .05  # time between repeat keypresses
    key_repeat_delay = .4  # time to wait until repeat keys

    def __init__(self):
        super(Menu, self).__init__()
        self.selected_index = 0  # track which menu item is selected
        self.menu_select_sound = tools.load_sound(self.menu_select_sound_filename)

        # for keyboard input handling
        self._key_repeat_task = None  # type: Task
        self._key_repeat_value = None  # type: int
        self._key_repeat_timer = None
        self._input_clear_task = None  # type: Task
        self._input_string = ''  # for holding keyboard input

        # menu_items is a layout of selectable elements
        # this is where the item list lives
        self.menu_items = GridLayout()
        self.menu_items.columns = self.columns
        self.add_widget(self.menu_items)

        # load the cursor
        image = tools.load_and_scale(self.cursor_filename)
        self.cursor = ImageWidget(image)
        self.add_widget(self.cursor)

    # def start_text_animation(self, text_area):
    #     """ Start an animation to show textarea, one character at a time
    #
    #     :param text_area: TextArea to animate
    #     :type text_area: core.components.ui.text.TextArea
    #     :rtype: None
    #     """
    #
    #     def next_character():
    #         try:
    #             next(text_area)
    #         except StopIteration:
    #             pass
    #         else:
    #             self.task(next_character, self.character_delay)
    #
    #     self.character_delay = self.default_character_delay
    #     self.remove_animations_of(next_character)
    #     next_character()
    #
    # def animate_text(self, text_area, text):
    #     """ Set and animate a text area
    #
    #     :param text: Test to display
    #     :type text: basestring
    #     :param text_area: TextArea to animate
    #     :type text_area: core.components.ui.text.TextArea
    #     :rtype: None
    #     """
    #     text_area.text = text
    #     self.start_text_animation(text_area)
    #
    # def alert(self, message):
    #     """ Write a message to the first available text area
    #
    #     Generally, a state will have just one, if any, text area.
    #     The first one found will be use to display the message.
    #     If no text area is found, a RuntimeError will be raised
    #
    #     :param message: Something interesting, I hope.
    #     :type message: basestring
    #
    #     :returns: None
    #     """
    #
    #     def find_textarea():
    #         for sprite in self.sprites:
    #             if isinstance(sprite, TextArea):
    #                 return sprite
    #         print("attempted to use 'alert' on state without a TextArea", message)
    #         raise RuntimeError
    #
    #     self.animate_text(find_textarea(), message)

    def reload_items(self):
        """ Empty all items in the menu and re-add them

        Only works if initialize_items is used

        :return: None
        """
        logger.debug("{} trigger refresh reloading items".format(self))
        self.trigger_refresh()
        items = self.initialize_items()
        if items:
            self.menu_items.clear_widgets()

            for item in items:
                self.add_widget(item)

            number_items = len(self.menu_items)
            if self.menu_items and self.selected_index >= number_items:
                self.change_selection(number_items - 1)

    def show_cursor(self):
        """ Show the cursor that indicates the selected object

        :returns: None
        """
        if self.cursor not in self.children:
            self.add_widget(self.cursor)
            self.trigger_cursor_update(False)
            self.get_selected_item().in_focus = True

    def hide_cursor(self):
        """ Hide the cursor that indicates the selected object

        :returns: None
        """
        if self.cursor in self.children:
            self.remove_widget(self.cursor)
            selected = self.get_selected_item()
            if selected is not None:
                selected.in_focus = False

    def _refresh_layout(self):
        """ Fit border to contents and hide/show cursor

        :return:
        """
        # self.menu_items.expand = not self.shrink_to_items

        if not self.in_focus:
            self.hide_cursor()
            return

        # check if we have items, but they are all disabled
        disabled = all(i.disabled for i in self.menu_items)

        if self.menu_items and not disabled:
            self.show_cursor()
            self.trigger_cursor_update(False)
        else:
            self.hide_cursor()

    # INPUT BUFFER
    def add_input_buffer(self, char):
        self._input_string += char

    def clear_input_buffer(self):
        self._input_string = ''

    def backspace(self):
        self._input_string = self._input_string[:-1]

    def process_event(self, event):
        """ Process pygame input events

        The menu cursor is handled here, as well as the ESC and ENTER keys.

        This will also toggle the 'in_focus' of the menu item

        :type event: pygame.Event
        :returns: None
        """
        if event.type == pygame.KEYDOWN:
            self.in_focus = True

            # TODO: remove this check each time
            # check if we have items, but they are all disabled
            disabled = all(i.disabled for i in self.menu_items)

            if not disabled and self.menu_items:

                if event.key == pygame.K_RETURN:
                    self.menu_select_sound.play()
                    self.on_menu_selection(self.get_selected_item())
                    return

                else:
                    index = self.menu_items.determine_cursor_movement(self.selected_index, event)
                    if not self.selected_index == index:
                        self.change_selection(index)
                        self.check_start_key_repeat(event.key)
                        return

                # try to find items based on input
                if self.key_aware:
                    self.handle_keypress(event)
                    # index = self.get_index_from_input()
                    # if index is not None:
                    #     self.change_selection(index)
                    #     return

        elif event.type == pygame.KEYUP:
            self.check_key_repeat(event.key)
            return

        # TODO: handling of click/drag, miss-click, etc
        # TODO: drag scrolling
        elif self.touch_aware and event.type == pygame.MOUSEBUTTONDOWN:
            for index, item in enumerate(self.menu_items):
                if item.enabled and item.bounds.collidepoint(event.pos):
                    self.change_selection(index)
                    self.on_menu_selection(self.get_selected_item())
                    return None

    def handle_keypress(self, event):
        """ Handle a keypress from a human

        * store the input
        * keep a timer to clear the input

        :type event: pygame.event.Event
        :return:
        """
        self.add_input_buffer(event.unicode.upper())
        if self._input_clear_task:
            self._input_clear_task.abort()

        index = self.find_selection(self._input_string)
        if index is None:
            self.clear_input_buffer()
        else:
            task = self.task(self.clear_input_buffer, self.input_timeout)
            self._input_clear_task = task
            self.change_selection(index)

    def find_selection(self, query):
        for index, result in enumerate(self.menu_items.children):
            if query in result.label.upper():
                return index
        else:
            return None

    def check_start_key_repeat(self, key):
        """ Only try to repeat a key if a repeat isn't already running

        Simple check only allows one key repeat and prevents recursion.

        :type key: int
        :return:
        """
        if self._key_repeat_task is None:
            self.start_key_repeat(key)

    def start_key_repeat(self, key):
        """ Begin timer until repeating starts

        :type key: int
        :return:
        """
        if self._key_repeat_task is None:
            delay = self.task(self.start_key_interval, self.key_repeat_delay)
            self._key_repeat_task = delay
            self._key_repeat_value = key

    def start_key_interval(self):
        """ Begin repeating

        :return:
        """
        task = self.task(self.handle_key_repeat, self.key_repeat_interval, -1)
        self._key_repeat_task = task

    def handle_key_repeat(self):
        """ Emit a single event

        These events will not propagate down state stack

        :return:
        """
        event = pygame.event.Event(pygame.KEYDOWN, {'key': self._key_repeat_value, 'unicode': ''})
        self.process_event(event)

        # TODO: remove need to call check_bounds manually
        # call check_bounds to ensure menu scrolls with virtual events
        # some bug prevents check bounds from happening in process_event above
        # could be related to the order that animations are executed
        self.check_bounds()

    def check_key_repeat(self, key):
        """ Should repeating stop?

        :param key:
        :return:
        """
        if self._key_repeat_value == key:
            self.stop_key_repeat()

    def stop_key_repeat(self):
        """ Stop repeating or waiting

        :return:
        """
        self._key_repeat_task.abort()
        self._key_repeat_task = None
        self._key_repeat_value = None

    def get_index_from_input(self):
        for index, item in enumerate(self.menu_items):
            if self._input_string in item.label.upper():
                return index
        return None

    def change_selection(self, index, animate=True):
        """ Force the menu to be evaluated, move cursor, and trigger focus changes

        :return: None
        """
        previous = self.get_selected_item()
        if previous is not None:
            previous.in_focus = False  # clear the focus flag of old item, if any
        self.selected_index = index  # update the selection index
        self.menu_select_sound.play()  # play a sound
        self.trigger_cursor_update(animate)  # move cursor and [maybe] animate it
        # self.check_bounds()  # scroll items if off the screen
        self.get_selected_item().in_focus = True  # set focus flag of new item
        self.on_menu_selection_change()  # let subclass know menu has changed

    def check_bounds(self):
        """ Check if the currently selected item is off screen and animate to show it

        This is essentially: scrolling the menu items if the items are off screen

        :return: None
        """
        # rect of the newly selected item and cursor
        # TODO: what is the selected item not able to test bounds?
        selection = self.get_selected_item().rect.union(self.cursor._bounds)

        # TODO: do not hardcode values
        # adjust bounds to compensate for the cursor
        bounds = self._bounds.inflate(tools.scale(-2), tools.scale(-6))

        # if selected rect is within bounds nothing needs to happen
        if bounds.contains(selection):
            return

        # determine if the contents need to be scrolled within its bounds
        bounding_rect = self.calc_bounding_rect()

        diff = tools.calc_scroll_thing(selection, bounding_rect, bounds)
        if diff:
            self.remove_animations_of(self.menu_items.irect)
            self.animate(self.menu_items.irect, duration=.25, relative=True, **diff)

    def search_items(self, game_object):
        """ Non-optimised search through menu_items for a particular thing

        TODO: address the confusing name "game object"

        :param game_object:
        :return:
        """
        for menu_item in self.menu_items:
            if game_object == menu_item.game_object:
                return menu_item
        return None

    def trigger_cursor_update(self, animate=True):
        """ Force the menu cursor to move into the correct position

        :param animate: If True, then arrow will move smoothly into position
        :returns: None or Animation
        """
        selected = self.get_selected_item()

        x, y = selected.rect.midleft
        x -= tools.scale(2)

        self.cursor._flag = True

        if animate:
            # top = self.menu_items.bounds.top + 100
            # self.remove_animations_of(self.menu_items.irect)
            # self.animate(self.menu_items.irect, y=top, duration=self.cursor_move_duration)
            self.cursor._bounds.size = self.cursor.irect.size
            self.remove_animations_of(self.cursor._bounds)
            ani = self.animate(self.cursor._bounds, right=x, centery=y, duration=self.cursor_move_duration)
            ani.update_callback = self.check_bounds
            return ani
        else:
            self.remove_animations_of(self.cursor._bounds)
            self.cursor._bounds.size = self.cursor.irect.size
            self.cursor._bounds.midright = x, y
            return None

    def get_selected_item(self):
        """ Get the Menu Item that is currently selected

        :rtype: Widget
        """
        try:
            item = self.menu_items[self.selected_index]
            assert item is not None
            return item
        except IndexError:
            return None

    # ============================================================================
    #   The following methods are designed to be monkey patched or overloaded
    # ============================================================================

    def calc_menu_items_rect(self):
        """ Calculate the area inside the internal rect where items are listed

        :rtype: pygame.Rect
        """
        # WARNING: hardcoded values related to menu arrow size
        #          if menu arrow image changes, this should be adjusted
        cursor_margin = -tools.scale(11), -tools.scale(5)
        inner = self.calc_internal_rect()
        menu_rect = inner.inflate(*cursor_margin)
        menu_rect.bottomright = inner.bottomright
        return menu_rect

    def on_menu_selection(self, item):
        """ Hook for things to happen when player selects a menu option

        Override in subclass, if you want to

        :return:
        """
        if item.enabled:
            item.game_object()

    def on_menu_selection_change(self):
        """ Hook for things to happen after menu selection changes

        Override in subclass

        :returns: None
        """
        pass
