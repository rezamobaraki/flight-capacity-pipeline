# Use an official Python runtime as a parent image
FROM python:3.14-slim AS base

# Install uv from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory to /app
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Copy dependency definitions
COPY pyproject.toml uv.lock ./

# Development stage
FROM base AS dev
# Install dependencies (including dev)
RUN uv sync --frozen --no-install-project
# Copy application code
COPY src src
COPY tests tests
# Install the project itself
RUN uv sync --frozen
# Add the virtual environment to the PATH
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

# Production stage
FROM base AS prod
# Install dependencies (production only)
RUN uv sync --frozen --no-install-project --no-dev
# Copy application code
COPY src src
# Install the project itself (production only)
RUN uv sync --frozen --no-dev
# Add the virtual environment to the PATH
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

# Expose the port used by the FastAPI app
EXPOSE 8000

# Default command to run the application
CMD ["uvicorn", "src.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
