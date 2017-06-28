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
import pygame

from core import tools
from core.components.animation import remove_animations_of
from core.components.menu.interface import MenuCursor
from core.components.menu.interface import MenuItem
from core.components.ui.font import shadow_text
from core.components.ui.layout import GridLayout, RelativeLayout
from core.components.ui.widget import Widget


class Menu(Widget):
    """ A class to create menu objects.

    :background: String

    :ivar rect: The rect of the menu in pixels, defaults to 0, 0, 400, 200.
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
    touch_aware = False  # if true, then menu items can be selected with the mouse/touch

    def __init__(self):
        super(Menu, self).__init__()

        self.menu_rect = None
        self.menu_items = GridLayout()
        self.menu_items.columns = self.columns
        self.add_widget(self.menu_items)

        # generally just for the cursor arrow
        self.menu_sprites = RelativeLayout()
        self.add_widget(self.menu_sprites)

        self.selected_index = 0  # track which menu item is selected
        # holds sprites representing menu items
        self.arrow = None

        self.menu_select_sound = tools.load_sound(self.menu_select_sound_filename)
        self.line_spacing = tools.scale(10)
        self.font = tools.load_default_font()

        # load the cursor
        image = tools.load_and_scale(self.cursor_filename)
        self.arrow = MenuCursor(image)
        self.menu_sprites.add_widget(self.arrow)

    def build_text_item(self, label, callback, icon=None):
        """ Create a menu item and add it to the menu

        :param label: Some text
        :param icon: pygame surface (not used yet)
        :param callback: callback to use when selected
        :return: Menu Item
        """
        # WHITE
        # bg = (192, 192, 192)
        # fg = (245, 245, 245)
        bg = (192, 192, 192)
        fg = (0, 0, 0)
        image = shadow_text(self.font, fg, bg, label)
        item = MenuItem(image, label, None, callback)
        self.menu_items.add_widget(item)

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
        self._needs_refresh = True
        items = self.initialize_items()
        if items:
            self.menu_items.clear_widgets()

            for item in items:
                self.add(item)

            number_items = len(self.menu_items)
            if self.menu_items and self.selected_index >= number_items:
                self.change_selection(number_items - 1)

    def show_cursor(self):
        """ Show the cursor that indicates the selected object

        :returns: None
        """
        if self.arrow not in self.menu_sprites:
            self.menu_sprites.add_widget(self.arrow)
            self.trigger_cursor_update(False)
            self.get_selected_item().in_focus = True

    def hide_cursor(self):
        """ Hide the cursor that indicates the selected object

        :returns: None
        """
        if self.arrow in self.menu_sprites:
            self.menu_sprites.remove(self.arrow)
            selected = self.get_selected_item()
            if selected is not None:
                selected.in_focus = False

    def refresh_layout(self):
        """ Fit border to contents and hide/show cursor

        :return:
        """
        # self.menu_items.expand = not self.shrink_to_items

        # check if we have items, but they are all disabled
        disabled = all(i.disabled for i in self.menu_items)

        self.trigger_cursor_update(False)

        if self.menu_items and not disabled:
            self.show_cursor()
        else:
            self.hide_cursor()

    def process_event(self, event):
        """ Process pygame input events

        The menu cursor is handled here, as well as the ESC and ENTER keys.

        This will also toggle the 'in_focus' of the menu item

        :type event: pygame.Event
        :returns: None
        """
        if event.type == pygame.KEYDOWN:

            # check if we have items, but they are all disabled
            disabled = all(i.disabled for i in self.menu_items)

            if not disabled and self.menu_items:

                if event.key == pygame.K_RETURN:
                    self.menu_select_sound.play()
                    self.on_menu_selection(self.get_selected_item())

                else:
                    index = self.menu_items.determine_cursor_movement(self.selected_index, event)
                    if not self.selected_index == index:
                        self.change_selection(index)

        # TODO: handling of click/drag, miss-click, etc
        # TODO: eventually, maybe move some handling into menuitems
        # TODO: handle screen scaling?
        # TODO: generalized widget system
        elif self.touch_aware and event.type == pygame.MOUSEBUTTONDOWN:
            # menu items is (sometimes) a relative group, so their rect will be relative to their parent
            # we need to adjust the point to topleft of the containing rect
            # eventually, a widget system could do this automatically

            # make sure that the rect's position is current
            # a sprite group may not be a relative group... so an attribute error will be raised
            # obvi, a wart, but will be fixed sometime (tm)
            try:
                self.menu_items.update_rect_from_parent()
            except AttributeError:
                # not a relative group, no need to adjust cursor
                mouse_pos = event.pos
            else:
                # move the mouse/touch origin to be relative to the menu_items
                # TODO: a vector type would be niceeee
                mouse_pos = [a - b for a, b in zip(event.pos, self.menu_items.rect.topleft)]

            # loop through all the items here and see if they collide
            # eventually, we should make this more generic...not part of the menu
            for index, item in enumerate([i for i in self.menu_items if i.enabled]):
                if item.rect.collidepoint(mouse_pos):
                    self.change_selection(index)
                    self.on_menu_selection(self.get_selected_item())

    def change_selection(self, index, animate=True):
        """ Force the menu to be evaluated and move cursor and trigger focus changes

        :return: None
        """
        previous = self.get_selected_item()
        if previous is not None:
            previous.in_focus = False  # clear the focus flag of old item, if any
        self.selected_index = index  # update the selection index
        self.menu_select_sound.play()  # play a sound
        self.trigger_cursor_update(animate)  # move cursor and [maybe] animate it
        self.check_bounds()  # scroll items if off the screen
        self.get_selected_item().in_focus = True  # set focus flag of new item
        self.on_menu_selection_change()  # let subclass know menu has changed

    def check_bounds(self):
        """ Check if the currently selected item is off screen, and animate to show it

        This is essentially: scrolling the menu items if the items are off screen

        WIP

        :return: None
        """
        # TODO: unify the menu_rect attribute, or move menu to own widget
        menu_rect = self.menu_items.calc_bounding_rect()

        # get the selected item, if any
        selected = self.get_selected_item()
        if selected is None:
            raise RuntimeError

        # transform coordinates to screen space
        selected_rect = self.menu_items.calc_absolute_rect(selected.rect)

        # determine if the contents need to be scrolled on the screen
        diff = tools.calc_scroll_thing(selected_rect, menu_rect, self.rect)

        if diff:
            remove_animations_of(menu_rect, self.animations)
            self.animate(self.menu_rect, duration=.25, relative=True, **diff)

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
        if selected is None:
            raise RuntimeError

        x, y = selected.rect.midleft
        x -= tools.scale(2)

        if animate:
            self.remove_animations_of(self.arrow.rect)
            return self.animate(self.arrow.rect, right=x, centery=y, duration=self.cursor_move_duration)
        else:
            self.arrow.rect.midright = x, y
            return None

    def get_selected_item(self):
        """ Get the Menu Item that is currently selected

        :rtype: MenuItem
        :rtype: core.components.menu.interface.MenuItem
        """
        try:
            item = self.menu_items[self.selected_index]
            assert item is not None
            return item
        except IndexError:
            raise RuntimeError("invalid selected index?")

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

    def calc_final_rect(self):
        """ Calculate the area in the game window where menu is shown

        This value is the __desired__ location and size, and should not change
        over the lifetime of the menu.  It is used to generate animations
        to open the menu.

        The rect represents the size of the menu after all items are added.

        :rtype: pygame.Rect
        """
        original = self.rect.copy()  # store the original rect
        self.refresh_layout()  # arrange the menu
        rect = self.rect.copy()  # store the final rect
        self.rect = original  # set the original back
        return rect

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
