from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from sd_hw_2.domain.gradebook import Gradebook
from sd_hw_2.domain.models import DomainError


@dataclass(frozen=True)
class FinalScore:
    value: Decimal
    missing_criterion_ids: tuple[str, ...]


class MissingScoresPolicy(Protocol):
    def check(self, missing_criterion_ids: tuple[str, ...]) -> None: ...


class AllowMissingScores:
    def check(self, missing_criterion_ids: tuple[str, ...]) -> None:
        pass


class RequireAllScores:
    def check(self, missing_criterion_ids: tuple[str, ...]) -> None:
        if missing_criterion_ids:
            missing = ", ".join(missing_criterion_ids)
            raise DomainError(f"Не выставлены оценки по критериям: {missing}")


class FinalScoreCalculator:
    def __init__(self, policy: MissingScoresPolicy) -> None:
        self._policy = policy

    def calculate(self, gradebook: Gradebook, student_id: str) -> FinalScore:
        scores = {
            evaluation.criterion_id: evaluation.score.value
            for evaluation in gradebook.evaluations_for(student_id)
        }
        criteria = gradebook.criteria
        if not criteria:
            raise DomainError("Рубрикатор пуст")

        missing = tuple(criterion.id for criterion in criteria if criterion.id not in scores)
        self._policy.check(missing)

        total_weight = sum(criterion.weight for criterion in criteria)
        weighted_score = sum(
            scores[criterion.id] / criterion.max_score * criterion.weight
            for criterion in criteria
            if criterion.id in scores
        )
        return FinalScore(100 * weighted_score / total_weight, missing)
