# Fuel Optimization API

This project calculates the optimal fuel stops along a route in the USA, minimizing the total cost based on fuel prices.

## Tech Stack

*   **Backend:** Django 5, Django Rest Framework
*   **Database:** PostgreSQL with PostGIS (via Docker)
*   **Routing:** OSRM (Open Source Routing Machine) Public API
*   **Geocoding:** Nominatim (OpenStreetMap)
*   **Containerization:** Docker & Docker Compose

## Prerequisites

*   Docker and Docker Compose installed.

## Setup & Running

1.  **Build and Start Containers:**
    ```bash
    docker compose up --build
    ```

2.  **Apply Migrations:**
    ```bash
    docker compose exec web python manage.py migrate
    ```

3.  **Load Fuel Data:**
    The project includes a CSV file with fuel prices. You need to load this into the database.
    *Note: The loader uses a free geocoding service which is rate-limited (1 request/sec). Loading the full dataset will take a long time. Use `--limit` for testing.*

    ```bash
    docker compose exec web python manage.py load_fuel_data fuel-prices-for-be-assessment.csv --limit 50
    ```

    **Alternative (Quick Start):**
    To quickly seed the database with test stations along the NY-DC route:
    ```bash
    docker compose exec web python manage.py seed_test_data
    ```

## API Usage

**Endpoint:** `POST /api/route/`

**Request Body:**
```json
{
    "start_location": "New York, NY",
    "finish_location": "Boston, MA"
}
```

**Response:**
```json
{
    "route_geometry": { ... },
    "stops": [ ... ],
    "total_fuel_cost": 45.20,
    "total_distance_miles": 215.5
}
```

## Documentation

Once the server is running, visit:
*   **Swagger UI:** [http://localhost:8001/api/schema/swagger-ui/](http://localhost:8001/api/schema/swagger-ui/)
*   **ReDoc:** [http://localhost:8001/api/schema/redoc/](http://localhost:8001/api/schema/redoc/)
