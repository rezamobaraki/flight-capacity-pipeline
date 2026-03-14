from src.errors.app import AppError


class DatabaseError(AppError):
    pass


class DatabaseNotInitializedError(DatabaseError):
    def __init__(self):
        super().__init__("Database connection not initialized")
