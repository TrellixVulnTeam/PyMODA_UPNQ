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
from typing import Tuple

import numpy as np
from nptyping import Array
from scipy.signal import filtfilt, butter


def loop_butter(signal_in: Array, fmin: float, fmax: float, fs: float) -> Tuple[Array, int]:
    max_out = np.max(signal_in)
    optimal_order = 1

    _max = 10 * max_out
    while max_out < _max:
        optimal_order += 1

        sig_out = bandpass_butter(signal_in, optimal_order, fmin, fmax, fs)
        max_out = np.max(sig_out)

    optimal_order -= 1
    sig_out = bandpass_butter(signal_in, optimal_order, fmin, fmax, fs)

    return sig_out, optimal_order


def bandpass_butter(c: Array, n: int, flp: float, fhi: float, fs: float) -> Array:
    fnq = fs / 2

    Wn = np.asarray([flp / fnq, fhi / fnq])
    b, a = butter(n, Wn, btype="bandpass")[:2]

    return filtfilt(b, a, c, padtype="odd", padlen=3 * (max(len(b), len(a)) - 1))
