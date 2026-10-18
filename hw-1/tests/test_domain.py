import pytest

from sd_hw_1.domain import Bicycle, DockStation, Helmet, Scooter
from sd_hw_1.domain.interfaces import EnergyConsumer


def test_non_electric_bicycle_is_not_an_energy_consumer() -> None:
    bicycle = Bicycle("TR-001", "Bicycle", 8)

    assert not isinstance(bicycle, EnergyConsumer)


def test_electric_scooter_is_an_energy_consumer() -> None:
    scooter = Scooter("TR-001", "Scooter", 8, daily_energy_kwh=1.5)

    assert isinstance(scooter, EnergyConsumer)


@pytest.mark.parametrize(
    ("factory", "message"),
    [
        (lambda: Bicycle("", "Велосипед", 8), "инвентарный номер"),
        (lambda: Bicycle("TR-001", "", 8), "наименование"),
        (lambda: Bicycle("TR-001", "Велосипед", 0), "простота для новичка"),
        (lambda: Bicycle("TR-001", "Велосипед", 8, 101), "техническое состояние"),
        (
            lambda: Scooter("TR-001", "Scooter", 8, daily_energy_kwh=-0.1),
            "энергопотребление",
        ),
        (lambda: Helmet("", "Шлем"), "инвентарный номер"),
        (lambda: DockStation("EQ-001", "Станция", -0.1), "энергопотребление"),
    ],
)
def test_domain_rejects_invalid_values(factory, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        factory()


@pytest.mark.parametrize("energy", [float("nan"), float("inf"), float("-inf")])
@pytest.mark.parametrize("entity", [Scooter, DockStation])
def test_energy_consumers_reject_non_finite_energy(entity, energy: float) -> None:
    with pytest.raises(ValueError, match="конечным неотрицательным числом"):
        if entity is Scooter:
            entity("TR-001", "Самокат", 8, daily_energy_kwh=energy)
        else:
            entity("EQ-001", "Станция", daily_energy_kwh=energy)
