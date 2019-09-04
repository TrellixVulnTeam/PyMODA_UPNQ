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
import time
from multiprocessing import cpu_count
from typing import List

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QWindow

from maths.multiprocessing.Task import Task


class Scheduler(List[Task]):
    """
    A class which handles scheduling tasks, according to the number of CPU cores.

    As an example, a 4-core, 8-thread machine will run 9 processes
    concurrently and an 8-core, 16-thread CPU will run 17 processes
    concurrently.
    """

    def __init__(self, window: QWindow = None, delay_seconds: float = 0.05):
        super().__init__()
        self.core_count: int = cpu_count() + 1
        self.running_tasks: List[Task] = []

        self.delay_seconds = delay_seconds
        self.delay_millis = int(delay_seconds * 1000)

        if window:
            print("WARNING: use coroutines instead of QTimer.")
            self.timer = QTimer(window)
            self.timer.timeout.connect(self.check_results)

        self.terminated = False
        self.stopped = False
        self.time_start: float = 0

    async def coro_run(self) -> List[tuple]:
        """Run with coroutines."""
        self.time_start = time.time()

        result = await asyncio.gather(*[t.coro_run(self.delay_seconds) for t in self])
        print(f"Time taken (coroutines): {time.time() - self.time_start:.1f} seconds.")

        return result

    def check_results(self):
        if self.all_tasks_finished():
            self.on_all_tasks_completed()

        for t in self.running_tasks:
            t.update()
            if t.finished:
                self.on_task_completed(t)

    def start(self):
        self.time_start = time.time()
        self.timer.start(self.delay_millis)
        self.update_tasks()

    def update_tasks(self):
        tasks = self.tasks_to_run()
        self.running_tasks.extend(tasks)
        [t.start() for t in tasks]

        print(f"Started {len(tasks)} tasks. {self.total_running_tasks()} "
              f"tasks are currently running.")

    def terminate(self):
        if not (self.terminated or self.stopped):
            [t.terminate() for t in self]
            self.terminated = True
            self.stop_timer()

    def stop_timer(self):
        if not self.stopped:
            self.stopped = True
            self.timer.stop()
            self.timer.deleteLater()

    def on_task_completed(self, task):
        self.running_tasks.remove(task)
        self.update_tasks()

    def on_all_tasks_completed(self):
        print(f"All tasks completed in {(time.time() - self.time_start):.1f} seconds.")
        self.stop_timer()

    def available_tasks(self) -> List[Task]:
        """Gets all tasks which are available to run."""
        return [t for t in self if not (t.running or t.finished)]

    def all_tasks_finished(self) -> bool:
        return all([t.finished for t in self])

    def total_running_tasks(self) -> int:
        running = self.running_tasks
        return sum([t.total_tasks() for t in running])

    def tasks_to_run(self) -> List[Task]:
        """
        Gets the tasks that should be run, based on the core count
        and the current number of running tasks.
        """
        # Number of remaining tasks to run.
        available = self.available_tasks()

        # The total number of tasks (including sub-tasks) for each available task.
        task_counts = [t.total_tasks() for t in available]

        running_count = self.total_running_tasks()

        # Number of tasks that can be started without reducing efficiency.
        num_to_run = self.core_count - running_count

        final_task_index = 0
        for i in range(1, len(task_counts) + 1):
            total = sum(task_counts[:i])

            if total <= num_to_run:
                final_task_index = i
            else:
                break

        if final_task_index == 0 and running_count == 0:
            final_task_index += 1

        return available[:final_task_index]
