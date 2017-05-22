from unittest import TestCase
import os
import sys


from core.states.combat.combat import CombatState, EnqueuedAction
from mock import Mock

# for some test runners that cannot find the tuxemon core
sys.path.insert(0, os.path.join('tuxemon', ))


class CombatQueueTests(TestCase):
    def setUp(self):
        self.s = CombatState
        m0 = Mock()
        t = Mock()
        self.q = map(EnqueuedAction,
                     [
                         (m0, t, None)
                     ])

    def test_sort_order(self):
        state = Mock()
        state._action_queue = self.q
        self.s.sort_action_queue(state)
