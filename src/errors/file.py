from src.errors.app import AppValidationError, NotFoundError


class DataFileNotFoundError(NotFoundError):
	def __init__(self, path: str):
		super().__init__(f"Data file not found: {path}")
		self.path = path


class NoFlightDataError(AppValidationError):
	def __init__(self):
		super().__init__("No usable flight data found")


class AircraftNotFoundError(NotFoundError):
	def __init__(self, equipment: str):
		super().__init__(f"Unknown aircraft equipment: {equipment}")
		self.equipment = equipment
