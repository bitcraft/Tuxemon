from __future__ import division

import logging
import math

import pygame

from core import prepare

# Create a logger for optional handling of debug messages.
logger = logging.getLogger(__name__)

__all__ = ('GraphicBox', 'draw_text')


def layout(scale):
    def func(area):
        return [scale * i for i in area]

    return func


layout = layout(prepare.SCALE)


def guest_font_height(font):
    return guess_rendered_text_size("Tg", font)[1]


def guess_rendered_text_size(text, font):
    return font.size(text)


def shadow_text(font, fg, bg, text):
    top = font.render(text, 1, fg)
    shadow = font.render(text, 1, bg)

    offset = layout((0.5, 0.5))
    size = [int(math.ceil(a + b)) for a, b in zip(offset, top.get_size())]
    image = pygame.Surface(size, pygame.SRCALPHA)

    image.blit(shadow, offset)
    image.blit(top, (0, 0))
    return image


def iter_render_text(text, font, fg, bg, rect):
    line_height = guest_font_height(font)
    dirty = rect
    for line_index, line in enumerate(constrain_width(text, font, rect.width)):
        top = rect.top + line_index * line_height
        for scrap in build_line(line):
            surface = shadow_text(font, fg, bg, scrap)
            update_rect = surface.get_rect(top=top, left=rect.left)
            yield dirty, update_rect, surface
            dirty = update_rect
        dirty = (0, 0, 0, 0)


def build_line(text):
    for index in range(1, len(text) + 1):
        yield text[:index]


def constrain_width(text, font, width):
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
                    logger.error('message is too large for width', text)
                    raise RuntimeError
                yield scrap
                scrap = word
            else:
                scrap = test
        else:  # executed when line is too large
            yield scrap


def iterate_words(text):
    for word in text.split(" "):
        yield word


def iterate_lines(text):
    for line in text.strip().split("\n"):
        yield line


def iterate_word_lines(text):
    for line in iterate_lines(text):
        yield iterate_words(line)
