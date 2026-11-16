from sd_hw_2.application.ports import GradebookRepository, ResultExporter, ResultMode, ResultReport
from sd_hw_2.domain.models import Criterion, DomainError, Evaluation, Score, Student
from sd_hw_2.domain.results import FinalScoreCalculator


class PosApplication:
    def __init__(
        self,
        repository: GradebookRepository,
        exporter: ResultExporter,
        provisional_calculator: FinalScoreCalculator,
        official_calculator: FinalScoreCalculator,
    ) -> None:
        self._repository = repository
        self._exporter = exporter
        self._calculators = {
            ResultMode.PROVISIONAL: provisional_calculator,
            ResultMode.OFFICIAL: official_calculator,
        }

    def add_student(self, student: Student) -> None:
        gradebook = self._repository.load()
        gradebook.add_student(student)
        self._repository.save(gradebook)

    def list_students(self) -> tuple[Student, ...]:
        return self._repository.load().students

    def add_criterion(self, criterion: Criterion) -> None:
        gradebook = self._repository.load()
        gradebook.add_criterion(criterion)
        self._repository.save(gradebook)

    def list_criteria(self) -> tuple[Criterion, ...]:
        return self._repository.load().criteria

    def list_evaluations(self, student_id: str) -> tuple[Evaluation, ...]:
        return self._repository.load().evaluations_for(student_id)

    def assign_score(self, student_id: str, criterion_id: str, score: Score) -> Evaluation:
        gradebook = self._repository.load()
        evaluation = gradebook.assign_score(student_id, criterion_id, score)
        self._repository.save(gradebook)
        return evaluation

    def correct_score(self, student_id: str, criterion_id: str, score: Score) -> Evaluation:
        gradebook = self._repository.load()
        evaluation = gradebook.correct_score(student_id, criterion_id, score)
        self._repository.save(gradebook)
        return evaluation

    def cancel_score(self, student_id: str, criterion_id: str) -> None:
        gradebook = self._repository.load()
        gradebook.cancel_score(student_id, criterion_id)
        self._repository.save(gradebook)

    def calculate_result(self, student_id: str, mode: ResultMode) -> ResultReport:
        gradebook = self._repository.load()
        student = gradebook.get_student(student_id)
        score = self._calculators[mode].calculate(gradebook, student_id)
        return ResultReport(student, mode, score)

    def export_result(self, student_id: str, mode: ResultMode, destination: str) -> ResultReport:
        if not destination.strip():
            raise DomainError("Укажи, куда сохранить итог")
        report = self.calculate_result(student_id, mode)
        self._exporter.export(report, destination)
        return report
