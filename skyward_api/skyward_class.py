from typing import Dict, List, Union
from skyward_api.assignment import Assignment

class SkywardClass():
    """Object for class with grades.

    Parameters
    ----------
    name : str
        Skyward name of class (e.g. "CLASS NAME (Period #) TEACHER NAME").
    grades : List[Assignment]
        Grades in the class.

    Attributes
    ----------
    class_name : str
        Name of the class (e.g. "CLASS NAME").
    period : int
        Period of class (e.g. #).
    teacher : type
        Teacher of class (e.g. "TEACHER NAME").
    grades : type
        Grades in the class.

    """
    def __init__(self, name: str, grades: List[Assignment]) -> None:
        split_1 = name.split(" (")
        class_name = split_1[0]
        split_2 = split_1[1].split(") ")
        period = int(split_2[0].replace("Period ", ""))
        teacher = split_2[1]

        self.class_name = class_name
        self.period = period
        self.teacher = teacher
        self.grades = grades

    def add_grade(self, grade: Assignment) -> None:
        """Adds a grade to class grades.

        Parameters
        ----------
        grade : Assignment
            Grade to add.

        Side-Effects
        ------------
        Grade is added to self.grades.

        """
        self.grades.append(grade)

    def sort_grades_by_date(self) -> None:
        """Sorts grades in order they appear in Skyward (most recent first).

        Side-Effects
        ------------
        self.grades is now sorted by descending date.

        """
        self.grades = sorted(self.grades, reverse=True)

    def skyward_title(self) -> str:
        """Returns the title Skyward gave to the class.

        Returns
        -------
        str
            The title Skyward gave to the class ("CLASS NAME (Period #) TEACHER NAME").

        """
        return "{0} (Period {1}) {2}".format(
            self.class_name,
            self.period,
            self.teacher
        )

    def grades_to_text(self) -> List[str]:
        """Converts the Assignment objects to their text representations.

        Returns
        -------
        List[str]
            Assignments as text.

        """
        return list(
            map(
                lambda grade: str(grade),
                self.grades
            )
        )

    def __str__(self) -> str:
        """Represents the SkywardClass as a string.

        Returns
        -------
        str
            SkywardClass object represented as a string.

        """
        text_grades = self.grades_to_text()
        text_grades_tabbed = list(
            map(
                lambda string: "\t" + string,
                text_grades
            )
        )

        grades_str = '\n'.join(text_grades_tabbed)

        return "{0}:\n {1}".format(self.skyward_title(), grades_str)

    def __sub__(self, other: object) -> "SkywardClass":
        """Set difference of grades.

        Parameters
        ----------
        other : object
            Other class to subtract.

        Returns
        -------
        SkywardClass
            Skyward class with grades that are the set difference of self.grades and
            other.grades. Must be the same class as self.

        Raises
        -------
        ValueError
            other was not a SkywardClass or it was not the same Skyward class as self.

        """
        if not isinstance(other, SkywardClass):
            raise ValueError("- only defined between SkywardClass object.")
        if self.skyward_title() != other.skyward_title():
            raise ValueError(
                (
                    "- only defined between the same SkywardClasses. Your "
                    " two classes have different names."
                )
            )
        my_grades = self.grades
        their_grades = other.grades
        diff_grades = [
            grade
            for grade in my_grades if grade not in their_grades
        ]
        return SkywardClass(self.skyward_title(), diff_grades)

    def __add__(self, other: "SkywardClass") -> "SkywardClass":
        """Class with grades as the set union of the arguments grades.

        Parameters
        ----------
        other : SkywardClass
            Other SkywardClass representing the **same** class as self.

        Returns
        -------
        "SkywardClass"
            SkywardClass with grades from both self and other.

        Raises
        -------
        ValueError
            other did not represent the same class as self.

        """
        if self.skyward_title() != other.skyward_title():
            raise ValueError("+ only defined between same classes.")
        return SkywardClass(self.skyward_title(), self.grades + other.grades)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, SkywardClass):
            raise ValueError("< only defined between two SkywardClasses")
        return self.period < other.period

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, SkywardClass):
            raise ValueError("> only defined between two SkywardClasses")
        return not (self < other) and (self.period != other.period)

    def __le__(self, other: object) -> bool:
        return not self > other

    def __ge__(self, other: object) -> bool:
        return not self < other
