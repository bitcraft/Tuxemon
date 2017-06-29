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
import inspect
import logging
import os
import sys
from abc import ABCMeta
from importlib import import_module

import pygame

from core import prepare
from core import tools
from core.components.sprite import SpriteGroup
from core.components.ui.widget import Widget

# Create a logger for optional handling of debug messages.
logger = logging.getLogger(__name__)


class State(object):
    """ This is a mixin class for Widgets.
    
    Add this as a super class to a Widget to allow it to operate on
    the StateStack for game flow control.

    All states should inherit from it. No direct instances of this
    class should be created. Update must be overloaded in the child class.

    Overview of Methods:
       startup       - Called when added to the state stack
       resume        - Called each time state is updated for first time
       update        - Called each frame while state is active
       process_event - Called when there is a new input event
       pause         - Called when state is no longer active
       shutdown      - Called before state is destroyed

    :ivar game: core.control.Control
    :cvar force_draw: If True, state will never be skipped in drawing phase
    :cvar rect: Area of the screen will be drawn on
    """
    __metaclass__ = ABCMeta

    transparent = False  # ignore all background/borders
    force_draw = False  # draw even if completely under another state

    def __init__(self):
        """ Do not override this unless there is a special need.

        All init for the State, loading of config, images, etc should
        be done in State.startup or State.resume, not here.

        :param control: State Manager / Control / Game... all the same
        :returns: None
        """
        super(State, self).__init__()

        # self.game = control  # TODO: rename 'game' to 'control'?
        self.start_time = 0.0
        self.current_time = 0.0
        self.animations = pygame.sprite.Group()  # only animations and tasks
        self.sprites = SpriteGroup()  # all sprites that draw on the screen

    def __repr__(self):
        return "<State: {}".format(self.name)

    @property
    def name(self):
        return self.__class__.__name__

    def load_sprite(self, filename, **kwargs):
        """ Load a sprite and add it to this state

        kwargs can be any value used by pygame Rect, or layer

        :param filename: filename, relative to the resources folder
        :type filename: String
        :param kwargs: Keyword arguments to pass to the Rect constructor
        :returns: core.components.sprite.Sprite
        """
        layer = kwargs.pop('layer', 0)
        sprite = tools.load_sprite(filename, **kwargs)
        self.sprites.add(sprite, layer=layer)
        return sprite

    def update(self, time_delta):
        """ Time update function for state.  Must be overloaded in children.

        :param time_delta: amount of time in fractional seconds since last update
        :type time_delta: Float
        :returns: None
        :rtype: None
        """
        pass

    def startup(self, **kwargs):
        """ Called when scene is added to State Stack

        This will be called:
        * after state is pushed and before next update
        * just once during the life of a state

        Example uses: loading images, configuration, sounds.

        :param kwargs: Configuration options
        :returns: None
        :rtype: None
        """
        pass

    def resume(self):
        """ Called before update when state is newly in focus

        This will be called:
        * before update after being pushed to the stack
        * before update after state has been paused

        After being called, state will begin to receive player input
        Could be called several times over lifetime of state

        Example uses: starting music, open menu, starting animations, timers, etc

        :returns: None
        :rtype: None
        """
        pass

    def pause(self):
        """ Called when state is pushed back in the stack, allowed to pause

        This will be called:
        * after update when state is pushed back
        * before being shutdown

        After being called, state will no longer receive player input
        Could be called several times over lifetime of state

        Example uses: stopping music, sounds, fading out, making state graphics dim

        :returns: None
        :rtype: None
        """
        pass

    def shutdown(self):
        """ Called when state is removed from stack and will be destroyed

        This will be called:
        * after update when state is popped

        Make sure to release any references to objects that may cause
        cyclical dependencies.

        :returns: None
        :rtype: None
        """
        pass


class StateManager(object):
    """ Mix-in style class for use with Control class.

    This is currently undergoing a refactor of sorts, API may not be stable
    """

    def __init__(self):
        """ Currently no need to call __init__
            function is declared to provide IDE with some info on the class only
            this may change in the future, do not rely on this behaviour
        """
        self.done = False
        self.current_time = 0.0
        self.package = ""
        self._state_queue = list()
        self._state_stack = list()
        self._state_dict = dict()
        self._held_keys = list()
        self._state_resume_set = set()
        self._remove_queue = list()

    def reset_controls(self):
        """ Reset the controls during a state change

        This is accomplished by using a list of keys which were
        being held, then sending KEYUP events for each one.

        :returns: None
        """
        current_state = self.current_state
        for event in self._held_keys:
            new_event = pygame.event.Event(pygame.KEYUP, event.dict)
            current_state.process_event(new_event)
        self._held_keys = list()

    def auto_state_discovery(self):
        """ Scan a folder, load states found in it, and register them
        """
        state_folder = prepare.BASEDIR + os.path.join(*self.package.split('.'))
        exclude_endings = (".py", ".pyc", ".pyo", "__pycache__")
        logger.debug("loading game states from {}".format(state_folder))
        for folder in os.listdir(state_folder):
            if any(folder.endswith(end) for end in exclude_endings):
                continue
            for state in self.collect_states_from_path(folder):
                self.register_state(state)

    def register_state(self, state):
        """ Add a state class

        :param state: any subclass of core.state.State
        :returns: None
        """
        name = state.__name__
        logger.debug("loading state: {}".format(state.__name__))
        self._state_dict[name] = state

    @staticmethod
    def collect_states_from_module(import_name):
        """ Given a module, return all classes in it that are a game state

        Abstract Base Classes, those whose metaclass is abc.ABCMeta, will
        not be included in the state dictionary.

        :param import_name: Name of module
        :rtype: collections.Iterable[State]
        """
        classes = inspect.getmembers(sys.modules[import_name], inspect.isclass)

        for c in (i[1] for i in classes):
            if issubclass(c, Widget):
                yield c

    def collect_states_from_path(self, folder):
        """ Load a state from disk, but do not register it

        :param folder: folder to load from
        :returns: Generator of instanced states
        :rtype: collections.Iterable[Class]
        """
        try:
            import_name = self.package + '.' + folder
            import_module(import_name)
            for state in self.collect_states_from_module(import_name):
                yield state
        except Exception as e:
            template = "{} failed to load or is not a valid game package"
            logger.error(e)
            logger.error(template.format(folder))
            raise

    def query_all_states(self):
        """ Return a dictionary of all loaded states

        Keys are state names, values are State classes

        :returns: dictionary of all loaded states
        :rtype: Dict
        """
        return self._state_dict.copy()

    def queue_state(self, state, **kwargs):
        """ Queue a state to be pushed after the top state is popped or replaced

        Use this to chain execution of states, without causing a
        state to get instanced before it is on top of the stack.

        :param state:
        :returns:
        """
        self._state_queue.append((state, kwargs))

    def pop_state(self, state=None):
        """ Pop some state.  Default is the current one.  The previously running state will resume.

        If there is a queued state, then that state will be resumed, not the previous!
        Game loop will end if the last state is popped.

        :param state: The state to remove from stack.  Use None (or omit) for current state.
        :returns: None
        """
        # handle situation where there is a queued state
        if self._state_queue:
            state, kwargs = self._state_queue.pop(0)
            self.replace_state(state, **kwargs)
            return

        # no queued state, so proceed as normal
        if state is None:
            index = 0
        elif state in self._state_stack:
            index = self._state_stack.index(state)
        else:
            logger.critical("Attempted to pop state when state was not active.")
            raise RuntimeError

        if index == 0:
            self.reset_controls()

        try:
            previous = self._state_stack.pop(index)
        except IndexError:
            logger.critical("Attempted to pop state when no state was active.")
            raise RuntimeError

        previous.pause()
        previous.shutdown()

        #  DEBUGGING =========================================================
        # import gc
        # import inspect
        # gc.collect()
        #
        # if not all(map(inspect.isframe, gc.get_referrers(previous))):
        #     logger.debug("State was not able to be GC'd %s" % previous)

        # DEBUGGING =========================================================

        if index == 0 and self._state_stack:
            self.current_state.resume()
        elif index and self._state_stack:
            pass
        else:
            # TODO: make API for quiting the app main loop
            self.done = True
            self._wants_to_exit = True

    def push_state(self, state_name, **kwargs):
        """ Pause currently running state and start new one.

        :param state_name: name of state to start
        :returns: instanced State
        :rtype: core.state.State
        """
        try:
            state = self._state_dict[state_name]
        except KeyError:
            logger.critical('Cannot find state: {}'.format(state_name))
            raise RuntimeError

        previous = self.current_state
        self.reset_controls()

        if previous is not None:
            previous.pause()

        instance = state()
        instance.game = self
        self._state_stack.insert(0, instance)

        instance.controller = self
        instance.startup(**kwargs)
        self._state_resume_set.add(instance)

        return instance

    def replace_state(self, state_name, **kwargs):
        """ Replace the currently running state with a new one

        This is essentially, just a push_state, followed by pop_state(running_state).
        This cannot be used to replace states in the middle of the stack.

        :param state_name: name of state to start
        :returns: New instance
        :rtype: core.state.State
        """
        previous = self._state_stack[0]
        instance = self.push_state(state_name, **kwargs)
        self.pop_state(previous)
        return instance

    @property
    def state_name(self):
        """ Name of state currently running

        TODO: phase this out?

        :returns: string
        :rtype: String
        """
        return self._state_stack[0].name

    @property
    def current_state(self):
        """ The currently running state

        :returns: State
        :rtype: core.state.State
        """
        try:
            return self._state_stack[0]
        except IndexError:
            return None

    @property
    def active_states(self):
        """ Return list of states that are active

        :returns: List of states currently active
        :rtype: List
        """
        return self._state_stack[:]
