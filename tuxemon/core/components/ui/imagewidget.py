from core.components.ui.widget import Widget


class ImageWidget(Widget):
    def __init__(self, image):
        super(ImageWidget, self).__init__()
        self.image = image
        self.irect = image.get_rect()
        self.rect = self.irect.copy()
        self._flag = False

    def _draw(self, surface):
        """

        :type surface: pygame.Surface
        :return:
        """
        self.rect = self.calc_bounding_rect()
        if self.visible:
            # if self._flag:
            #     print(self, self.rect, self.irect, self.bounds)
            surface.blit(self.image, self.rect)