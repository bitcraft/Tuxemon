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
from __future__ import absolute_import
from __future__ import division

import pygame as pg

from core import tools
from core.components.menu.interface import HorizontalBar
from core.components.ui import MenuItem
from core.components.ui.menu import Menu
from core.components.ui.graphicbox import GraphicBox
from core.components.ui.textarea import TextArea
from core.components.ui.font import bubble_text, shadow_text


class MonsterInfoState(Menu):
    """

    """
    background_filename = "gfx/backgrounds/autumn.png"
    draw_borders = False

    def startup(self, **kwargs):
        super(MonsterInfoState, self).startup(**kwargs)

        # load and scale the _background
        background = None
        if self.background_filename:
            background = tools.load_image(self.background_filename)

        # load and scale the menu borders
        border = None
        if self.draw_borders:
            border = tools.load_and_scale(self.borders_filename)

        # set the helper to draw the _background
        self.window = GraphicBox(border, background, (12, 222, 222))
        self.window.rect = pg.Rect(0, 0, 700, 700)

        self.add_widget(self.window)

        # make a text area to show messages
        self.text_area = TextArea(self.font, self.font_color, (96, 96, 96))
        self.text_area.rect = pg.Rect(tools.scale_sequence([20, 80, 80, 100]))
        self.sprites.add(self.text_area, layer=100)

        # Set up the border images used for the monster slots
        self.monster_slot_border = {}
        # self.bar = HorizontalBar()

        self.columns = 4

        # load and scale the monster slot borders
        root = "gfx/ui/monster/"
        border_types = ["empty", "filled", "active"]
        for border_type in border_types:
            filename = root + border_type + "_monster_slot_border.png"
            border = tools.load_and_scale(filename)

            filename = root + border_type + "_monster_slot_bg.png"
            background = tools.load_image(filename)

            # window = GraphicBox(border, background, None)
            # self.monster_slot_border[border_type] = window

        # TODO: something better than this global, load_sprites stuff
        for monster in self.game.player1.monsters:
            monster.load_sprites()

        width = tools.scale(40)
        height = tools.scale(40)

        # make 6 slots
        for i in range(30):
            rect = pg.Rect(0, 0, width, height)
            surface = pg.Surface(rect.size, pg.SRCALPHA)
            self.render_monster_slot(surface, rect, self.game.player1.monsters[i], False)
            item = MenuItem(surface, None, None, None)
            self.add_widget(item)

    def render_monster_slot(self, surface, rect, monster, in_focus):
        filled = monster is not None
        if filled:
            self.draw_monster_info(surface, monster, rect)
        return surface

    # def refresh_menu_items(self):
    #     """ Used to render slots after their 'focus' flags change
    #
    #     :return:
    #     """
    #     for index, item in enumerate(self.children):
    #         try:
    #             monster = self.game.player1.monsters[index]
    #         except IndexError:
    #             monster = None
    #         item.game_object = monster
    #         item.enabled = monster is not None
    #         item.image.fill((0, 0, 0, 0))
    #         # TODO: Cleanup this hack
    #         if index == self.selected_index:
    #             item.in_focus = True
    #         self.render_monster_slot(item.image, item.image.get_rect(), item.game_object, item.in_focus)

    def draw_monster_info(self, surface, monster, rect):
        """

        :type surface: pygame.surface.Surface
        :type monster: core.components.monster.Monster
        :type rect: pygame.rect.Rect
        :return:
        """
        # position and draw hp bar
        hp_rect = rect.copy()
        hp_rect.width = rect.width
        hp_rect.left = 0
        hp_rect.height = tools.scale(6)
        hp_rect.bottom = rect.bottom

        # draw the hp bar
        # self.bar.value = monster.current_hp / monster.hp
        # self.bar.draw(surface, hp_rect)

        # TODO: ANIMATION
        # generate a fun shadow
        shad = tools.make_shadow_surface(monster.sprites['menu'])
        shad = pg.transform.scale(shad, (shad.get_width(), shad.get_height() // 2))

        # position the monster sprite in the center
        monster_rect = monster.sprites['menu'].get_rect()
        # monster_rect.center = rect.center
        monster_rect.midtop = rect.midtop

        # draw the shadowm the sprite
        surface.blit(shad, monster_rect.move(0, monster_rect.height // 2))
        surface.blit(monster.sprites['menu'], monster_rect)

        # draw the name
        text = shadow_text(self.font, monster.name)
        text_rect = text.get_rect()
        # text_rect.centerx = rect.centerx
        text_rect.midtop = monster_rect.midbottom
        surface.blit(text, text_rect)

        # draw the level
        text = bubble_text(self.font, str(monster.level), (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.midleft = hp_rect.topleft
        text_rect.left += tools.scale(2)
        surface.blit(text, text_rect)

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
