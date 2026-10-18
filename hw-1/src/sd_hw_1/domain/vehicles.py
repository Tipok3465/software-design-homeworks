from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True, slots=True)
class Vehicle:
    inventory_number: str
    name: str
    beginner_friendliness: int
    condition_percent: int = 100

    def __post_init__(self) -> None:
        if not self.inventory_number.strip():
            raise ValueError("инвентарный номер не может быть пустым")
        if not self.name.strip():
            raise ValueError("наименование не может быть пустым")
        if not 1 <= self.beginner_friendliness <= 10:
            raise ValueError("простота для новичка должна быть от 1 до 10")
        if not 0 <= self.condition_percent <= 100:
            raise ValueError("техническое состояние должно быть от 0 до 100")


@dataclass(frozen=True, slots=True)
class ElectricVehicle(Vehicle):
    daily_energy_kwh: float = 0.0

    def __post_init__(self) -> None:
        super(ElectricVehicle, self).__post_init__()
        if not isfinite(self.daily_energy_kwh) or self.daily_energy_kwh < 0:
            raise ValueError("суточное энергопотребление должно быть конечным неотрицательным числом")


@dataclass(frozen=True, slots=True)
class Scooter(ElectricVehicle):
    pass


@dataclass(frozen=True, slots=True)
class Bicycle(Vehicle):
    pass


@dataclass(frozen=True, slots=True)
class ElectricBicycle(ElectricVehicle):
    pass

