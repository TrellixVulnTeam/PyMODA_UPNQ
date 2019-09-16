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
from gui.plotting.MatplotlibWidget import MatplotlibWidget
from maths.signals.TimeSeries import TimeSeries


class SignalPlot(MatplotlibWidget):
    """
    Plots the signal, which is a simple set of amplitudes against time.
    """

    def plot(self, data: TimeSeries, clear=True):
        if clear:
            self.clear()
            self.rect_stack.clear()

        self.axes.xaxis.set_label_position("top")
        self.update_xlabel()
        self.update_ylabel()
        self.axes.autoscale(True)

        x = data.times
        y = data.signal

        xlim = (x[0], x[-1])
        self.axes.plot(x, y, linewidth=0.7)
        self.axes.autoscale(False)
        self.axes.set_xlim(xlim)
        self.on_plot_complete()

    def zoom_to(self, rect, save_state=True, trigger_listeners=True):
        """Override the zoom to not change the range of visible y-values."""
        rect.y1, rect.y2 = self.ylim()
        super(SignalPlot, self).zoom_to(rect, save_state, trigger_listeners)

    def get_xlabel(self):
        return "Time (s)"

    def get_ylabel(self):
        return "Value"