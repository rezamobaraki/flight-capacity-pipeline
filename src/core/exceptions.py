class AppError(Exception):
    status_code: int = 500


class NotFoundError(AppError):
    status_code: int = 404


class AppValidationError(AppError):
    status_code: int = 422


class DatabaseError(AppError):
    pass


class DatabaseNotInitializedError(DatabaseError):
    def __init__(self):
        super().__init__("Database connection not initialized")


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
