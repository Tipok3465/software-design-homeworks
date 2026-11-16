from sd_hw_2.domain.models import Criterion, DomainError, Evaluation, Score, Student


class Gradebook:
    def __init__(self) -> None:
        self._students: dict[str, Student] = {}
        self._criteria: dict[str, Criterion] = {}
        self._evaluations: dict[tuple[str, str], Evaluation] = {}

    @property
    def students(self) -> tuple[Student, ...]:
        return tuple(self._students.values())

    @property
    def criteria(self) -> tuple[Criterion, ...]:
        return tuple(self._criteria.values())

    def add_student(self, student: Student) -> None:
        if student.id in self._students:
            raise DomainError(f"Студент с идентификатором {student.id} уже есть")
        self._students[student.id] = student

    def add_criterion(self, criterion: Criterion) -> None:
        if criterion.id in self._criteria:
            raise DomainError(f"Критерий с идентификатором {criterion.id} уже есть")
        self._criteria[criterion.id] = criterion

    def evaluations_for(self, student_id: str) -> tuple[Evaluation, ...]:
        self.get_student(student_id)
        return tuple(
            evaluation for evaluation in self._evaluations.values()
            if evaluation.student_id == student_id
        )

    def assign_score(self, student_id: str, criterion_id: str, score: Score) -> Evaluation:
        key = (student_id, criterion_id)
        if key in self._evaluations:
            raise DomainError("Оценка уже выставлена. Для замены используй исправление")
        return self._save_evaluation(student_id, criterion_id, score)

    def correct_score(self, student_id: str, criterion_id: str, score: Score) -> Evaluation:
        self._require_evaluation(student_id, criterion_id)
        return self._save_evaluation(student_id, criterion_id, score)

    def cancel_score(self, student_id: str, criterion_id: str) -> None:
        self._require_evaluation(student_id, criterion_id)
        del self._evaluations[student_id, criterion_id]

    def _save_evaluation(
        self, student_id: str, criterion_id: str, score: Score
    ) -> Evaluation:
        student = self.get_student(student_id)
        criterion = self._require_criterion(criterion_id)
        evaluation = Evaluation.create(student, criterion, score)
        self._evaluations[student_id, criterion_id] = evaluation
        return evaluation

    def get_student(self, student_id: str) -> Student:
        if student_id not in self._students:
            raise DomainError(f"Студент {student_id} не найден")
        return self._students[student_id]

    def _require_criterion(self, criterion_id: str) -> Criterion:
        if criterion_id not in self._criteria:
            raise DomainError(f"Критерий {criterion_id} не найден")
        return self._criteria[criterion_id]

    def _require_evaluation(self, student_id: str, criterion_id: str) -> None:
        self.get_student(student_id)
        self._require_criterion(criterion_id)
        if (student_id, criterion_id) not in self._evaluations:
            raise DomainError("Оценка не выставлена")
