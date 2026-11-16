from decimal import Decimal

import pytest

from sd_hw_2.domain.gradebook import Gradebook
from sd_hw_2.domain.models import Criterion, DomainError, Score, Student
from sd_hw_2.domain.results import AllowMissingScores, FinalScoreCalculator, RequireAllScores


@pytest.fixture
def gradebook() -> Gradebook:
    book = Gradebook()
    book.add_student(Student("s1", "Анна"))
    book.add_student(Student("s2", "Ольга"))
    book.add_criterion(Criterion("practice", "Практика", Decimal(10), Decimal(2)))
    book.add_criterion(Criterion("theory", "Теория", Decimal(20), Decimal(3)))
    return book


def test_weighted_result_uses_current_scores_and_ignores_other_students(
    gradebook: Gradebook,
) -> None:
    gradebook.assign_score("s1", "practice", Score(Decimal(8)))
    gradebook.assign_score("s1", "theory", Score(Decimal(15)))
    gradebook.assign_score("s2", "practice", Score(Decimal(10)))
    calculator = FinalScoreCalculator(RequireAllScores())
    assert calculator.calculate(gradebook, "s1").value == Decimal(77)

    gradebook.correct_score("s1", "practice", Score(Decimal(10)))
    assert calculator.calculate(gradebook, "s1").value == Decimal(85)


def test_cancellation_makes_result_provisional_again(gradebook: Gradebook) -> None:
    gradebook.assign_score("s1", "practice", Score(Decimal(8)))
    gradebook.assign_score("s1", "theory", Score(Decimal(0)))
    official = FinalScoreCalculator(RequireAllScores())
    assert official.calculate(gradebook, "s1").value == Decimal(32)

    gradebook.cancel_score("s1", "theory")
    provisional = FinalScoreCalculator(AllowMissingScores()).calculate(gradebook, "s1")
    assert provisional.value == Decimal(32)
    assert provisional.missing_criterion_ids == ("theory",)
    with pytest.raises(DomainError, match="theory"):
        official.calculate(gradebook, "s1")


def test_empty_rubric_has_no_final_score() -> None:
    gradebook = Gradebook()
    gradebook.add_student(Student("s1", "Анна"))
    with pytest.raises(DomainError, match="Рубрикатор пуст"):
        FinalScoreCalculator(AllowMissingScores()).calculate(gradebook, "s1")
