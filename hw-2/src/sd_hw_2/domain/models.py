from dataclasses import dataclass
from decimal import Decimal

MIN_CRITERION_VALUE = Decimal("0.000001")
MAX_CRITERION_VALUE = Decimal(1_000_000)


class DomainError(ValueError):
    pass


def _validate_criterion_value(value: Decimal, label: str) -> None:
    if not value.is_finite() or not MIN_CRITERION_VALUE <= value <= MAX_CRITERION_VALUE:
        raise DomainError(
            f"{label} должен быть числом от {MIN_CRITERION_VALUE} до {MAX_CRITERION_VALUE}"
        )


@dataclass(frozen=True)
class Student:
    id: str
    name: str

    def __post_init__(self) -> None:
        if not self.id.strip() or not self.name.strip():
            raise DomainError("У студента должны быть идентификатор и имя")


@dataclass(frozen=True)
class Criterion:
    id: str
    name: str
    max_score: Decimal
    weight: Decimal

    def __post_init__(self) -> None:
        if not self.id.strip() or not self.name.strip():
            raise DomainError("У критерия должны быть идентификатор и название")
        _validate_criterion_value(self.max_score, "Максимальный балл")
        _validate_criterion_value(self.weight, "Вес")


@dataclass(frozen=True)
class Score:
    value: Decimal

    def __post_init__(self) -> None:
        if not self.value.is_finite() or self.value < 0:
            raise DomainError("Балл должен быть конечным неотрицательным числом")


@dataclass(frozen=True)
class Evaluation:
    student_id: str
    criterion_id: str
    score: Score

    @classmethod
    def create(cls, student: Student, criterion: Criterion, score: Score) -> "Evaluation":
        if score.value > criterion.max_score:
            raise DomainError(f"Балл не может превышать {criterion.max_score}")
        return cls(student.id, criterion.id, score)
