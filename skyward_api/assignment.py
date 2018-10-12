import datetime
from typing import Any

class Assignment():
    def __init__(
        self,
        name: str,
        num_points: str,
        total_points: str,
        letter_grade: str,
        date: str
    ) -> None:
        self.name = name
        self.num_points = num_points
        self.total_points = total_points
        self.letter_grade = letter_grade

        spl = date.split("/")
        if len(spl[2]) != 4:
            year = "20" + spl[2]
            spl[2] = year
        self.date = "/".join(spl)

    def points_str(self) -> str:
        return "{0}/{1} ({2})".format(
            self.num_points,
            self.total_points,
            self.letter_grade
        )

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __le__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            my_date = datetime.datetime.strptime(self.date, "%m/%d/%Y")
            their_date = datetime.datetime.strptime(other.date, "%m/%d/%Y")
            return my_date <= their_date
        else:
            return False

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return (self <= other) and not self == other

    def __ge__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return not (self < other)

    def __gt__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return (self >= other) and self != other

    def __str__(self) -> str:
        return "({0}) {1} {2}".format(
            self.date,
            self.name,
            self.points_str()
        )
