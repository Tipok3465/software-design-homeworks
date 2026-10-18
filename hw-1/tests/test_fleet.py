from unittest.mock import Mock

import pytest

from sd_hw_1.domain import Bicycle, DockStation, Helmet, Scooter, Vehicle
from sd_hw_1.services import DuplicateInventoryNumberError, FleetService


def test_approved_vehicle_is_added() -> None:
    inspection = Mock()
    inspection.approve.return_value = True
    fleet = FleetService(inspection)
    vehicle = Scooter("TR-001", "Scooter", 7, daily_energy_kwh=2.5)

    assert fleet.accept_vehicle(vehicle) is True
    assert fleet.vehicle_count == 1
    inspection.approve.assert_called_once_with(vehicle)


def test_rejected_vehicle_is_not_added() -> None:
    inspection = Mock()
    inspection.approve.return_value = False
    fleet = FleetService(inspection)

    assert fleet.accept_vehicle(Scooter("TR-001", "Broken scooter", 7)) is False
    assert fleet.vehicle_count == 0


def test_beginner_rule_includes_boundary_value_six() -> None:
    inspection = Mock()
    inspection.approve.return_value = True
    fleet = FleetService(inspection)
    fleet.accept_vehicle(Scooter("TR-001", "Easy", 6))
    fleet.accept_vehicle(Scooter("TR-002", "Advanced", 5))

    assert [item.inventory_number for item in fleet.beginner_vehicles()] == ["TR-001"]


def test_total_energy_includes_consumers_only() -> None:
    inspection = Mock()
    inspection.approve.return_value = True
    fleet = FleetService(inspection)
    fleet.accept_vehicle(Scooter("TR-001", "Scooter", 8, daily_energy_kwh=2.5))
    fleet.accept_vehicle(Bicycle("TR-002", "Bicycle", 9))
    fleet.add_equipment(DockStation("EQ-001", "Dock", 4.0))
    fleet.add_equipment(Helmet("EQ-002", "Helmet"))

    assert fleet.total_daily_energy_kwh() == pytest.approx(6.5)


def test_new_vehicle_type_requires_no_fleet_service_changes() -> None:
    class CargoBike(Vehicle):
        pass

    inspection = Mock()
    inspection.approve.return_value = True
    fleet = FleetService(inspection)
    cargo_bike = CargoBike("TR-001", "Cargo bike", 3)

    assert fleet.accept_vehicle(cargo_bike) is True
    assert fleet.inventory() == (cargo_bike,)


def test_inventory_contains_vehicles_and_equipment() -> None:
    inspection = Mock()
    inspection.approve.return_value = True
    fleet = FleetService(inspection)
    fleet.accept_vehicle(Scooter("TR-001", "Scooter", 8))
    fleet.add_equipment(Helmet("EQ-001", "Helmet"))

    assert [(item.inventory_number, item.name) for item in fleet.inventory()] == [
        ("TR-001", "Scooter"),
        ("EQ-001", "Helmet"),
    ]


def test_duplicate_inventory_number_is_rejected() -> None:
    inspection = Mock()
    inspection.approve.return_value = True
    fleet = FleetService(inspection)
    fleet.add_equipment(Helmet("ITEM-001", "Helmet"))

    with pytest.raises(DuplicateInventoryNumberError):
        fleet.accept_vehicle(Scooter("ITEM-001", "Scooter", 8))

