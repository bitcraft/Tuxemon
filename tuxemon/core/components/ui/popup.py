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
from core.components.ui.window import Window


class PopUpMenu(Window):
    """ Menu with "pop up" style animation

    """

    # def animate_open(self):
    #     """ Called when menu is going to open
    #
    #     Menu will not receive input during the animation
    #     Menu will only play this animation once
    #
    #     Must return either an Animation or Task to attach callback
    #     Only modify state of the menu Rect
    #     Do not change important state attributes
    #
    #     :returns: Animation or Task
    #     :rtype: core.components.animation.Animation
    #     """
    #     return
    #
    #     # anchor the center of the popup
    #     rect = self.game.screen.get_rect()
    #     self.anchor("center", rect.center)
    #
    #     rect = self.calc_final_rect()
    #
    #     # set rect to a small size for the initial values of the animation
    #     self.rect = self.rect.copy()           # required.  do not remove.
    #     self.rect.height = int(rect.height * .1)
    #     self.rect.width = int(rect.width * .1)
    #     self.rect.center = rect.center
    #
    #     # if this statement were removed, then the menu would
    #     # refresh and the size animation would be lost
    #     self._needs_refresh = False
    #
    #     # create animation to open window with
    #     ani = self.animate(self.rect, height=rect.height, width=rect.width, duration=.20)
    #     ani.update_callback = lambda: setattr(self.rect, "center", rect.center)
    #     return ani
