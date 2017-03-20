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
import math

import pygame as pg

from core import tools


def bubble_text(font, fg, bg, text):
    """ Render text with a thin border

    :type font: pg.font.Font
    :param fg:
    :param bg:
    :param text: Text to draw
    :rtype: pg.Surface
    """
    top = font.render(text, 1, fg)
    back = font.render(text, 1, bg)

    # equals about 1 'pixel'
    offset = tools.scale_sequence((1, 1))
    size = [int(math.ceil(a + b)) for a, b in zip(offset, top.get_size())]
    image = pg.Surface(size, pg.SRCALPHA)

    # simulate a border by blitting the bg around in a circle
    for x in range(int(offset[0] * 2)):
        for y in range(int(offset[1] * 2)):
            image.blit(back, (x, y))

    image.blit(top, offset)
    return image


def shadow_text(font, fg, bg, text):
    """ Render text with a shadow

    :type font: pg.font.Font
    :param fg:
    :param bg:
    :param text: Text to draw
    :rtype: pg.Surface
    """
    top = font.render(text, 1, fg)
    shadow = font.render(text, 1, bg)

    # equals about 1 'pixel'
    offset = tools.scale_sequence((0.5, 0.5))
    size = [int(math.ceil(a + b)) for a, b in zip(offset, top.get_size())]
    image = pg.Surface(size, pg.SRCALPHA)

    image.blit(shadow, offset)
    image.blit(top, (0, 0))
    return image


def iter_render_text(text, font, fg, bg, rect):
    """ Return generator of text, rendered a character at a time, constrained by rect

    :type font: pg.font.Font
    :param text:
    :param fg:
    :param bg:
    :param rect:
    """
    line_height = guess_font_height(font)
    dirty = rect
    for line_index, line in enumerate(constrain_width(text, font, rect.width)):
        top = rect.top + line_index * line_height
        for scrap in build_line(line):
            surface = shadow_text(font, fg, bg, scrap)
            update_rect = surface.get_rect(top=top, left=rect.left)
            yield dirty, update_rect, surface
            dirty = update_rect
        dirty = (0, 0, 0, 0)


def guess_font_height(font):
    """ Estimate the height of a line of the font

    :type font: pg.font.Font
    :return:
    """
    return guess_rendered_text_size("Tg", font)[1]


def guess_rendered_text_size(text, font):
    """ Estimate the size of rendered text

    Faster than rendering
    If only height is needed, use guess_font_height

    :param text:
    :type font: pg.font.Font
    :return:
    """
    return font.size(text)


def build_line(text):
    """ Return generator that yields a line of text one character at a time

    :param text:
    """
    for index in range(1, len(text) + 1):
        yield text[:index]


def constrain_width(text, font, width):
    """ Generator that yields lines of text, constrained by width

    :param text:
    :type font: pg.font.Font
    :param width:
    """
    for line in iterate_word_lines(text):
        scrap = None
        for word in line:
            if scrap:
                test = scrap + " " + word
            else:
                test = word
            token_width = font.size(test)[0]
            if token_width >= width:
                if scrap is None:
                    print('message is too large for width', text)
                    raise RuntimeError
                yield scrap
                scrap = word
            else:
                scrap = test
        else:  # executed when line is too large
            yield scrap


def iterate_words(text):
    """ Generator that yields words of a line of text

    :param text:
    """
    for word in text.split(" "):
        yield word


def iterate_lines(text):
    """ Generator that yields text split by newlines

    :param text:
    """
    for line in text.strip().split("\n"):
        yield line


def iterate_word_lines(text):
    """ Generator that yields at word and line boundries

    :param text:
    """
    for line in iterate_lines(text):
        yield iterate_words(line)


def draw_text(surface, text=None, rect=None, justify="left", align=None,
              font=None, font_size=None, font_color=None):
    """Draws text to a surface. If the text exceeds the rect size, it will
    autowrap. To place text on a new line, put TWO newline characters (\\n)  in your text.

    :param text: The text that you want to draw to the current menu item.
        *Default: core.components.menu.Menu.text*
    :param left: The horizontal pixel position of the text relative to the menu's position.
        *Default: 0*
    :param top: The vertical pixel position of the text relative to the menu's position.
        *Default: 0*
    :param justify: Left, center, or right justify the text. Valid options: "left", "center",
        "right". *Default: "left"*
    :param align: Align the text to the top, middle, or bottom of the menu. Valid options:
        "top", "middle", "bottom". *Default: "top"*
    :param font_size: Size of the font in pixels BEFORE scaling is done. *Default: 4*
    :param font_color: Tuple of RGB values of the font _color to use. *Default: (10, 10, 10)*

    :type text: String
    :type left: Integer
    :type top: Integer
    :type justify: String
    :type align: String
    :type font_size: Integer
    :type font_color: Tuple

    :rtype: None
    :returns: None

    **Examples:**

    >>> draw_text(screen "boo", justify="center", align="middle")

    .. image:: images/menu/justify_center.png

    """
    left, top, width, height = rect

    if not font_color:
        font_color = (0, 0, 0)

    # Create a text surface so we can determine how many pixels
    # wide each character is
    text_surface = font.render(text, 1, font_color)

    # Calculate the number of pixels per letter based on the size
    # of the text and the number of characters in the text

    if not text:
        return

    pixels_per_letter = text_surface.get_width() / len(text)

    # Create a list of the lines of text as well as a list of the
    # individual words so we can check each line's length in pixels
    lines = []
    wordlist = []

    # Loop through each word in the text and add it to the word list
    for word in text.split():

        # If there is a linebreak in this word, then split it up into a list separated by \n
        if "\\n" in word:
            w = word.split("\\n")

            # Loop through the list and every time we encounter a blank string, then that is
            # a new line. So we append the current line and reset the word list for a new line
            for item in w:
                if item == '':
                    # This is a new line!
                    lines.append(" ".join(wordlist))
                    wordlist = []
                # If we encounter an actual word, then just append it to the word list
                else:
                    wordlist.append(item)

        # If there's no line break, continue normally to word wrap
        else:

            # Append the word to the current line
            wordlist.append(word)

            # Here, we convert the list into a string separated by spaces and multiply
            # the number of characters in the string by the number of pixels per letter
            # that we calculated earlier. This will let us know how large the text will
            # be in pixels.
            if len(" ".join(wordlist)) * pixels_per_letter > width:
                # If the size exceeds the width of the menu, then append the line to the
                # list of lines, but stripping off the last word we added (because this
                # was the word that made us exceed the menubox's size.
                lines.append(" ".join(wordlist[:-1]))

                # Reset the wordlist for the next line and add the word we stripped off
                wordlist = []
                wordlist.append(word)

    # If the last line is not blank, then append it to the list
    if " ".join(wordlist) != '':
        lines.append(" ".join(wordlist))

    # If the justification was set, handle the position of the text automatically
    if justify == "center":
        if lines:
            left = (left + (width / 2)) - \
                   ((len(lines[0]) * pixels_per_letter) / 2)
        else:
            left = 0

    elif justify == "right":
        raise NotImplementedError("Needs to be implemented")

    # If text alignment was set, handle the position of the text automatically
    if align == "middle":
        top = (top + (height / 2)) - \
              ((text_surface.get_height() * len(lines)) / 2)

    elif align == "bottom":
        raise NotImplementedError("Needs to be implemented")

    # Set a spacing variable that we will add to to space each line.
    spacing = 0
    for item in lines:
        line = font.render(item, 1, font_color)

        surface.blit(line, (left, top + spacing))
        spacing += line.get_height()  # + self.line_spacing
