import pygame

from core import tools
from core.components.ui.graphicbox import GraphicBox


class HorizontalBar(object):
    """ UI Element for filled horizontal bars
    """
    border_filename = "gfx/ui/normal_bar.png"
    border = None
    fg_color = pygame.Color('#61DD55')
    bg_color = pygame.Color('#CCCCCC')

    def __init__(self, value=1.0):
        if self.border is None:
            self.load_graphics()

        rect = (0, 0, 100, 40)
        self.rect = rect
        # self._color = 112, 248, 168
        self.value = value
        self.visible = True

    def load_graphics(self):
        """ Image become class attribute, so is shared.
            Eventually, implement some game-wide image caching
        """
        image = tools.load_and_scale(self.border_filename)
        HorizontalBar.border = GraphicBox(image)

        # @staticmethod
        # def calc_inner_rect(rect):
        #     """ Calculate the inner rect to draw fg_color that fills bar
        #         The values here are calculated based on game scale and
        #         the content of the border image file.
        #
        #     :param rect:
        #     :returns:
        #     """
        #     inner = rect.copy()
        #     inner.top += tools.scale(2)  # top is 2 pixels from top of the raw image
        #     inner.height -= tools.scale(4)  # height is 4 pixels less than the height of the original
        #     inner.left += tools.scale(2)  # left side of bar is 2 pixels from the left of the original
        #     inner.width -= tools.scale(4)  # width is 4 pixels less than the width of the original
        #     return inner

        # def draw(self, surface, rect):
        #     inner = self.calc_inner_rect(rect)
        #     pygame.draw.rect(surface, self.bg_color, inner)
        #     if self.value > 0:
        #         left = inner.left
        #         inner.width *= self.value
        #         inner.left = left
        #         pygame.draw.rect(surface, self.fg_color, inner)
        #     self.border.draw(surface, rect)


class HpBar(HorizontalBar):
    """ HP bar for UI elements.
    """
    border_filename = "gfx/ui/monster/hp_bar.png"
    fg_color = 10, 240, 25
    bg_color = 245, 10, 25

    # @staticmethod
    # def calc_inner_rect(rect):
    #     """ Calculate the inner rect to draw fg_color that fills bar
    #         The values here are calculated based on game scale and
    #         the content of the border image file.
    #
    #     :param rect:
    #     :returns:
    #     """
    #     inner = rect.copy()
    #     inner.top += tools.scale(2)
    #     inner.height -= tools.scale(4)
    #     inner.left += tools.scale(9)
    #     inner.width -= tools.scale(11)
    #     return inner


