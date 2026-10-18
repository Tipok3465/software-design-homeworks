from collections.abc import Callable

from sd_hw_1.container import build_fleet_service
from sd_hw_1.domain import Bicycle, ChargingCabinet, DockStation, ElectricBicycle, Helmet, Scooter
from sd_hw_1.services import FleetService

Input = Callable[[str], str]
Output = Callable[[str], None]

LINE = "-" * 58
MENU = """Главное меню
1. Принять транспорт в парк
2. Добавить вещь на баланс
3. Показать показатели парка
4. Показать транспорт для новичков
5. Показать весь инвентарь
0. Выйти"""


def main() -> None:
    run_console(build_fleet_service())


def run_console(
    fleet: FleetService,
    input_fn: Input = input,
    output_fn: Output = print,
) -> None:

    actions = {
        "1": lambda: _add_vehicle(fleet, input_fn, output_fn),
        "2": lambda: _add_equipment(fleet, input_fn, output_fn),
        "3": lambda: _show_metrics(fleet, output_fn),
        "4": lambda: _show_beginner_vehicles(fleet, output_fn),
        "5": lambda: _show_inventory(fleet, output_fn),
    }

    output_fn("Система учета парка ВышКат")
    output_fn(LINE)
    while True:
        output_fn(f"\n{MENU}")
        try:
            choice = input_fn("Выберите действие: ").strip()
        except EOFError:
            output_fn("\nВвод завершён.")
            return

        if choice == "0":
            output_fn("\nРабота завершена.")
            return

        action = actions.get(choice)
        if action is None:
            output_fn("[ОШИБКА] Неизвестная команда. Выберите пункт от 0 до 5.")
            continue

        try:
            action()
        except ValueError as error:
            output_fn(f"[ОШИБКА] {error}.")


def _add_vehicle(fleet: FleetService, input_fn: Input, output_fn: Output) -> None:
    _show_section("Приём транспорта", output_fn)
    output_fn("1 - самокат, 2 - велосипед, 3 - электровелосипед")
    kind = input_fn("Выберите вид: ").strip()
    inventory_number = input_fn("Инвентарный номер: ").strip()
    name = input_fn("Наименование: ").strip()
    friendliness = _read_int(input_fn, "Простота для новичка (1-10): ")
    condition = _read_int(input_fn, "Техническое состояние (0-100): ")

    if kind == "1":
        energy = _read_float(input_fn, "Суточный расход энергии, кВт ч: ")
        vehicle = Scooter(
            inventory_number,
            name,
            friendliness,
            condition_percent=condition,
            daily_energy_kwh=energy,
        )
    elif kind == "2":
        vehicle = Bicycle(inventory_number, name, friendliness, condition)
    elif kind == "3":
        energy = _read_float(input_fn, "Суточный расход энергии, кВт ч: ")
        vehicle = ElectricBicycle(
            inventory_number,
            name,
            friendliness,
            condition_percent=condition,
            daily_energy_kwh=energy,
        )
    else:
        raise ValueError("Неизвестный вид транспорта")

    if fleet.accept_vehicle(vehicle):
        output_fn("[ПРИНЯТО] Транспорт прошёл техосмотр и добавлен в парк.")
    else:
        output_fn("[ОТКАЗ] Транспорт не прошёл техосмотр.")


def _add_equipment(fleet: FleetService, input_fn: Input, output_fn: Output) -> None:
    _show_section("Добавление вещи", output_fn)
    output_fn("1 - шлем, 2 - док-станция, 3 - зарядный шкаф")
    kind = input_fn("Выберите вид: ").strip()
    inventory_number = input_fn("Инвентарный номер: ").strip()
    name = input_fn("Наименование: ").strip()

    if kind == "1":
        item = Helmet(inventory_number, name)
    elif kind == "2":
        energy = _read_float(input_fn, "Суточный расход энергии, кВт ч: ")
        item = DockStation(inventory_number, name, energy)
    elif kind == "3":
        energy = _read_float(input_fn, "Суточный расход энергии, кВт ч: ")
        item = ChargingCabinet(inventory_number, name, energy)
    else:
        raise ValueError("Неизвестный вид вещи")

    fleet.add_equipment(item)
    output_fn("[ДОБАВЛЕНО] Вещь поставлена на баланс.")


def _show_metrics(fleet: FleetService, output_fn: Output) -> None:
    _show_section("Показатели парка", output_fn)
    output_fn(f"Транспортных средств : {fleet.vehicle_count}")
    output_fn(f"Энергопотребление: {fleet.total_daily_energy_kwh():.2f} кВт ч в сутки")


def _show_beginner_vehicles(fleet: FleetService, output_fn: Output) -> None:
    _show_section("Транспорт для новичков", output_fn)
    vehicles = fleet.beginner_vehicles()
    if not vehicles:
        output_fn("Подходящего транспорта для новичков нет.")
        return
    output_fn(f"{'N':>2}  {'Инвентарный номер':<20}  {'Наименование':<24}  Простота")
    output_fn(LINE)
    for index, vehicle in enumerate(vehicles, start=1):
        output_fn(
            f"{index:>2}  {vehicle.inventory_number:<20}  "
            f"{vehicle.name:<24}  {vehicle.beginner_friendliness}/10"
        )


def _show_inventory(fleet: FleetService, output_fn: Output) -> None:
    _show_section("Имущество на балансе", output_fn)
    items = fleet.inventory()
    if not items:
        output_fn("На балансе пока ничего нет.")
        return
    output_fn(f"{'N':>2}  {'Инвентарный номер':<20}  Наименование")
    output_fn(LINE)
    for index, item in enumerate(items, start=1):
        output_fn(f"{index:>2}  {item.inventory_number:<20}  {item.name}")


def _show_section(title: str, output_fn: Output) -> None:
    output_fn(f"\n{title}")
    output_fn(LINE)


def _read_int(input_fn: Input, prompt: str) -> int:
    try:
        return int(input_fn(prompt))
    except ValueError as error:
        raise ValueError("ожидалось целое число") from error


def _read_float(input_fn: Input, prompt: str) -> float:
    try:
        return float(input_fn(prompt).replace(",", "."))
    except ValueError as error:
        raise ValueError("ожидалось число") from error


if __name__ == "__main__":
    main()
