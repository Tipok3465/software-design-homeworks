import json
from dataclasses import asdict
from decimal import Decimal, InvalidOperation
from pathlib import Path
from tempfile import NamedTemporaryFile

from sd_hw_2.domain.gradebook import Gradebook
from sd_hw_2.domain.models import Criterion, Score, Student


class JsonGradebookRepository:
    def __init__(self, path: Path) -> None:
        self._path = path

    def load(self) -> Gradebook:
        book = Gradebook()
        try:
            raw = self._path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return book
        except UnicodeError as error:
            raise ValueError("Не удалось прочитать ведомость в кодировке UTF-8") from error

        try:
            data = json.loads(raw, parse_float=Decimal)
            students, criteria, evaluations = (
                data[key] for key in ("students", "criteria", "evaluations")
            )
            if not all(isinstance(items, list) for items in (students, criteria, evaluations)):
                raise ValueError("Ожидались списки студентов, критериев и оценок")
            for student in students:
                book.add_student(Student(student["id"], student["name"]))
            for criterion in criteria:
                book.add_criterion(
                    Criterion(
                        criterion["id"],
                        criterion["name"],
                        Decimal(criterion["max_score"]),
                        Decimal(criterion["weight"]),
                    )
                )
            for evaluation in evaluations:
                book.assign_score(
                    evaluation["student_id"],
                    evaluation["criterion_id"],
                    Score(Decimal(evaluation["score"])),
                )
        except (AttributeError, InvalidOperation, KeyError, TypeError, ValueError) as error:
            raise ValueError(f"Некорректный файл ведомости: {self._path}") from error
        return book

    def save(self, gradebook: Gradebook) -> None:
        data = {
            "students": [asdict(student) for student in gradebook.students],
            "criteria": [
                {
                    "id": criterion.id,
                    "name": criterion.name,
                    "max_score": str(criterion.max_score),
                    "weight": str(criterion.weight),
                }
                for criterion in gradebook.criteria
            ],
            "evaluations": [
                {
                    "student_id": evaluation.student_id,
                    "criterion_id": evaluation.criterion_id,
                    "score": str(evaluation.score.value),
                }
                for student in gradebook.students
                for evaluation in gradebook.evaluations_for(student.id)
            ],
        }
        with NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=self._path.parent, delete=False
        ) as file:
            temporary = Path(file.name)
            try:
                json.dump(data, file, ensure_ascii=False, indent=2)
                file.close()
                temporary.replace(self._path)
            finally:
                temporary.unlink(missing_ok=True)
