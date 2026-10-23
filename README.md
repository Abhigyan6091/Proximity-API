# Proximity Location Search API

FastAPI service that finds the 10 closest locations matching a requested category and search radius on a 100x100 grid.

## API Specification

- **Route:** `GET /search/`
- **Parameters:**
  - `lat` (float): Query Latitude
  - `long` (float): Query Longitude
  - `cat` (string): Category name (e.g. `bank`, `cafe`, `hospital`, etc.)
  - `rad` (float): Circular search radius
  - `link` (string, optional): Link field as per API specification
- **Response Format:**
  ```json
  {
    "ids": [5051, 5053, 5251, 4751, 4949, 5149, 5047, 5154, 4551, 4653]
  }
  ```

## Live Container Deployment Link

The service is deployed and running inside the dedicated student container:
```text
http://10.1.75.79:4239/search?lat=0.505051&long=0.505051&cat=cafe&rad=0.1&link=none
```
*Note: Both `/search` and `/search/` routes are supported without redirection.*


## Running Locally

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the server:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 4000
   ```
3. Query the endpoint:
   ```bash
   curl "http://localhost:4000/search/?lat=0.0&long=0.0&cat=hospital&rad=0.3"
   ```

## Running with Docker (One-Command Startup)

1. Build and start the containerized service:
   ```bash
   docker compose up --build
   ```
2. Query the containerized endpoint (Host Port 4239 -> Container Port 4000):
   ```bash
   curl "http://localhost:4239/search?lat=0.505051&long=0.505051&cat=cafe&rad=0.1&link=none"
   ```
   Or query the live deployed container:
   ```bash
   curl "http://10.1.75.79:4239/search?lat=0.505051&long=0.505051&cat=cafe&rad=0.1&link=none"
   ```
3. Stop the service cleanly:
   ```bash
   docker compose down
   ```

## Evaluation Documentation & Evidence

- **PDF Evaluation Report:** [`Dockerization_Report_Final.pdf`](Dockerization_Report_Final.pdf)
- **Comprehensive Markdown Report:** [`REPORT.md`](REPORT.md)
- **Terminal Verification Screenshots:** [`screenshots/`](screenshots/)

