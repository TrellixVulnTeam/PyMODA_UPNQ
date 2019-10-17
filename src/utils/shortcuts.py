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

import os
import platform
import sys
from subprocess import Popen, PIPE

system = platform.system()


class OS:
    @staticmethod
    def is_windows() -> bool:
        """
        Returns whether the current OS is Windows.
        """
        return system == "Windows"

    @staticmethod
    def is_linux() -> bool:
        """
        Returns whether the current OS is Linux-based.
        """
        return system == "Linux"

    @staticmethod
    def is_mac_os() -> bool:
        """
        Returns whether the current OS is macOS (hopefully).
        """
        return not (OS.is_linux() or OS.is_windows())  # TODO: Improve implementation.


def create_shortcut() -> str:
    """
    Creates a shortcut to launch PyMODA with current arguments. Can be called on any
    operating system.
    """
    if OS.is_windows():
        status = _create_shortcut_windows()
    elif OS.is_linux():
        status = _create_shortcut_linux()
    elif OS.is_mac_os():
        status = _create_shortcut_mac_os()
    else:
        status = "Operating system unknown. Could not create shortcut."

    return status


def _create_shortcut_windows() -> str:
    """
    Creates a desktop shortcut on Windows, which launches PyMODA with the
    current arguments.
    """
    import os
    import winshell

    path = os.path.join(winshell.desktop(), "PyMODA.lnk")
    with winshell.shortcut(path) as s:
        # Path to Python interpreter.
        s.path = _get_python_interpreter_executable()
        s.description = "Shortcut to launch PyMODA."
        s.arguments = _python_interpreter_arguments()

    return "Created desktop shortcut for PyMODA with current arguments."


def _create_shortcut_linux() -> str:
    """
    Creates a command-line alias to launch PyMODA with current arguments,
    by adding it to ~/.bashrc and ~/.zshrc if it exists or zsh is installed.
    """
    bashrc = _get_abs_path_in_home_folder(".bashrc")  # Bash.
    zshrc = _get_abs_path_in_home_folder(".zshrc")  # Zsh.
    with open(bashrc, "r") as f:
        bash_lines = f.readlines()

    try:
        with open(zshrc, "r") as f:
            zsh_lines = f.readlines()
    except FileNotFoundError:
        if _is_zsh_installed():
            zsh_lines = []
        else:
            zsh_lines = None

    alias_pymoda = "alias pymoda="
    filter_func = lambda line: alias_pymoda not in line
    line_to_add = f"{alias_pymoda}'{_get_python_interpreter_executable()} {_python_interpreter_arguments()}'"

    bash_lines = list(filter(filter_func, bash_lines))
    bash_lines.append(line_to_add)
    with open(bashrc, "w") as f:
        f.writelines(bash_lines)

    if zsh_lines is not None:
        zsh_lines = list(filter(filter_func, zsh_lines))
        zsh_lines.append(line_to_add)

        with open(zshrc, "w") as f:
            f.writelines(zsh_lines)

    return (
        "Created 'pymoda' alias to launch PyMODA with current arguments. "
        "Open a new terminal in any folder and try typing 'pymoda'."
    )


def _get_python_interpreter_executable() -> str:
    return sys.executable


def _create_shortcut_mac_os() -> str:
    return "macOS shortcuts are not supported yet."


def _get_abs_path_in_home_folder(file_name: str) -> str:
    """
    Returns the absolute path to the a particular file
    in the home folder on Linux.
    """
    from pathlib import Path

    home = str(Path.home())
    return os.path.join(home, file_name)


def _python_interpreter_arguments() -> str:
    """
    Returns the path to the main Python file plus all current arguments.
    """
    return " ".join([_abs_path_to_main_py()] + sys.argv[1:])


def _abs_path_to_main_py() -> str:
    """
    Returns the absolute path to the main Python file, `main.py`.
    """
    main_py_name = sys.argv[0].replace("\\", "/").split("/")[-1]
    return os.path.abspath(main_py_name)


def _is_zsh_installed() -> bool:
    """
    Returns whether the Zsh shell is installed on the system, by checking
    whether the output of `which zsh` is empty.
    """
    pipe = Popen("which zsh", shell=True, stdout=PIPE).stdout
    output = pipe.read()

    return bool(output)
