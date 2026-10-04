# Proximity Location Search API

FastAPI service that finds the 10 closest locations matching a requested category and search radius on a 100x100 grid.

## API Specification

- **Route:** `GET /search/`
- **Parameters:**
  - `lat` (float): Query Latitude
  - `long` (float): Query Longitude
  - `cat` (string): Category name (e.g. `bank`, `cafe`, `hospital`, etc.)
  - `rad` (float): Circular search radius
- **Response Format:**
  ```json
  {
    "ids": [5051, 5053, 5251, 4751, 4949, 5149, 5047, 5154, 4551, 4653]
  }
  ```

## Live Deployment Link

```text
http://10.1.75.79:4239/search/?lat=0.505051&long=0.505051&cat=cafe&rad=0.1
```

## Running Locally

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the server:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000
   ```
3. Query the endpoint:
   ```bash
   curl "http://localhost:8000/search/?lat=0.0&long=0.0&cat=hospital&rad=0.3"
   ```
