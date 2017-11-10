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
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
from functools import partial

from core.components.ui import build_text_item
from core.components.ui.menu import Menu
from core.components.ui.widget import Widget

# Create a logger for optional handling of debug messages.
logger = logging.getLogger(__name__)


class TextInput(Widget):
    def __init__(self, charset=u"ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"):
        super(TextInput, self).__init__()

        # widget for getting input
        self.key_input = Menu()
        self.key_input.menu_items.columns = len(charset) // 6
        self.add_widget(self.key_input)

        # add characters to input
        add_widget = self.key_input.menu_items.add_widget
        for char in charset:
            item = build_text_item(char, partial(self.key_input.add_input_buffer, char))
            add_widget(item)

        # backspace key
        item = build_text_item("<=", self.key_input.backspace)
        add_widget(item)

        # button to confirm the input and close the dialog
        item = build_text_item("END", None)
        add_widget(item)

        self.string_input = self.key_input._input_string
