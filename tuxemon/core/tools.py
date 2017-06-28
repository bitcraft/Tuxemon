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
#
"""

This module is a random collection of things that don't currently
have a home somewhere else.  It is the Tuxemon codebase junk drawer.

"""
from __future__ import absolute_import
from __future__ import division

import logging
import operator
import os.path
from itertools import product
import re

import pygame

from core import prepare
from core.components import pyganim
from core.platform import mixer

# Create a logger for optional handling of debug messages.
logger = logging.getLogger(__name__)

# map of axis names to the named edges along a pygame rect
axis_rect_edge_map = {"y": {"top", "bottom"}, "x": {"left", "right"}}

# font cache, since it is used often and slow to load
_font_cache = dict()


def calc_scroll_thing(rect, group, bounds):
    """ Very poorly named.  See description.

    Given a rect, group rect and bounding box, return a dictionary
    that describes the movement along any axis that will cause the
    rect to be contained fully inside the bounds.

    :type rect: pygame.Rect
    :type group: pygame.Group
    :type bounds: pygame.Rect
    :rtype: dict
    """
    # check if the selected thing is outside the screen
    if bounds.contains(rect):
        return None

    # get a list of axes that are allowed to scroll
    scroll_axes = calc_scroll_freedom(group, bounds)

    # only calculate changes if the menu is able to scroll
    if scroll_axes:
        # get which quadrant the selected item is in in relation to the screen
        quadrants = calc_quadrant(rect, bounds)

        diff = dict()
        for axis in scroll_axes:
            # for each axis, get the quadrant that the menu item is in
            # then determine the distance needed to move the scrollable
            # region so that the edges match and rect is contained in bounds
            d = axis_rect_edge_map[axis].intersection(quadrants).pop()
            diff[d] = getattr(bounds, d) - getattr(rect, d)

        return diff

    else:
        return None


def calc_scroll_freedom(rect, parent):
    """ Very poorly named.  See description.

    Given a rect and a parent, return any axis that the
    the rect could move, if constrained by the parent rect.

    This is used to determine valid movements for scrolling
    regions.

    :type rect: pygame.Rect
    :type parent: pygame.Rect
    :rtype: list
    """
    x = rect.width > parent.width
    y = rect.height > parent.height

    if x and y:
        return {'x', 'y'}
    elif x:
        return {'x'}
    elif y:
        return {'y'}
    else:
        return None


def calc_quadrant(rect, parent):
    """ Determine which quadrant (n, e, s, w) the rect is in

    Uses pygame Rect terms: "top bottom left right"

    If return value is empty set, then the rects overlap exactly

    :type rect: pygame.Rect
    :type parent: pygame.Rect
    :rtype: set
    """
    q = set()

    if rect.centerx > parent.centerx:
        q.add("right")
    elif rect.centerx < parent.centerx:
        q.add("left")

    if rect.centery > parent.centery:
        q.add("bottom")
    elif rect.centery < parent.centery:
        q.add("top")

    return q


def strip_from_sheet(sheet, start, size, columns, rows=1):
    """ Strips individual frames from a sprite sheet given a start location,
    sprite size, and number of columns and rows."""
    frames = []
    for j in range(rows):
        for i in range(columns):
            location = (start[0] + size[0] * i, start[1] + size[1] * j)
            frames.append(sheet.subsurface(pygame.Rect(location, size)))
    return frames


def strip_coords_from_sheet(sheet, coords, size):
    """ Strip specific coordinates from a sprite sheet."""
    frames = []
    for coord in coords:
        location = (coord[0] * size[0], coord[1] * size[1])
        frames.append(sheet.subsurface(pygame.Rect(location, size)))
    return frames


def get_cell_coordinates(rect, point, size):
    """ Find the cell of size, within rect, that point occupies."""
    cell = [None, None]
    point = (point[0] - rect.x, point[1] - rect.y)
    cell[0] = (point[0] // size[0]) * size[0]
    cell[1] = (point[1] // size[1]) * size[1]
    return tuple(cell)


def cursor_from_image(image):
    """ Take a valid image and create a mouse cursor."""
    colors = {(0, 0, 0, 255): "X",
              (255, 255, 255, 255): "."}
    rect = image.get_rect()
    icon_string = []
    for j in range(rect.height):
        this_row = []
        for i in range(rect.width):
            pixel = tuple(image.get_at((i, j)))
            this_row.append(colors.get(pixel, " "))
        icon_string.append("".join(this_row))
    return icon_string


def transform_resource_filename(filename):
    """ Appends the resource folder name to a filename

    :param filename: String
    :rtype: basestring
    """
    return os.path.join(prepare.BASEDIR, 'resources', filename)


def load_and_scale(filename):
    """ Load an image and scale it according to game settings

    * Filename will be transformed to be loaded from game resource folder
    * Will be converted if needed.
    * Scale factor will match game setting.

    :param filename:
    :rtype: pygame.Surface
    """
    return scale_surface(load_image(filename), prepare.SCALE)


def smart_convert(image):
    """ Given an unconverted file, determine if it has transparent pixels
    and return a converted image, with per-pixel alpha if needed.

    :param image: pygame.Surface
    :rtype: pygame.Surface
    """
    # get number of opaque pixels in the image
    px = pygame.mask.from_surface(image, 127).count()

    # there are no transparent pixels in the image because
    # the number of pixels matches the number of opaque pixels
    if px == operator.mul(*image.get_size()):
        return image.convert()

    return image.convert_alpha()


def load_image(filename):
    """ Load image from the resources folder

    * Filename will be transformed to be loaded from game resource folder
    * Will be converted if needed.

    This is a "smart" loader, and will convert files in the best way,
    but is slightly slower than just loading.  Its important that
    this is not called too often (like once per draw!)

    :param filename: String
    :rtype: pygame.Surface
    """
    filename = transform_resource_filename(filename)
    return smart_convert(pygame.image.load(filename))


def load_font(filename, size):
    """ Load font from the resources folder

    * Filename will be transformed to be loaded from game resource folder
    * Font will be no smaller thn the configured smallest size
    * Font will be scaled to fit the screen

    :param filename: String
    :type size: int
    :rtype: pygame.font.Font
    """
    # the next line determines where fonts are stored
    filename = os.path.join('font', filename)
    filename = transform_resource_filename(filename)
    size = min(prepare.MIN_FONT_SIZE, size)
    font_size = scale(size)
    return pygame.font.Font(filename, font_size)


def get_cached_font(filename, size):
    """ Attempt to load a font from the cache.  Load if not found.

    :param filename: String
    :type size: int
    :rtype: pygame.font.Font
    """
    key = filename, size
    try:
        return _font_cache[key]
    except KeyError:
        font = load_font(filename, size)
        _font_cache[key] = font
        return font


def load_default_font():
    """ Convenience function to load the default font

    :rtype: pygame.font.Font
    """
    return get_cached_font(prepare.DEFAULT_FONT_FILENAME, prepare.DEFAULT_FONT_SIZE)


def load_sprite(filename, **rect_kwargs):
    """ Load an image from disk and return a pygame sprite

    Image name will be transformed and converted
    Rect attribute will be set

    Any keyword arguments will be passed to the get_rect method
    of the image for positioning the rect.

    :param filename: Filename to load
    :rtype: core.components.sprite.Sprite
    """
    from core.components.sprite import Sprite
    sprite = Sprite()
    sprite.image = load_and_scale(filename)
    sprite.rect = sprite.image.get_rect(**rect_kwargs)
    return sprite


def new_scaled_rect(*args, **kwargs):
    """ Create a new rect and scale it

    :param args: Normal args for a Rect
    :param kwargs: Normal kwargs for a Rect
    :rtype: pygame.rect.Rect
    """
    rect = pygame.Rect(*args, **kwargs)
    return scale_rect(rect)


def scale_rect(rect, factor=prepare.SCALE):
    """ Scale a rect.  Returns a new object.

    :param rect: pygame Rect
    :param factor: int
    :rtype: pygame.rect.Rect
    """
    return pygame.Rect([i * factor for i in list(rect)])


def scale_surface(surface, factor):
    """ Scale a surface.  Just a shortcut.

    :returns: Scaled surface
    :rtype: pygame.Surface
    """
    return pygame.transform.scale(surface, [int(i * factor) for i in surface.get_size()])


def load_frames_files(directory, name):
    """ Load animation that is a collection of frames

    For example, water00.png, water01.png, water03.png

    :type directory: str
    :type name: str

    :rtype: generator
    """
    scale = prepare.SCALE
    for animation_frame in os.listdir(directory):
        pattern = name + "\.[0-9].*"
        if re.findall(pattern, animation_frame):
            frame = pygame.image.load(directory + "/" + animation_frame).convert_alpha()
            frame = pygame.transform.scale(frame, (frame.get_width() * scale, frame.get_height() * scale))
            yield frame


def create_animation(frames, duration, loop):
    """ Create animation from frames, a list of surfaces

    :param frames:
    :param duration:
    :param loop:
    :return:
    """
    data = [(f, duration) for f in frames]
    animation = pyganim.PygAnimation(data, loop=loop)
    conductor = pyganim.PygConductor({'animation': animation})
    return animation, conductor


def load_animation_from_frames(directory, name, duration, loop=False):
    """ Load animation from a collection of frame files

    :param directory:
    :param name:
    :param duration:
    :param loop:

    :return:
    """
    frames = load_frames_files(directory, name)
    return create_animation(frames, duration, loop)


def scale_tile(surface, tile_size):
    """ Scales a map tile based on resolution.

    :type surface: pygame.Surface
    :type tile_size: int
    :rtype: pygame.Surface
    """
    if type(surface) is pygame.Surface:
        surface = pygame.transform.scale(surface, tile_size)
    else:
        surface.scale(tile_size)

    return surface


def scale_sprite(sprite, ratio):
    """ Scale a sprite's image in place

    :type sprite: pygame.Sprite
    :param ratio: amount to scale by
    :rtype: core.components.sprite.Sprite
    """
    center = sprite.rect.center
    sprite.rect.width *= ratio
    sprite.rect.height *= ratio
    sprite.rect.center = center
    sprite._original_image = pygame.transform.scale(sprite._original_image, sprite.rect.size)
    sprite._needs_update = True


def scale_sequence(sequence):
    """ Scale the thing

    :param sequence:
    :rtype: list
    """
    return [i * prepare.SCALE for i in sequence]


def scale(number):
    """ Scale the thing

    :param number: int
    :rtype: int
    """
    return prepare.SCALE * number


def convert_alpha_to_colorkey(surface, colorkey=(255, 0, 255)):
    """ Convert image with perpixel alpha to normal surface with colorkey

    This is a crude hack that only works well with images that do not
    have alpha blended antialiased edges.  Using this function on such
    images will result in discoloration of edges.

    :param surface: Some image to change
    :type surface: pygame.Surface
    :param colorkey: Colorkey to use for transparency
    :type colorkey: Sequence or pygame.Color

    :returns: Modified surface
    :rtype: pygame.Surface
    """
    image = pygame.Surface(surface.get_size())
    image.fill(colorkey)
    image.set_colorkey(colorkey)
    image.blit(surface, (0, 0))
    return image


def make_shadow_surface(surface, color=(0, 0, 0, 96)):
    """create a surface suitable to be used as a shadow

    slow.  use once and cache the result
    image must have alpha channel or results are undefined
    """
    w, h = surface.get_size()
    shad = pygame.Surface((w, h), flags=pygame.SRCALPHA)
    mask = pygame.mask.from_surface(surface)
    for pixel in product(range(w), range(h)):
        if mask.get_at(pixel):
            shad.set_at(pixel, color)
    return shad


def check_parameters(parameters, required=0, exit=True):
    """
    Checks to see if a given list has the required number of items
    """
    if len(parameters) < required:
        import inspect
        calling_function = inspect.stack()[1][3]
        logger.error("'" + calling_function + "' requires at least " + str(required) + "parameters.")
        if exit:
            import sys
            sys.exit(1)
        return False

    else:
        return True


def load_sound(filename):
    """ Load a sound from disk

    The required path will be appended to the filename

    :param filename: filename to load
    :type filename: basestring
    :rtype: core.platform.mixer.Sound
    """

    class DummySound(object):
        def play(self):
            pass

    filename = transform_resource_filename(filename)

    # on some platforms, pygame will silently fail loading
    # a sound if the filename is incorrect so we check here
    if not os.path.exists(filename):
        msg = 'audio file does not exist: {}'.format(filename)
        logger.error(msg)
        return DummySound()

    try:
        return mixer.Sound(filename)
    except MemoryError:
        # raised on some systems if there is no mixer
        logger.error('memoryerror, unable to load sound')
        return DummySound()
    except pygame.error as e:
        # pick one:
        # * there is no mixer
        # * sound has invalid path
        # * mixer has no output (device ok, no speakers)
        logger.error(e)
        logger.error('unable to load sound')
        return DummySound()


def calc_dialog_rect(screen_rect):
    """ Return a rect that is the area for a dialog box on the screen

    :param screen_rect:
    :return:
    """
    rect = screen_rect.copy()
    rect.height *= .25
    rect.width *= .8
    rect.center = screen_rect.centerx, screen_rect.bottom - rect.height
    return rect


def open_dialog(game, text, menu=None):
    """ Open a dialog along the bottom edge of the screen

    This dialog is typically used for spoken words between characters.

    :type game: core.control.Control
    :param text: list of strings
    :param menu:

    :rtype: core.states.dialog.DialogState
    """
    rect = calc_dialog_rect(game.screen.get_rect())
    return game.push_state("DialogState", text=text, rect=rect, menu=menu)


def open_info_dialog(game, text, menu=None):
    """ Open a dialog in the center of the screen

    This dialog is typically used for messages from the game to the player.

    :type game: core.control.Control
    :param text: list of strings
    :param menu:

    :rtype: State
    """
    state = game.push_state("DialogState", text=text, menu=menu)
    state.shrink_to_items = True
    return state
