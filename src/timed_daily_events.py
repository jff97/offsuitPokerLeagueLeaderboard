import threading
from datetime import datetime, timedelta
from typing import Callable, List

class DailyTimeScheduler:
    def __init__(self, times: List[str], task: Callable):
        self.times = times
        self.task = task
        self._schedule_next_run()

    def _get_next_run_time(self) -> datetime:
        now = datetime.now()
        next_times = []

        for t in self.times:
            hour, minute = map(int, t.split(":"))
            run_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if run_time <= now:
                run_time += timedelta(days=1)
            next_times.append(run_time)

        return min(next_times)

    def _run_and_reschedule(self):
        self.task()
        self._schedule_next_run()

    def _schedule_next_run(self):
        next_time = self._get_next_run_time()
        delay = (next_time - datetime.now()).total_seconds()
        threading.Timer(delay, self._run_and_reschedule).start()
        print(f"[Scheduler] Next run scheduled at {next_time.strftime('%Y-%m-%d %H:%M:%S')}")
