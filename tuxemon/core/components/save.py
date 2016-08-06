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
# Leif Theden <leif.theden@gmail.com>
#
#
# core.components.save Handle save games.
#
#
import datetime
import json
import logging
import os
import tempfile
from base64 import b64encode, b64decode

import pygame
from six import BytesIO

from core import prepare
from core.components.item import Item
from core.components.monster import Monster
from core.components.technique import Technique

# Create a logger for optional handling of debug messages.
logger = logging.getLogger(__name__)

# TODO: move to a config somewhere?
screenshot_fmt = ".png"


class JSONPersistance(object):
    """ This class is used to save and restore game state using a json formatted file
    """
    pass


def encode_surface(surface):
    """ Encode a surface so that it is suitable to be embedded in json

    Encodes a pygame surface into base64 encoded png.

    :type surface: pygame.Surface
    :rtype: dict
    """
    # somewhat convoluted way to store compressed images in json.
    # pygame can only write compressed image data to a file,
    # so we do some gymnastics to get that data into memory.
    # using tostring/fromstring is more straightforward, but
    # only stores uncompressed images.

    # get a temporary file for the image
    fn = tempfile.NamedTemporaryFile(suffix=screenshot_fmt, delete=False)

    # use pygame to save our image
    pygame.image.save(surface, fn.name)

    # read the image data
    with fn as fp:
        data = fp.read()

    # delete the temp file
    os.unlink(fn.name)

    # get the image data as b64 encoded UTF-8 for json
    image_data = b64encode(data).decode('UTF-8')

    return {'fmt': screenshot_fmt, 'data': image_data}


def decode_surface(im_data):
    """ Decode data from json, return surface

    im_data['data'] => basestring, base64 encoded image
    im_data['fmt']  => basestring, filename suffix for image type (ie 'png')

    :type im_data: dict
    :rtype: pygame.Surface
    """
    data = BytesIO(b64decode(im_data['data']))
    return pygame.image.load(data, im_data['fmt'])


def save(player, screenshot, slot, game):
    """Saves the current game state to a file using shelve.

    :param screenshot: Screenshot to embed into the file
    :param player: The player object that contains data to save.
    :param slot: The save slot to save the data to.
    :param game: The core.control.Control object that runs the game.

    :type screenshot: pygame.Surface
    :type player: core.components.player.Player
    :type slot: Integer
    :type game: core.control.Control

    :rtype: None
    :returns: None

    """
    # this dictionary will be serialized to the save file
    json_data = dict()

    # Save a screenshot of the current frame
    json_data['screenshot'] = encode_surface(screenshot)

    tempinv1 = dict()
    for name, itm in player.inventory.items():
        tempinv1[itm['item'].slug] = itm['quantity']
    json_data["inventory"] = tempinv1

    tempmon1 = list()
    for mon1 in player.monsters:
        tempmon1.append(save_monster(mon1))
    json_data["monsters"] = tempmon1

    tempstorage1 = dict()
    for keysstore, valuesstore in tempstorage1.items():
        if keysstore == 'items':
            tempinv = dict()
            for name, itm in valuesstore.items():
                tempinv[itm['item'].slug] = itm['quantity']
            tempstorage1[keysstore] = tempinv
        if keysstore == 'monsters':
            tempmon = list()
            for monstore in valuesstore:
                tempmon.append(save_monster(monstore))
            tempstorage1[keysstore] = tempmon

    json_data['storage'] = tempstorage1
    json_data['current_map'] = game.get_map_name()
    json_data['game_variables'] = player.game_variables
    json_data['tile_pos'] = player.tile_pos
    json_data['player_name'] = player.name
    json_data['time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    with open(prepare.SAVE_PATH + str(slot) + '.save', 'w') as fp:
        json.dump(json_data, fp)

    logger.info("Saving data to save file: " + prepare.SAVE_PATH + str(slot) + '.save')


def save_monster(mon):
    """Prepares a dictionary of the monster to be saved to a file

    :param: None

    :rtype: Dictionary
    :returns: Dictionary containing all the information about the monster

    """
    save_data = dict()
    for key, value in mon.__dict__.items():
        if key == "moves":
            save_data["moves"] = [i.slug for i in mon.moves]
        elif key == "status":
            save_data["status"] = [i.slug for i in mon.status]
        elif key == "body":
            save_data[key] = save_body(mon.body)
        elif key != "sprites" and key != "moveset" and key != "ai":
            save_data[key] = value
    return save_data


def save_body(body):
    """Prepares a dictionary of the body to be saved to a file

    :param: None

    :rtype: Dictionary
    :returns: Dictionary containing all the information about the body

    """
    save_data = dict(body.__dict__)
    return save_data


def load(slot):
    """Loads game state data from a shelved save file.

    :param slot: The save slot to load game data from.
    :type slot: Integer

    :rtype: Dictionary
    :returns: Dictionary containing game data to load.

    """
    # this check is required since opening a shelve will
    # create the pickle is it doesn't already exist.
    # this check prevents a bug where saves are not recorded
    # properly.
    save_path = prepare.SAVE_PATH + str(slot) + '.save'
    if not os.path.exists(save_path):
        return

    with open(save_path) as fp:
        json_data = json.load(fp)

    save_data = dict()

    save_data['inventory'] = [load_item(i) for i in json_data['inventory']]
    save_data['monsters'] = [load_monster(i) for i in json_data['monsters']]

    # TODO: unify loading and game instancing
    # Loop through the storage item keys and re-add the surface.
    tempstorage = dict()
    for keys, values in json_data['storage'].items():
        if keys == 'items':
            tempinv = dict()

            for slug, quant in values.items():
                tempinv1 = dict()
                tempinv1['item'] = Item(slug)
                tempinv1['quantity'] = quant
                tempinv[tempinv1['item'].slug] = tempinv1
            tempstorage[keys] = tempinv

        elif keys == 'monsters':
            tempmon = list()
            for mon in values:
                tempmon1 = Monster()
                tempmon1.load_from_db(mon['slug'])
                load_monster(tempmon1, mon)
                tempmon.append(tempmon1)
            tempstorage[keys] = tempmon
        else:
            tempstorage[keys] = values

    save_data['storage'] = tempstorage
    save_data['game_variables'] = json_data['game_variables']
    save_data['tile_pos'] = json_data['tile_pos']
    save_data['current_map'] = json_data['current_map']
    save_data['player_name'] = json_data['player_name']
    save_data['time'] = json_data['time']
    save_data['screenshot'] = decode_surface(json_data['screenshot'])

    return save_data


def load_item(save_data):
    slot = dict()
    tempinv1['item'] = Item(save_data['slug'])
    tempinv1['quantity'] = save_data['']
    tempinv[tempinv1['item'].slug] = tempinv1
    return slot


def load_monster(save_data):
    """Loads information from saved data

    :param save_data: Dictionary loaded from the json file

    :rtype: None
    :returns: None

    """
    monster = Monster()
    monster.load_from_db(save_data['slug'])
    for key, value in save_data.items():
        if key == "moves":
            monster.moves = [Technique(i) for i in value]
        if key == "status":
            monster.status = [Technique(i) for i in value]
        elif key == "body":
            load_body(save_data, value)
        else:
            setattr(save_data, key, value)
    monster.load_sprites()


def load_body(body, save_data):
    """Loads information from saved data

    :param save_data: Dictionary loaded from the json file

    :rtype: None
    :returns: None

    """
    for key, value in save_data.items():
        setattr(body, key, value)
