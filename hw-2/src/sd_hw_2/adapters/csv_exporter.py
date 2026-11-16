import csv
from pathlib import Path

from sd_hw_2.adapters.result_format import MODE_LABELS
from sd_hw_2.application.ports import ResultReport


class CsvResultExporter:
    def export(self, report: ResultReport, destination: str) -> None:
        with Path(destination).open("x", encoding="utf-8-sig", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Код студента", "Имя", "Режим", "Итог из 100", "Пропуски"])
            writer.writerow(
                [
                    report.student.id,
                    report.student.name,
                    MODE_LABELS[report.mode],
                    f"{report.score.value:.2f}",
                    ", ".join(report.score.missing_criterion_ids),
                ]
            )
