from argparse import ArgumentParser
from pathlib import Path

from sd_hw_2.adapters.console import run_console
from sd_hw_2.adapters.csv_exporter import CsvResultExporter
from sd_hw_2.adapters.json_repository import JsonGradebookRepository
from sd_hw_2.application.facade import PosApplication
from sd_hw_2.domain.results import AllowMissingScores, FinalScoreCalculator, RequireAllScores


class Container:
    def __init__(self, data_path: Path) -> None:
        self.application = PosApplication(
            repository=JsonGradebookRepository(data_path),
            exporter=CsvResultExporter(),
            provisional_calculator=FinalScoreCalculator(AllowMissingScores()),
            official_calculator=FinalScoreCalculator(RequireAllScores()),
        )


def main() -> None:
    parser = ArgumentParser(description="Преподавательская оценка студентов")
    parser.add_argument(
        "--data", type=Path, default=Path("pos-gradebook.json"), help="путь к файлу ведомости"
    )
    args = parser.parse_args()
    run_console(Container(args.data).application)


if __name__ == "__main__":
    main()
