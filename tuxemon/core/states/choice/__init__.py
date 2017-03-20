from __future__ import division

from core.components.ui.popup import PopUpMenu
from core.components.ui.font import shadow_text
from core.components.menu.interface import MenuItem


class ChoiceState(PopUpMenu):
    """ Game state with a graphic box and some text in it

    Pressing the action button:
    * if text is being displayed, will cause text speed to go max
    * when text is displayed completely, then will show the next message
    * if there are no more messages, then the dialog will close
    """
    shrink_to_items = True
    escape_key_exits = False

    def startup(self, **kwargs):
        super(ChoiceState, self).startup(**kwargs)
        self.menu = kwargs.get("menu", list())

    def initialize_items(self):
        for key, label, callback in self.menu:
            image = shadow_text(self.font, label)
            item = MenuItem(image, label, None, callback)
            self.add(item)
