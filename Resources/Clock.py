from datetime import datetime as dt

class Clock():
    overall_ticks: float = 0
    start_time_ticks: float = 0

    def start(self):
        self.start_time_ticks = self.get_currenttime_ticks()

    def stop(self):
        self.overall_ticks += self.get_currenttime_ticks() - self.start_time_ticks

    def reset(self):
        self.overall_ticks = 0
        self.start_time_ticks = self.get_currenttime_ticks()

    def get_currenttime_ticks(self) -> int:
        return int(dt.now().timestamp() * 1000)
    
    def check_bounds(self, max_minutes: int) -> bool: 
        return self.overall_ticks > ((max_minutes * 60) * 1000)