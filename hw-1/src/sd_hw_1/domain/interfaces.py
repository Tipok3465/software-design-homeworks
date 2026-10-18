from __future__ import annotations

from typing import Protocol, runtime_checkable

from sd_hw_1.domain.vehicles import Vehicle


@runtime_checkable
class InventoryItem(Protocol):

    @property
    def inventory_number(self) -> str: ...

    @property
    def name(self) -> str: ...


@runtime_checkable
class EnergyConsumer(Protocol):

    @property
    def daily_energy_kwh(self) -> float: ...


class VehicleInspection(Protocol):

    def approve(self, vehicle: Vehicle) -> bool: ...

