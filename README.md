# Flight Capacity Pipeline

A data engineering pipeline and API that calculates available cargo capacity (payload and volume) for flights based on ADS-B event streams and aircraft specifications.

## 🚀 Features

- **Ingestion**: Efficiently processes daily flight event CSVs and aircraft JSON data.
- **Transformation**: Aggregates raw events into flights using SQL-based ELT pattern.
- **Capacity Calculation**: Determines payload and volume for each flight.
- **API**: Exposes flight capacity data via a RESTful API.
- **Dockerized**: Fully containerized for easy deployment and testing.

## 🛠 Prerequisites

- **Python 3.14+**
- **[uv](https://github.com/astral-sh/uv)** (for dependency management)
- **Docker & Docker Compose** (optional, for containerized execution)

## 📦 Installation & Setup

### Local Development

1.  **Install Dependencies**:
    ```bash
    make install
    ```

2.  **Run the Pipeline (Ingestion)**:
    Process the raw CSVs and populate the SQLite database.
    ```bash
    make ingest
    ```
    *This reads from `data/raw/` and outputs to `data/warehouse/flight_capacity.db`.*

3.  **Start the API Server**:
    Host the REST API locally on port 8000.
    ```bash
    make run
    ```
    Open [http://localhost:8000/docs](http://localhost:8000/docs) to explore the endpoints.

4.  **Run Tests**:
    ```bash
    make test
    # or with coverage
    make test-cov
    ```

### 🐳 Docker Usage

The project is fully containerized as **Flight Capacity Pipeline**. You can run the entire stack without installing Python locally.

1.  **Build Images**:
    ```bash
    make docker-build
    ```

2.  **Run Ingestion**:
    ```bash
    make docker-ingest
    ```

3.  **Start API**:
    ```bash
    make docker-up
    ```
    Access the API at `http://localhost:8000`.

4.  **Run Tests in Docker**:
    ```bash
    make docker-test
    ```

## 📂 Project Structure

- `src/`: Source code for the application.
  - `cli.py`: Entry point for batch processing.
  - `main.py`: Entry point for the FastAPI server.
  - `services/`: Business logic (ETL orchestration, File I/O).
  - `repositories/`: Database interactions (SQLite).
- `data/`: Directory for input and output data.
- `docs/`: Architecture and design documentation.
- `tests/`: Pytest suite.

## 📚 Documentation

For detailed design decisions, architecture diagrams, and cloud scaling proposals, please refer to:
- [Design & Architecture](docs/design_architecture.md)
- [Excalidraw](https://excalidraw.com/#json=Is8leyFiz5cQk8VkuJQgX,pTcPe8WfFd0Fm4fdSKpjGA)) 
