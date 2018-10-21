from typing import List
from skyward_api.assignment import Assignment

class SkywardClass():
    def __init__(self, name: str, grades: List[Assignment]) -> None:
        self.name = name
        self.grades = grades

    def grades_to_text(self) -> List[str]:
        return list(
            map(
                lambda grade: str(grade),
                self.grades
            )
        )

    def __str__(self) -> str:
        text_grades = self.grades_to_text()
        text_grades_tabbed = list(
            map(
                lambda string: "\t" + string,
                text_grades
            )
        )

        grades_str = '\n'.join(text_grades_tabbed)

        return "{0}:\n {1}".format(self.name, grades_str)

    def __sub__(self, other: object) -> "SkywardClass":
        if not isinstance(other, SkywardClass):
            raise ValueError("- only defined between SkywardClass object.")
        if self.name != other.name:
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
        return SkywardClass(self.name, diff_grades)
