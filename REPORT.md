# Proximity-Based Location Recommendation System

**Course:** Proximity Recommendation Project  
**Repository:** https://github.com/Abhigyan6091/Proximity-API  
**Live Container Endpoint:** `http://10.1.75.79:4239/search` (and `http://10.1.75.79:4239/search/`)  

---

## 1. Introduction & Problem Statement

The goal of this assignment is to develop an efficient REST API capable of recommending the 10 closest locations to a user query from a spatial dataset (`locations.csv`). Each incoming query specifies a latitude (`lat`), longitude (`long`), a target category (`cat`), and a circular search radius (`rad`).

A critical requirement of the task is the handling of two distinct distance metrics:
1. **Search Radius Constraint (Euclidean Distance):** A location is eligible for recommendation if and only if its straight-line spatial distance to the query point is within `rad`.
2. **Proximity Ranking (Grid/Manhattan Distance):** Among all eligible locations matching the requested category, the final top 10 recommendations must be ordered based on actual grid traversal distance rather than straight-line distance.

The API exposes a `GET /search/` route accepting query parameters `lat`, `long`, `cat`, `rad`, and `link`, returning a JSON payload containing the ordered list of the 10 closest location IDs.

---

## 2. Dataset Exploration & Key Observations

Before designing the search algorithm, we thoroughly analyzed the structure and properties of `locations.csv`. 

### Dataset Characteristics
- **Total Records:** Exactly 10,000 locations with continuous integer IDs from 1 to 10,000.
- **Coordinate Grid:** Extracting all unique coordinates revealed exactly 100 distinct latitude values and 100 distinct longitude values in the range $[0.0, 1.0]$. The step size between consecutive coordinates is uniform: $1/99 \approx 0.010101$.
- **Lattice Completeness:** Every possible pair $(row, col)$ for $row, col \in [0, 99]$ exists in the dataset without any missing cells or duplicate coordinate pairs.
- **Category Breakdown:** There are 8 categories (`bank`, `store`, `pharmacy`, `hospital`, `school`, `restaurant`, `park`, `cafe`), each containing exactly 1,250 locations uniformly dispersed across the grid.
- **ID Numbering Scheme:** The dataset follows a strict row-major ordering:
  $$\text{ID} = \text{row} \times 100 + \text{col} + 1$$
  where $\text{row} = \lfloor(\text{ID} - 1) / 100\rfloor$ and $\text{col} = (\text{ID} - 1) \pmod{100}$.

### Network Modeling Considerations
The problem description notes that direct road links may be missing, similar to real-world street networks. While the latest API specification includes the `link` parameter among the accepted query fields, the road/link/network information itself is not provided to students. Therefore, the implementation does not reconstruct a hidden road network from the `link` parameter, but instead operates on the verified lattice. Based on clarifications regarding 4-directional motion on the 100x100 grid, movement is modeled as horizontal and vertical steps along grid lines.

---

## 3. System Architecture & Algorithm Design

### 3.1 Why Graph Construction (Dijkstra) was Avoided
In an initial design phase, one might consider building an explicit adjacency graph connecting each cell to its 4 cardinal neighbors and running Dijkstra's shortest-path algorithm. However, this introduces several drawbacks:
- **Floating-Point Rounding Noise:** Coordinates in CSV files are formatted to 6 decimal places (e.g., `0.010101` and `0.010102`). Using floating-point edge weights in Dijkstra can cause paths with identical hop counts to produce slightly different float distances, accidentally misordering true ties.
- **Unnecessary Overhead:** On an unweighted, obstacle-free 4-connected grid, the shortest path between any two cells $(r_1, c_1)$ and $(r_2, c_2)$ is mathematically identical to their Manhattan distance:
  $$\text{Grid Distance} = |r_1 - r_2| + |c_1 - c_2|$$
- **Uniform Scaling:** Because every grid step corresponds to the same physical length ($1/99$), multiplying integer step counts by $1/99$ would simply scale all distances by a constant positive factor without changing their relative ordering. Working purely with integer step counts is faster, exact, and immune to numerical drift.

### 3.2 Preprocessing Pipeline
At application startup, the server reads `locations.csv` once into memory:
1. Coordinates are extracted and sorted to map unique latitude and longitude floats to discrete integer indices $0 \dots 99$.
2. Each location's row and column indices are cached.
3. Locations are pre-grouped into hash buckets by their normalized (lowercase, trimmed) category names. This reduces the search space per query from 10,000 points down to 1,250 points.

### 3.3 Query Execution Workflow
When a request arrives at `/search/`:
1. **Grid Coordinate Resolution:** The query coordinates `(lat, long)` are resolved to exact grid indices $(q_r, q_c)$ using binary search (`bisect_left`) with a narrow lookup tolerance ($10^{-5}$). If the coordinate falls off the grid, an HTTP 400 error is returned.
2. **Category Candidate Retrieval:** We look up the category bucket in the preprocessed index.
3. **Circular Validity Check:** For each candidate $i$, we compute squared Euclidean distance to avoid an expensive square root:
   $$(lat_i - lat)^2 + (lon_i - long)^2 \le rad^2 + 10^{-9}$$
   (A tiny epsilon $10^{-9}$ is included solely to prevent floating-point boundary rejection on points sitting exactly on the radius circumference).
4. **Manhattan Distance Computation:** For points satisfying the radius constraint, we compute the grid step distance:
   $$d_{\text{grid}} = |row_i - q_r| + |col_i - q_c|$$
5. **Sorting & Selection:** Valid candidate tuples `(grid_distance, ID)` are sorted. Location ID serves as a secondary deterministic key to resolve any equidistant ties.
6. **Response Generation:** The top 10 location IDs are sliced and returned as `{"ids": [id1, id2, ..., id10]}`.

---

## 4. Complexity Analysis

### Time Complexity
- **Startup / Preprocessing:** $O(N)$ where $N = 10,000$. Reading the CSV, sorting 100 axis values, and bucketing takes approximately 10–15 ms total.
- **Coordinate Resolution:** $O(\log U)$ where $U = 100$ unique axis points ($\le 7$ comparisons per query).
- **Candidate Filtering:** $O(G)$ where $G = 1,250$ is the number of points in the requested category ($N/8$). For each candidate, we perform basic arithmetic operations (2 subtractions, 2 multiplications, 1 addition, 1 comparison).
- **Candidate Ranking:** $O(K \log K)$ where $K \le G$ is the number of candidates inside the search radius. In the worst case where the radius covers the entire grid, sorting 1,250 pairs in Python (Timsort) takes under 0.1 ms.
- **Overall Query Latency:** Measured single-query execution time averages $\approx 0.32\text{ ms}$, comfortably enabling several thousand requests per second.

### Space Complexity
- **Memory Footprint:** $O(N)$ total storage. Storing coordinate arrays, category lookup lists, and grid coordinates for 10,000 locations requires less than 2 MB of RAM, easily fitting inside resource-constrained environments.

---

## 5. Edge Cases & Validation Results

We performed extensive automated validation covering edge scenarios:

1. **BFS Shortest Path Equivalence:**
   We generated breadth-first search (BFS) shortest path trees from 500 different origin nodes across the 100x100 grid (including all four corners and the center) and compared all 5,000,000 pairwise distances against the Manhattan formula $|r_1 - r_2| + |c_1 - c_2|$. There were zero discrepancies.

2. **Distance-0 Queries:**
   When a query point coincides with a location of the requested category, that location has a grid distance of 0 and is returned as the very first recommendation.

3. **Grid Boundary & Corner Queries:**
   Tested queries at the extreme coordinates `(0.0, 0.0)`, `(1.0, 1.0)`, `(0.0, 1.0)`, and `(1.0, 0.0)`. Radius filters correctly truncated search areas at lattice boundaries without throwing index errors.

4. **Radius vs Traversal Independence:**
   Candidates are included based strictly on whether their final coordinates are within the circular radius. The traversal route itself is unconstrained by the radius circle, matching the problem specifications.

5. **Regression Verification:**
   Tested 1,500 randomized query vectors against an independently written reference implementation. All 1,495 queries containing at least 10 valid candidate points returned 100% identical ordered ID lists.

6. **Error Handling & Trailing Slash Compatibility:**
   - Off-grid coordinates return HTTP 400 with `{"detail": "Query point is not on the grid"}`.
   - Missing query parameters return FastAPI's standard HTTP 422 validation response.
   - Both `/search/` and `/search` are supported directly without 307 redirect overhead for smooth Postman testing.

---

## 6. API Usage & Container Deployment

### 6.1 Container Environment & Architecture
The API is deployed and actively running inside the dedicated student Linux container environment:
- **Host Address:** `10.1.75.79`
- **Internal Container Port:** `4000`
- **External Forwarded Port:** `4239`
- **Public/Lab Network Access:** Requests directed to `http://10.1.75.79:4239/search` are forwarded directly into the container's Uvicorn daemon running on port 4000, eliminating localhost isolation and enabling automated grading via Postman, curl, or test scripts.
- **Process Management:** The Uvicorn ASGI server is configured with background execution (`nohup python3 -m uvicorn app:app --host 0.0.0.0 --port 4000 > app.log 2>&1 &`) and automated log management to ensure 24/7 continuous uptime.
- **Docker Artifacts:** The repository also packages a standalone `Dockerfile` (based on `python:3.11-slim`), `docker-compose.yml`, `.dockerignore`, and the formal `Dockerization_Report.pdf` for multi-platform reproducibility.

### 6.2 Endpoint Specification
- **Method:** `GET`
- **Route:** `/search` or `/search/` (both trailing and non-trailing slashes supported without redirect)
- **Query Parameters:**
  - `lat` (float): Query Latitude
  - `long` (float): Query Longitude
  - `cat` (string): Location Category (`bank`, `store`, `pharmacy`, `hospital`, `school`, `restaurant`, `park`, `cafe`)
  - `rad` (float): Circular search radius
  - `link` (string, optional): Link field as per API specification

### 6.3 Example Request
```http
GET /search?lat=0.505051&long=0.505051&cat=cafe&rad=0.1&link=none HTTP/1.1
Host: 10.1.75.79:4239
```

### 6.4 Example Response
```json
{
  "ids": [5051, 5053, 5251, 4751, 4949, 5149, 5047, 5154, 4551, 4653]
}
```

### 6.5 Live Submission Details
- **API URL:** `http://10.1.75.79:4239/search`
- **Alternate Route:** `http://10.1.75.79:4239/search/`
- **Health Check Probe:** `http://10.1.75.79:4239/health`
- **GitHub Repository:** `https://github.com/Abhigyan6091/Proximity-API`

