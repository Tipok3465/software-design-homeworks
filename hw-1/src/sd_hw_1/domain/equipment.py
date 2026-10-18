from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True, slots=True)
class Equipment:
    inventory_number: str
    name: str

    def __post_init__(self) -> None:
        if not self.inventory_number.strip():
            raise ValueError("инвентарный номер не может быть пустым")
        if not self.name.strip():
            raise ValueError("наименование не может быть пустым")


@dataclass(frozen=True, slots=True)
class EnergyEquipment(Equipment):
    daily_energy_kwh: float = 0.0

    def __post_init__(self) -> None:
        super(EnergyEquipment, self).__post_init__()
        if not isfinite(self.daily_energy_kwh) or self.daily_energy_kwh < 0:
            raise ValueError("суточное энергопотребление должно быть конечным неотрицательным числом")


@dataclass(frozen=True, slots=True)
class Helmet(Equipment):
    pass


@dataclass(frozen=True, slots=True)
class DockStation(EnergyEquipment):
    pass


@dataclass(frozen=True, slots=True)
class ChargingCabinet(EnergyEquipment):
    pass

