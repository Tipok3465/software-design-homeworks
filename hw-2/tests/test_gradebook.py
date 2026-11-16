from decimal import Decimal

import pytest

from sd_hw_2.domain.gradebook import Gradebook
from sd_hw_2.domain.models import Criterion, DomainError, Score, Student


@pytest.fixture
def gradebook() -> Gradebook:
    book = Gradebook()
    book.add_student(Student("s1", "Анна"))
    book.add_criterion(Criterion("c1", "Практика", Decimal(10), Decimal(40)))
    return book


@pytest.mark.parametrize("value", ["-1", "NaN", "Infinity", "-Infinity"])
def test_score_requires_nonnegative_finite_number(value: str) -> None:
    with pytest.raises(DomainError):
        Score(Decimal(value))


@pytest.mark.parametrize(
    ("maximum", "weight"),
    [
        ("0", "1"),
        ("10", "0"),
        ("10", "NaN"),
        ("Infinity", "1"),
        ("1e-999999", "1"),
        ("1", "1e-999999"),
        ("1e999999", "1"),
        ("10", "1e999999"),
    ],
)
def test_criterion_requires_maximum_and_weight_in_supported_range(
    maximum: str, weight: str
) -> None:
    with pytest.raises(DomainError):
        Criterion("c1", "Практика", Decimal(maximum), Decimal(weight))


@pytest.mark.parametrize("value", ["0.000001", "1000000"])
def test_criterion_accepts_both_boundaries(value: str) -> None:
    criterion = Criterion("c1", "Практика", Decimal(value), Decimal(value))
    assert criterion.max_score == criterion.weight == Decimal(value)


@pytest.mark.parametrize("value", [0, 10])
def test_accepts_score_on_both_boundaries(gradebook: Gradebook, value: int) -> None:
    score = Score(Decimal(value))
    gradebook.assign_score("s1", "c1", score)
    assert gradebook.evaluations_for("s1")[0].score == score


@pytest.mark.parametrize(("student_id", "criterion_id"), [("s2", "c1"), ("s1", "c2")])
def test_unknown_student_or_criterion_cannot_receive_score(
    gradebook: Gradebook, student_id: str, criterion_id: str
) -> None:
    with pytest.raises(DomainError, match="не найден"):
        gradebook.assign_score(student_id, criterion_id, Score(Decimal(8)))
    assert gradebook.evaluations_for("s1") == ()


def test_score_above_maximum_never_enters_gradebook(gradebook: Gradebook) -> None:
    with pytest.raises(DomainError, match="превышать"):
        gradebook.assign_score("s1", "c1", Score(Decimal("10.01")))
    assert gradebook.evaluations_for("s1") == ()


def test_only_explicit_correction_can_replace_a_score(gradebook: Gradebook) -> None:
    original = gradebook.assign_score("s1", "c1", Score(Decimal(8)))
    with pytest.raises(DomainError, match="уже выставлена"):
        gradebook.assign_score("s1", "c1", Score(Decimal(9)))
    with pytest.raises(DomainError, match="превышать"):
        gradebook.correct_score("s1", "c1", Score(Decimal(11)))
    assert gradebook.evaluations_for("s1") == (original,)

    revised = gradebook.correct_score("s1", "c1", Score(Decimal("9.5")))
    assert revised.score.value == Decimal("9.5")
    assert gradebook.evaluations_for("s1") == (revised,)

    gradebook.cancel_score("s1", "c1")
    assert gradebook.evaluations_for("s1") == ()
    with pytest.raises(DomainError, match="не выставлена"):
        gradebook.cancel_score("s1", "c1")


def test_student_and_criterion_ids_cannot_be_reused(gradebook: Gradebook) -> None:
    with pytest.raises(DomainError, match="уже есть"):
        gradebook.add_student(Student("s1", "Ольга"))
    with pytest.raises(DomainError, match="уже есть"):
        gradebook.add_criterion(Criterion("c1", "Теория", Decimal(20), Decimal(1)))
    assert gradebook.students[0].name == "Анна"
    assert gradebook.criteria[0].name == "Практика"
