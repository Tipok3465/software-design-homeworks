import csv
from pathlib import Path

import pytest

from sd_hw_2.adapters.console import run_console
from sd_hw_2.application.ports import ResultMode
from sd_hw_2.main import Container


def play(container: Container, answers: list[str]) -> str:
    lines = iter(answers)
    output: list[str] = []

    def read(prompt: str) -> str:
        try:
            return next(lines)
        except StopIteration as error:
            raise EOFError from error

    run_console(container.application, read, output.append)
    return "\n".join(output)


def test_console_records_scores_and_exports_after_restart(tmp_path: Path) -> None:
    data = tmp_path / "gradebook.json"
    output = play(
        Container(data),
        [
            "1", "s1", "Анна, группа 1",
            "3", "practice", "Практика", "10", "2",
            "3", "theory", "Теория", "20", "3",
            "5", "s1", "practice", "12",
            "5", "s1", "practice", "8,0",
            "5", "s1", "theory", "15",
            "0",
        ],
    )
    assert "Балл не может превышать 10" in output

    destination = tmp_path / "report.csv"
    output = play(
        Container(data),
        ["9", "s1", "2", "10", "s1", "2", str(destination), "0"],
    )
    assert "77.00 из 100 (официальный итог)" in output
    assert "Итог выгружен." in output
    with destination.open(encoding="utf-8-sig", newline="") as file:
        header, row = csv.reader(file)
    assert header == ["Код студента", "Имя", "Режим", "Итог из 100", "Пропуски"]
    assert row == ["s1", "Анна, группа 1", "официальный", "77.00", ""]

    app = Container(data).application
    with pytest.raises(FileExistsError):
        app.export_result("s1", ResultMode.OFFICIAL, str(data))
    assert Container(data).application.list_students()[0].name == "Анна, группа 1"


@pytest.mark.parametrize(
    "invalid",
    ["{", '{"students": {}, "criteria": [], "evaluations": []}'],
)
def test_invalid_storage_is_reported_without_overwriting(tmp_path: Path, invalid: str) -> None:
    data = tmp_path / "gradebook.json"
    data.write_text(invalid, encoding="utf-8")
    output = play(Container(data), ["1", "s1", "Анна", "0"])
    assert "Некорректный файл ведомости" in output
    assert data.read_text(encoding="utf-8") == invalid


def test_eof_in_the_middle_of_input_exits_cleanly(tmp_path: Path) -> None:
    data = tmp_path / "gradebook.json"
    output = play(Container(data), ["1", "s1"])
    assert "Ввод завершён." in output
    assert not data.exists()


def test_extreme_weight_is_rejected_before_saving(tmp_path: Path) -> None:
    data = tmp_path / "gradebook.json"
    output = play(
        Container(data),
        [
            "1", "s1", "Анна",
            "3", "c1", "Практика", "10", "1e999999",
            "3", "c1", "Практика", "10", "2",
            "5", "s1", "c1", "10",
            "9", "s1", "2",
            "0",
        ],
    )
    assert "Ошибка: Вес должен быть числом от 0.000001 до 1000000" in output
    assert "100.00 из 100 (официальный итог)" in output
    criteria = Container(data).application.list_criteria()
    assert len(criteria) == 1
    assert str(criteria[0].weight) == "2"
