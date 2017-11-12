from core.components.ui.widget import Widget


class ImageWidget(Widget):
    def __init__(self, image):
        super(ImageWidget, self).__init__()
        self.image = image
        self.irect = image.get_rect()
        self.rect = self.irect.copy()

    def _draw(self, surface):
        """

        :type surface: pygame.Surface
        :return:
        """
        if self.visible:
            self.rect = self.calc_screen_rect()
            surface.blit(self.image, self.rect)
