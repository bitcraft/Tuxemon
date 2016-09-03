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
# William Edwards <shadowapex@gmail.com>
# Derek Clark <derekjohn.clark@gmail.com>
# Leif Theden <leif.theden@gmail.com>
#
from __future__ import division
from __future__ import absolute_import

import pygame

from core import prepare
from core import tools
from core.components.menu.interface import HpBar, MenuItem
from core.components.menu.menu import Menu
from core.components.ui.draw import GraphicBox
from core.components.ui.text import draw_text, TextArea


class MonsterInfoState(Menu):
    """

    """
    background_filename = "gfx/ui/monster/monster_menu_bg.png"
    draw_borders = False

    def startup(self, **kwargs):
        super(MonsterInfoState, self).startup(**kwargs)

        # make a text area to show messages
        self.text_area = TextArea(self.font, self.font_color, (96, 96, 96))
        self.text_area.rect = pygame.Rect(tools.scale_sequence([20, 80, 80, 100]))
        self.sprites.add(self.text_area, layer=100)

        # Set up the border images used for the monster slots
        self.monster_slot_border = {}
        self.monster_portrait = pygame.sprite.Sprite()
        self.hp_bar = HpBar()

        # load and scale the monster slot borders
        root = "gfx/ui/monster/"
        border_types = ["empty", "filled", "active"]
        for border_type in border_types:
            filename = root + border_type + "_monster_slot_border.png"
            border = tools.load_and_scale(filename)

            filename = root + border_type + "_monster_slot_bg.png"
            background = tools.load_image(filename)

            window = GraphicBox(border, background, None)
            self.monster_slot_border[border_type] = window

        # TODO: something better than this global, load_sprites stuff
        for monster in self.game.player1.monsters:
            monster.load_sprites()

    def calc_menu_items_rect(self):
        width, height = self.rect.size
        left = width // 2.25
        top = height // 12
        width /= 2
        return pygame.Rect(left, top, width, height - top * 2)

    def initialize_items(self):
        # position the monster portrait
        try:
            monster = self.game.player1.monsters[self.selected_index]
            image = monster.sprites["front"]
        except IndexError:
            image = pygame.Surface((1, 1), pygame.SRCALPHA)

        # position and animate the monster portrait
        width, height = prepare.SCREEN_SIZE
        self.monster_portrait.rect = image.get_rect(centerx=width // 4, top=height // 12)
        self.sprites.add(self.monster_portrait)
        self.animations.empty()

        width = tools.scale(80)
        height = tools.scale(32)

        # make 6 slots
        for i in range(3):
            rect = pygame.Rect(0, 0, width, height)
            surface = pygame.Surface(rect.size, pygame.SRCALPHA)
            item = MenuItem(surface, None, None, None)
            yield item

        self.refresh_menu_items()

    def on_menu_selection(self, menu_item):
        pass

    def render_monster_slot(self, surface, rect, monster, in_focus):
        filled = monster is not None
        border = self.determine_border(in_focus, filled)
        border.draw(surface)
        if filled:
            self.draw_monster_info(surface, monster, rect)
        return surface

    def refresh_menu_items(self):
        """ Used to render slots after their 'focus' flags change

        :return:
        """
        for index, item in enumerate(self.menu_items):
            try:
                monster = self.game.player1.monsters[index]
            except IndexError:
                monster = None
            item.game_object = monster
            item.enabled = monster is not None
            item.image.fill((0, 0, 0, 0))
            # TODO: Cleanup this hack
            if index == self.selected_index:
                item.in_focus = True
            self.render_monster_slot(item.image, item.image.get_rect(), item.game_object, item.in_focus)

    def draw_monster_info(self, surface, monster, rect):
        """

        :type surface: pygame.surface.Surface
        :type monster: core.components.monster.Monster
        :type rect: pygame.rect.Rect
        :return:
        """
        # position and draw hp bar
        hp_rect = rect.copy()
        left = rect.width * .6
        right = rect.right - tools.scale(4)
        hp_rect.width = right - left
        hp_rect.left = left
        hp_rect.height = tools.scale(8)
        hp_rect.centery = rect.centery

        # add the menu sprite
        # TODO: ANIMATION
        shad = tools.make_shadow_surface(monster.sprites['menu'])
        shad = pygame.transform.scale(shad, (shad.get_width(), shad.get_height() // 2))
        surface.blit(shad, tools.scale_sequence((4, 14)))
        surface.blit(monster.sprites['menu'], tools.scale_sequence((4, 2)))

        # # draw the hp bar
        # self.hp_bar.value = monster.current_hp / monster.hp
        # self.hp_bar.draw(surface, hp_rect)

        # draw the name

        text_rect = rect.inflate(-tools.scale(6), -tools.scale(6))
        text = self.shadow_text(monster.name)
        surface.blit(text, text_rect)
        #
        # # draw the level info
        # text_rect.top = rect.bottom - tools.scale(7)
        # draw_text(surface, "  Lv " + str(monster.level), text_rect, font=self.font)

        # # draw any status icons
        # # TODO: caching or something, idk
        # # TODO: not hardcode icon sizes
        # for index, status in enumerate(monster.status):
        #     if status.icon:
        #         image = tools.load_and_scale(status.icon)
        #         pos = (rect.width * .4) + (index * tools.scale(32)), rect.y + tools.scale(5)
        #         surface.blit(image, pos)

    def determine_border(self, selected, filled):
        if selected:
            return self.monster_slot_border['active']
        elif filled:
            return self.monster_slot_border['filled']
        else:
            return self.monster_slot_border['empty']

    def on_menu_selection_change(self):
        try:
            monster = self.game.player1.monsters[self.selected_index]
            image = monster.sprites["front"]
        except IndexError:
            image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.monster_portrait.image = image
        self.refresh_menu_items()
