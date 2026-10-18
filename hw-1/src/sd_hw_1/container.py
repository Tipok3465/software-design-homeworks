from sd_hw_1.services import FleetService, ServiceCenter


def build_fleet_service() -> FleetService:
    return FleetService(inspection=ServiceCenter())

