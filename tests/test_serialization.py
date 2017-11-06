import unittest
from collections import namedtuple

from core import prepare
from core.components.event.actions.player import Player
from core.components.persistance.serializer import Serializer
from core.control import PygameControl


def adapter(name, *args):
    nt = namedtuple(name, "parameters")

    def func(*args):
        return nt(args)

    return func


def sender(control, klass, name):
    def func(*args):
        a = adapter(name)
        getattr(klass(), name)(control, a(*args), None)

    return func


class SerializationTest(unittest.TestCase):
    def test_encode(self):
        prepare.init()

        print(prepare.BASEDIR)

        control = PygameControl(prepare.ORIGINAL_CAPTION)
        control.auto_state_discovery()

        # background state is used to prevent other states from
        # being required to track dirty screen areas.  for example,
        # in the start state, there is a menu on a blank background,
        # since menus do not clean up dirty areas, the blank,
        # "Background state" will do that.  The alternative is creating
        # a system for states to clean up their dirty screen areas.
        control.push_state("BackgroundState")

        # basically the main menu
        control.push_state("StartState")
        control.push_state("WorldState")

        # TODO: fix this player/player1 issue
        control.player1 = prepare.player1

        add_item = sender(control, Player, "add_item")
        add_item('item_apple')

        add_monster = sender(control, Player, "add_monster")
        add_monster("txmn_tux", 1)

        control.main_loop()

        data = Serializer().dump(control, "control")
        # data["@PygameControl:control"]['time'] = None
        # data["@PygameControl:control"]['@Player:player']['name'] = None

        del control.player1
        # del control.player

        import json
        with open('test.json', 'w') as fp:
            fp.write(json.dumps(data))

        Serializer().load(data, control)

        control.player1 = control.player

        self.assertEquals(None, control.time)
        self.assertEquals(None, control.player.name)
