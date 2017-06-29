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
#
#
# core.main Sets up the states and main game loop.
#
from __future__ import absolute_import

import logging

from . import prepare

logger = logging.getLogger(__name__)


def main():
    """Add all available states to our scene manager (tools.Control)
    and start the game using the pygame interface.

    :rtype: None
    :returns: None

    """
    import pygame
    from .control import PygameControl

    prepare.init()
    control = PygameControl(prepare.ORIGINAL_CAPTION)
    control.auto_state_discovery()

    # background state is used to prevent other states from
    # being required to track dirty screen areas.  for example,
    # in the start state, there is a menu on a blank background,
    # since menus do not clean up dirty areas, the blank,
    # "Background state" will do that.  The alternative is creating
    # a system for states to clean up their dirty screen areas.
    # control.push_state("BackgroundState")

    # basically the main menu
    control.push_state("StartState")

    # Show the splash screen if it is enabled in the game configuration
    # if prepare.CONFIG.splash == "1":
    #     control.push_state("SplashState")
    #     control.push_state("FadeInTransition")

    # block of code useful for testing
    logging.basicConfig(level=logging.DEBUG)
    if prepare.CONFIG.collision_map == "1":
        logger.info("********* DEBUG OPTIONS ENABLED *********")

        import random
        from core.components.event.actions.player import Player
        from core.components.monster import monsters as monster_db
        from core.components.technique import Technique

        # TODO: fix this player/player1 issue
        # DEBUG ONLY.
        control.player1 = prepare.player1
        action = control.event_engine.execute_action

        action("add_monster", ("txmn_bigfin", 10))
        action("add_monster", ("txmn_dandylion", 10))
        names = {'Omnn', 'Luil', 'Tasv', 'Ykimi', 'Nood', 'Rakck', 'Eisso', 'Pheuth', 'Ouste', 'Iuntu', 'Oechi', 'Yerc', 'Iati', 'Ormth', 'Tad', 'Slit', 'Sloint', 'Uelma', 'Osst', 'Lley', 'Rer', 'Tar', 'Belr', 'Thrias', 'Idaro', 'Dom', 'Endr', 'Ildth', 'Myld', 'Einai', 'Osm', 'Zaert', 'Ekino', 'Aurna', 'Teih', 'Itono', 'Ehona', 'Adeny', 'Dyng', 'Eane', 'Odra', 'Denth', 'End', 'Torph', 'Nysn', 'Iac', 'Schient', 'Orilo', 'Lernd', 'Pollt', 'Aldck', 'Thel', 'Tech', 'Iomy', 'Neih', 'Seis', 'Zis', 'Puit', 'Aormo', 'Fieck', 'Beirr', 'Dynlt', 'Umnt', 'Yare', 'Untth', 'Tons', 'Wart', 'Aene', 'Ranl', 'Smayd', 'Rherd', 'Eumi', 'Pheech', 'Rhal', 'Sez', 'Oathy', 'Kinlt', 'Elmg', 'Elery', 'Rank', 'Soy', 'Leip', 'Quoud', 'Yanga', 'Ati', 'Onalu', 'Souy', 'Tiant', 'Idyno', 'Englt', 'Ciz', 'Yatu', 'Enthrr', 'Rheund', 'Igari', 'Uara', 'Earda', 'Steic', 'Konn', 'Eete', 'Rhond', 'Oskeli', 'Umk', 'Ards', 'Snuck', 'Icha', 'Menn', 'Avesi', 'Baun', 'Ataie', 'Iougho', 'Unty', 'Ineh', 'Steip', 'Sulr', 'Isrt', 'Kek', 'Vers'}
        add_monster = partial(adapter("add_monster"))
        all_monster_slugs = set()
        for i in range(30):
            try:
                slug = all_monster_slugs.pop()
            except KeyError:
                all_monster_slugs = set(monster_db.database["monster"].keys())
                all_monster_slugs.remove('txmn_template')
                slug = all_monster_slugs.pop()
            level = random.randint(1, 21)
            Player().add_monster(control, add_monster(slug, level))

        for monster in control.player1.monsters:
            monster.name = names.pop()

        action("add_item", ("item_potion",))
        action("add_item", ("item_cherry",))
        action("add_item", ("item_capture_device",))

        for i in range(10):
            action("add_item", ("item_super_potion",))
        for monster in control.player1.monsters:
            monster.hp = 100
            monster.current_hp = random.randint(1, monster.hp)
            monster.apply_status(Technique("status_poison"))

        for i in range(100):
            action("add_item", ("item_apple",))
        control.push_state("MonsterInfoState")

    control.main()
    pygame.quit()


def headless():
    """Sets up out headless server and start the game.

    :rtype: None
    :returns: None

    """
    from .control import HeadlessControl

    control = HeadlessControl()
    control.auto_state_discovery()
    control.push_state("HeadlessServerState")
    control.main()
