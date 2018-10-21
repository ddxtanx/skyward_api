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
