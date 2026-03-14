class AppError(Exception):
    """Base exception for the application."""
    status_code: int = 500


class NotFoundError(AppError):
    """Resource not found error."""
    status_code: int = 404


class AppValidationError(AppError):
    """Application validation error."""
    status_code: int = 422


class DatabaseError(AppError):
    """Base database error."""
    pass


class DatabaseNotInitializedError(DatabaseError):
    """Raised when database is accessed before initialization."""
    def __init__(self):
        super().__init__("Database connection not initialized")


class DataFileNotFoundError(NotFoundError):
    """Raised when a required data file is missing."""
    def __init__(self, path: str):
        super().__init__(f"Data file not found: {path}")
        self.path = path


class NoFlightDataError(AppValidationError):
    """Raised when no flight data is available for processing."""
    def __init__(self):
        super().__init__("No usable flight data found")


class AircraftNotFoundError(NotFoundError):
    """Raised when aircraft equipment code is unknown."""
    def __init__(self, equipment: str):
        super().__init__(f"Unknown aircraft equipment: {equipment}")
        self.equipment = equipment

