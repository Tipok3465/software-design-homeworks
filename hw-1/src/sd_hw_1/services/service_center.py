from sd_hw_1.domain.vehicles import Vehicle


class ServiceCenter:

    def __init__(self, minimum_condition_percent: int = 70) -> None:
        if not 0 <= minimum_condition_percent <= 100:
            raise ValueError("порог технического состояния должен быть от 0 до 100")
        self._minimum_condition_percent = minimum_condition_percent

    def approve(self, vehicle: Vehicle) -> bool:
        return vehicle.condition_percent >= self._minimum_condition_percent

