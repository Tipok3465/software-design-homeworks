from sd_hw_1.domain import Scooter
from sd_hw_1.services import ServiceCenter


def test_service_center_accepts_serviceable_vehicle() -> None:
    assert ServiceCenter().approve(Scooter("TR-001", "Scooter", 8)) is True


def test_service_center_rejects_unserviceable_vehicle() -> None:
    vehicle = Scooter("TR-001", "Scooter", 8, condition_percent=69)

    assert ServiceCenter().approve(vehicle) is False


def test_service_center_accepts_vehicle_on_threshold() -> None:
    vehicle = Scooter("TR-001", "Scooter", 8, condition_percent=70)

    assert ServiceCenter().approve(vehicle) is True


def test_service_center_supports_an_injected_threshold() -> None:
    vehicle = Scooter("TR-001", "Scooter", 8, condition_percent=85)

    assert ServiceCenter(minimum_condition_percent=90).approve(vehicle) is False

