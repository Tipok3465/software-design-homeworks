from collections.abc import Callable
from decimal import Decimal, InvalidOperation

from sd_hw_2.adapters.result_format import MODE_LABELS
from sd_hw_2.application.facade import PosApplication
from sd_hw_2.application.ports import ResultMode, ResultReport
from sd_hw_2.domain.models import Criterion, Score, Student

MENU = """Главное меню
1. Добавить студента
2. Список студентов
3. Добавить критерий
4. Рубрикатор
5. Выставить оценку
6. Посмотреть оценки студента
7. Исправить оценку
8. Отменить оценку
9. Рассчитать итог
10. Экспортировать итог в CSV
0. Выйти"""


def run_console(
    app: PosApplication,
    read: Callable[[str], str] = input,
    write: Callable[[str], None] = print,
) -> None:
    def ask(prompt: str) -> str:
        return read(prompt).strip()

    def number(prompt: str) -> Decimal:
        try:
            return Decimal(ask(prompt).replace(",", "."))
        except InvalidOperation as error:
            raise ValueError("Введите число") from error

    def student_id() -> str:
        return ask("Код студента: ")

    def criterion_id() -> str:
        return ask("Код критерия: ")

    def mode() -> ResultMode:
        choice = ask("Режим (1 - предварительный, 2 - официальный): ")
        if choice == "1":
            return ResultMode.PROVISIONAL
        if choice == "2":
            return ResultMode.OFFICIAL
        raise ValueError("Выберите режим 1 или 2")

    def show_result(report: ResultReport) -> None:
        label = MODE_LABELS[report.mode]
        write(f"{report.student.name}: {report.score.value:.2f} из 100 ({label} итог)")
        if report.score.missing_criterion_ids:
            write("Не выставлены оценки: " + ", ".join(report.score.missing_criterion_ids))

    write("ПОС: преподавательская оценка студентов")
    while True:
        write("\n" + MENU)
        try:
            match ask("Выберите действие: "):
                case "0":
                    write("Работа завершена.")
                    return
                case "1":
                    app.add_student(Student(student_id(), ask("Имя студента: ")))
                    write("Студент добавлен.")
                case "2":
                    students = app.list_students()
                    if not students:
                        write("Студентов пока нет.")
                    for student in students:
                        write(f"{student.id}: {student.name}")
                case "3":
                    app.add_criterion(
                        Criterion(
                            criterion_id(), ask("Название критерия: "),
                            number("Максимальный балл: "), number("Вес: "),
                        )
                    )
                    write("Критерий добавлен.")
                case "4":
                    criteria = app.list_criteria()
                    if not criteria:
                        write("Рубрикатор пуст.")
                    for criterion in criteria:
                        write(
                            f"{criterion.id}: {criterion.name}, максимум {criterion.max_score}, "
                            f"вес {criterion.weight}"
                        )
                case "5":
                    app.assign_score(student_id(), criterion_id(), Score(number("Балл: ")))
                    write("Оценка выставлена.")
                case "6":
                    evaluations = app.list_evaluations(student_id())
                    if not evaluations:
                        write("Оценок пока нет.")
                    for evaluation in evaluations:
                        write(f"{evaluation.criterion_id}: {evaluation.score.value}")
                case "7":
                    app.correct_score(student_id(), criterion_id(), Score(number("Новый балл: ")))
                    write("Оценка исправлена.")
                case "8":
                    app.cancel_score(student_id(), criterion_id())
                    write("Оценка отменена.")
                case "9":
                    show_result(app.calculate_result(student_id(), mode()))
                case "10":
                    report = app.export_result(student_id(), mode(), ask("Путь к новому CSV: "))
                    show_result(report)
                    write("Итог выгружен.")
                case _:
                    write("Неизвестный пункт меню.")
        except (EOFError, KeyboardInterrupt):
            write("\nВвод завершён.")
            return
        except FileExistsError:
            write("Ошибка: файл для экспорта уже существует.")
        except OSError as error:
            write(f"Ошибка работы с файлом: {error.filename or error}")
        except (ValueError, ArithmeticError) as error:
            write(f"Ошибка: {error}")
