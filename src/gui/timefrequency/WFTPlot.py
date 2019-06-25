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
import windowFT
import matlab
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

from gui.base.components.PlotComponent import PlotComponent
from maths.TimeSeries import TimeSeries
from packages.wft.for_redistribution_files_only import windowFT


class WFTPlot(PlotComponent):

    def plot(self, data: TimeSeries):
        self.wft_plot(data)
        self.axes.autoscale(False)
        self.on_initial_plot_complete()

    def get_xlabel(self):
        return "Time (s)"

    def get_ylabel(self):
        return "Frequency (Hz)"

    def wft_plot(self, data: TimeSeries):
        package = windowFT.initialize()

        fs = data.frequency
        t = data.times
        # sig = np.cos(2 * np.pi * 3 * t + 0.75 * np.sin(2 * np.pi * t / 5))
        sig = data.data
        sig_matlab = sig.tolist()

        A = matlab.double([sig_matlab])
        fs_matlab = matlab.double([fs])

        w, l = package.windowFT(A, fs_matlab, nargout=2)

        a = np.asarray(w)
        gh = np.asarray(l)

        self.axes.pcolormesh(t, gh, np.abs(a))
        self.axes.set_title('STFT Magnitude')
