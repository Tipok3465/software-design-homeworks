from sd_hw_1.domain.interfaces import EnergyConsumer, InventoryItem, VehicleInspection
from sd_hw_1.domain.vehicles import Vehicle


class DuplicateInventoryNumberError(ValueError):
    pass


class FleetService:

    def __init__(self, inspection: VehicleInspection) -> None:
        self._inspection = inspection
        self._vehicles: list[Vehicle] = []
        self._equipment: list[InventoryItem] = []

    def accept_vehicle(self, vehicle: Vehicle) -> bool:
        self._ensure_unique_number(vehicle.inventory_number)
        if not self._inspection.approve(vehicle):
            return False
        self._vehicles.append(vehicle)
        return True

    def add_equipment(self, item: InventoryItem) -> None:
        self._ensure_unique_number(item.inventory_number)
        self._equipment.append(item)

    @property
    def vehicle_count(self) -> int:
        return len(self._vehicles)

    def beginner_vehicles(self) -> tuple[Vehicle, ...]:
        return tuple(
            vehicle for vehicle in self._vehicles if vehicle.beginner_friendliness >= 6
        )

    def total_daily_energy_kwh(self) -> float:
        items = (*self._vehicles, *self._equipment)
        return sum(
            item.daily_energy_kwh for item in items if isinstance(item, EnergyConsumer)
        )

    def inventory(self) -> tuple[InventoryItem, ...]:
        return (*self._vehicles, *self._equipment)

    def _ensure_unique_number(self, inventory_number: str) -> None:
        if any(item.inventory_number == inventory_number for item in self.inventory()):
            raise DuplicateInventoryNumberError(
                f'инвентарный номер "{inventory_number}" уже используется'
            )

