from sd_hw_1.cli import run_console
from sd_hw_1.container import build_fleet_service
from sd_hw_1.services import FleetService


def test_container_builds_ready_to_use_service() -> None:
    assert isinstance(build_fleet_service(), FleetService)


def test_user_can_add_vehicle_and_request_all_reports() -> None:
    answers = iter(
        [
            "1",
            "1",
            "TR-001",
            "Городской самокат",
            "8",
            "90",
            "1.5",
            "3",
            "4",
            "5",
            "0",
        ]
    )
    output: list[str] = []

    run_console(
        build_fleet_service(),
        input_fn=lambda _prompt: next(answers),
        output_fn=output.append,
    )

    text = "\n".join(output)
    assert "[ПРИНЯТО] Транспорт прошёл техосмотр и добавлен в парк." in text
    assert "Транспортных средств : 1" in text
    assert "Энергопотребление: 1.50 кВт ч в сутки" in text
    assert "Транспорт для новичков" in text
    assert "TR-001" in text
    assert "Городской самокат" in text
    assert "Имущество на балансе" in text
    assert "Работа завершена." in text


def test_user_can_add_equipment() -> None:
    answers = iter(["2", "2", "EQ-001", "Центральная станция", "4,5", "5", "0"])
    output: list[str] = []

    run_console(
        build_fleet_service(),
        input_fn=lambda _prompt: next(answers),
        output_fn=output.append,
    )

    text = "\n".join(output)
    assert "[ДОБАВЛЕНО] Вещь поставлена на баланс." in text
    assert "EQ-001" in text
    assert "Центральная станция" in text


def test_rejected_vehicle_is_reported_to_user() -> None:
    answers = iter(["1", "2", "TR-001", "Неисправный велосипед", "7", "40", "0"])
    output: list[str] = []

    run_console(
        build_fleet_service(),
        input_fn=lambda _prompt: next(answers),
        output_fn=output.append,
    )

    assert "[ОТКАЗ] Транспорт не прошёл техосмотр." in output


def test_invalid_command_does_not_terminate_application() -> None:
    answers = iter(["unknown", "0"])
    output: list[str] = []

    run_console(
        build_fleet_service(),
        input_fn=lambda _prompt: next(answers),
        output_fn=output.append,
    )

    assert "[ОШИБКА] Неизвестная команда. Выберите пункт от 0 до 5." in output
    assert "\nРабота завершена." in output
