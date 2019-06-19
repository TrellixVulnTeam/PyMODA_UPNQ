#  PyMODA, a Python implementation of MODA (Multiscale Oscillatory Dynamics Analysis).
#  Copyright (C) 2019  Lancaster University
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <https://www.gnu.org/licenses/>.
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog

from gui import resources
from gui.base.BaseUI import BaseUI


class SelectFileDialog(QDialog, BaseUI):
    """
    A dialog allowing the user to select a file. Files can be
    selected via drag-and-drop, or by browsing with the file
    explorer.
    """

    file = None

    def init_ui(self):
        uic.loadUi(resources.get_ui("dialog_select_file"), self)
        self.setup_drops()

    def setup_drops(self):
        """Sets up the label to accept drag-and-drop."""
        drop_target = self.lbl_drag_drop
        drop_target.setAcceptDrops(True)
        drop_target.set_drop_callback(self.set_file)

    def set_file(self, file):
        self.file = file

    def get_file(self):
        """Gets the file path for the selected file."""
        return resources.path_from_file_string(self.file)