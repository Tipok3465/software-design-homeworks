from copy import deepcopy
from decimal import Decimal

import pytest

from sd_hw_2.application.facade import PosApplication
from sd_hw_2.application.ports import ResultMode, ResultReport
from sd_hw_2.domain.gradebook import Gradebook
from sd_hw_2.domain.models import Criterion, DomainError, Score, Student
from sd_hw_2.domain.results import AllowMissingScores, FinalScoreCalculator, RequireAllScores


class MemoryRepository:
    def __init__(self) -> None:
        self._saved = Gradebook()
        self.save_count = 0

    def load(self) -> Gradebook:
        return deepcopy(self._saved)

    def save(self, gradebook: Gradebook) -> None:
        self._saved = deepcopy(gradebook)
        self.save_count += 1


class RecordingExporter:
    def __init__(self) -> None:
        self.exports: list[tuple[ResultReport, str]] = []

    def export(self, report: ResultReport, destination: str) -> None:
        self.exports.append((report, destination))


def build_app(repository: MemoryRepository, exporter: RecordingExporter) -> PosApplication:
    return PosApplication(
        repository,
        exporter,
        FinalScoreCalculator(AllowMissingScores()),
        FinalScoreCalculator(RequireAllScores()),
    )


@pytest.fixture
def scenario() -> tuple[PosApplication, MemoryRepository, RecordingExporter]:
    repository = MemoryRepository()
    exporter = RecordingExporter()
    app = build_app(repository, exporter)
    app.add_student(Student("s1", "Анна"))
    app.add_criterion(Criterion("practice", "Практика", Decimal(10), Decimal(2)))
    app.add_criterion(Criterion("theory", "Теория", Decimal(20), Decimal(3)))
    return app, repository, exporter


def test_export_uses_current_saved_scores(
    scenario: tuple[PosApplication, MemoryRepository, RecordingExporter],
) -> None:
    app, repository, exporter = scenario
    app.assign_score("s1", "practice", Score(Decimal(8)))
    app.assign_score("s1", "theory", Score(Decimal(15)))

    reopened = build_app(repository, exporter)
    assert [student.id for student in reopened.list_students()] == ["s1"]
    assert [criterion.id for criterion in reopened.list_criteria()] == ["practice", "theory"]
    assert reopened.calculate_result("s1", ResultMode.OFFICIAL).score.value == Decimal(77)
    reopened.correct_score("s1", "practice", Score(Decimal(10)))

    report = app.export_result("s1", ResultMode.OFFICIAL, "result.csv")
    assert report.score.value == Decimal(85)
    assert report.student == Student("s1", "Анна")
    assert report.mode == ResultMode.OFFICIAL
    assert exporter.exports == [(report, "result.csv")]


def test_cancelled_score_disables_official_export_but_not_provisional_export(
    scenario: tuple[PosApplication, MemoryRepository, RecordingExporter],
) -> None:
    app, _, exporter = scenario
    app.assign_score("s1", "practice", Score(Decimal(8)))
    app.assign_score("s1", "theory", Score(Decimal(15)))
    app.cancel_score("s1", "theory")

    with pytest.raises(DomainError, match="theory"):
        app.export_result("s1", ResultMode.OFFICIAL, "official.csv")
    assert not exporter.exports

    report = app.export_result("s1", ResultMode.PROVISIONAL, "provisional.csv")
    assert report.score.value == Decimal(32)
    assert report.score.missing_criterion_ids == ("theory",)
    assert exporter.exports == [(report, "provisional.csv")]


def test_invalid_correction_preserves_saved_score(
    scenario: tuple[PosApplication, MemoryRepository, RecordingExporter],
) -> None:
    app, repository, _ = scenario
    original = app.assign_score("s1", "practice", Score(Decimal(8)))
    save_count = repository.save_count

    with pytest.raises(DomainError, match="превышать"):
        app.correct_score("s1", "practice", Score(Decimal(11)))

    assert repository.save_count == save_count
    assert app.list_evaluations("s1") == (original,)
