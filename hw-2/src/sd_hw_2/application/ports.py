from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from sd_hw_2.domain.gradebook import Gradebook
from sd_hw_2.domain.models import Student
from sd_hw_2.domain.results import FinalScore


class ResultMode(str, Enum):
    PROVISIONAL = "provisional"
    OFFICIAL = "official"


@dataclass(frozen=True)
class ResultReport:
    student: Student
    mode: ResultMode
    score: FinalScore


class GradebookRepository(Protocol):
    def load(self) -> Gradebook:
        """Возвращает ведомость, изменения которой сохраняются только через save."""
        ...

    def save(self, gradebook: Gradebook) -> None: ...


class ResultExporter(Protocol):
    def export(self, report: ResultReport, destination: str) -> None: ...
