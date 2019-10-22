#  PyMODA, a Python implementation of MODA (Multiscale Oscillatory Dynamics Analysis).
#  Copyright (C) 2019 Lancaster University
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
import asyncio

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog

from data import resources
from gui.BaseUI import BaseUI
from maths.num_utils import float_or_none, float_to_str
from utils import args
from utils.settings import Settings


class FrequencyDialog(QDialog, BaseUI):
    """
    A dialog which allows the sampling frequency to be entered.
    """

    select_text = "Select item"
    current_selected = None

    def __init__(self):
        self.frequency: float = None
        self.settings = Settings()
        super(FrequencyDialog, self).__init__()

    def setup_ui(self) -> None:
        uic.loadUi(resources.get("layout:dialog_frequency.ui"), self)

        self.edit_freq.textChanged.connect(self.on_freq_changed)
        self.btn_use_recent.clicked.connect(self.use_recent_freq)
        self.setup_combo()

        asyncio.ensure_future(self.coro_check_args())

    def run_and_get(self) -> float:
        self.exec()
        self.settings.add_recent_freq(self.frequency)
        return self.frequency

    def setup_combo(self):
        values = self.settings.get_recent_freq()
        if values:
            self.combo_recent.addItems([float_to_str(f) for f in values])
        else:
            self.disable_recent_freq()

    async def coro_check_args(self):
        """
        Checks whether the frequency has been set in the commandline arguments and, if so, uses it.
        """
        await asyncio.sleep(0.4)

        freq: float = args.args_freq()
        if freq:
            self.frequency = freq
            self.accept()

    def combo_text(self, freq):
        return f"{freq} Hz"

    def use_recent_freq(self):
        self.frequency = float_or_none(self.combo_recent.currentText())
        self.accept()

    def on_freq_changed(self, value):
        self.frequency = float_or_none(value)
        self.disable_recent_freq()

    def disable_recent_freq(self):
        """
        Disables the UI for selecting a recent frequency, since it may cause users to erroneously
        use a recent frequency instead of the frequency typed into the GUI.
        """
        self.combo_recent.setDisabled(True)
        self.btn_use_recent.setDisabled(True)
