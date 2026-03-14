class AppError(Exception):
	status_code: int = 500


class NotFoundError(AppError):
	status_code: int = 404


class AppValidationError(AppError):
	status_code: int = 422
