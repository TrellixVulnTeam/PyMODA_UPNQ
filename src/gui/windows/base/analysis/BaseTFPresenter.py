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
from gui.dialogs.ErrorBox import ErrorBox
from gui.windows.base.analysis.BaseTFView import BaseTFView
from maths.algorithms.preprocessing import preprocess
from maths.signals.TimeSeries import TimeSeries
from utils import stdout_redirect, errorhandling


class BaseTFPresenter:

    def __init__(self, view: BaseTFView):
        self.view = view
        self.is_plotted = False
        self.plot_ampl = True
        self.tasks_completed = 0

        self.signals = None
        self.selected_signal_name = None
        self.open_file = None
        self.freq = None
        self.mp_handler = None
        self.logger = stdout_redirect.WindowLogger(self.on_log)

        errorhandling.subscribe(self.on_error)
        stdout_redirect.subscribe(self.logger)

    def init(self):
        # Add zoom listener to the signal plotting, which is displayed in the top left.
        self.view.signal_plot().add_zoom_listener(self.on_signal_zoomed)

        # Open dialog to select a data file.
        self.view.select_file()

    def calculate(self, calculate_all: bool):
        """
        Perform the main calculation. To connect as a slot,
        use functools.partial:

        `button.clicked.connect(partial(self.calculate, my_argument))`
        """
        pass

    def on_task_completed(self, total, weighting=1):
        self.tasks_completed += weighting
        self.view.update_progress(self.tasks_completed, total)

    def on_all_tasks_completed(self):
        self.tasks_completed = 0

    def on_error(self, exc_type, value, traceback):
        """Called when an error occurs, provided that the debug argument is not in use."""
        self.cancel_calculate()
        ErrorBox(exc_type, value, traceback)

    def on_log(self, text):
        """Called when a log should occur; tells view to display message in log pane."""
        self.view.set_log_text(text)

    def on_signal_zoomed(self, rect):
        """Called when the signal plotting (top left) is zoomed, and sets the x-limits."""
        if rect.is_valid():
            self.view.set_xlimits(rect.x1, rect.x2)
            self.signals.set_xlimits(rect.x1, rect.x2)

    def invalidate_data(self):
        """
        Sets the current data as invalid, so that it is not plotted
        while a calculation is in progress.
        """
        for d in self.signals:
            d.output_data.invalidate()

    def cancel_calculate(self):
        """
        Cancels the calculation of the desired transform(s),
        killing their processes immediately.
        """
        if self.mp_handler:
            self.mp_handler.stop()
        self.view.on_calculate_stopped()
        self.is_plotted = False
        self.on_all_tasks_completed()
        print("Calculation terminated.")

    def on_freq_changed(self, freq):
        """Called when the frequency is changed."""
        self.freq = float(freq)

    def set_frequency(self, freq: float):
        """Sets the frequency of the time-series."""
        self.signals.set_frequency(freq)

    def set_open_file(self, file: str):
        """Sets the name of the data file in use, and loads its data."""
        self.open_file = file
        print(f"Opening {self.open_file}...")
        self.view.update_title()
        self.load_data()

    def load_data(self):
        pass

    def get_window_name(self) -> str:
        """
        Gets the name of this window, adding the currently open file
        if applicable.
        """
        title = self.view.name
        if self.open_file:
            title += f" - {self.open_file}"
        return title

    def on_close(self):
        """Called when the window closes."""
        self.cancel_calculate()
        errorhandling.unsubscribe(self.on_error)

    def get_params(self):
        pass

    def on_data_loaded(self):
        pass

    def on_signal_selected(self, item):
        pass

    def get_total_tasks_count(self) -> int:
        """Returns the total number of tasks in progress."""
        return 0

    def get_selected_signal(self) -> TimeSeries:
        """Returns the currently selected signal as a TimeSeries."""
        return self.signals.get(self.selected_signal_name)

    def plot_preprocessed_signal(self):
        """Plots the preprocessed version of the signal."""
        sig = self.get_selected_signal()

        fmin = self.view.get_fmin()
        fmax = self.view.get_fmax()

        p = preprocess(sig.signal, sig.frequency, fmin, fmax)
        self.view.plot_preproc.clear()
        self.view.plot_preproc.plot(sig.times, sig.signal, p)
