import re


class Attendance:
    pattern = r'\((\d*)\/(\d*)\)'

    def __init__(self, data):
        match = re.search(self.pattern, data)
        if match:
            self.raids_attended = int(match[1])
            self.raids_available = int(match[2])
            self.attendance = self.raids_attended / self.raids_available

    def __str__(self):
        return f"{self.attendance * 100:.0f}% ({self.raids_attended}/{self.raids_available})"

    def __lt__(self, other):
        if isinstance(other, Attendance):
            return self.attendance < other.attendance
        if isinstance(other, int) or isinstance(other, float):
            return self.attendance * 100 < other

    def __gt__(self, other):
        if isinstance(other, Attendance):
            return self.attendance > other.attendance
        if isinstance(other, int) or isinstance(other, float):
            return self.attendance * 100 > other

    def __le__(self, other):
        if isinstance(other, Attendance):
            return self.attendance <= other.attendance
        if isinstance(other, int) or isinstance(other, float):
            return self.attendance * 100 <= other

    def __ge__(self, other):
        if isinstance(other, Attendance):
            return self.attendance >= other.attendance
        if isinstance(other, int) or isinstance(other, float):
            return self.attendance * 100 >= other

    def __eq__(self, other):
        if isinstance(other, Attendance):
            return self.attendance == other.attendance
        if isinstance(other, int) or isinstance(other, float):
            return self.attendance * 100 == other

    def __hash__(self):
        return hash(self.attendance)
