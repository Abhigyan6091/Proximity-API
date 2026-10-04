import csv
from bisect import bisect_left
from fastapi import FastAPI, HTTPException

app = FastAPI()

pts = []
with open("locations.csv", "r", encoding="utf-8") as f:
    r = csv.DictReader(f)
    for row in r:
        pts.append((int(row["ID"]), float(row["Latitude"]), float(row["Longitude"]), row["Category"].strip().lower()))

u_lat = sorted({p[1] for p in pts})
u_lon = sorted({p[2] for p in pts})
lat_m = {val: i for i, val in enumerate(u_lat)}
lon_m = {val: i for i, val in enumerate(u_lon)}

cat_idx = {}
grid_pos = []
for p in pts:
    r_idx, c_idx = lat_m[p[1]], lon_m[p[2]]
    grid_pos.append((r_idx, c_idx))
    cat_idx.setdefault(p[3], []).append(p[0] - 1)


def _get_axis_idx(axis, v, tol=1e-5):
    k = bisect_left(axis, v)
    for pos in (k - 1, k):
        if 0 <= pos < len(axis) and abs(axis[pos] - v) <= tol:
            return pos
    return -1


def find_closest(qlat, qlon, c_name, radius, limit=10):
    qr = _get_axis_idx(u_lat, qlat)
    qc = _get_axis_idx(u_lon, qlon)
    if qr == -1 or qc == -1:
        return None

    r_sq = radius * radius + 1e-9
    matched = []
    
    target_cat = c_name.strip().lower()
    for idx in cat_idx.get(target_cat, []):
        pid, plat, plon, _ = pts[idx]
        d_lat = plat - qlat
        d_lon = plon - qlon
        if d_lat * d_lat + d_lon * d_lon <= r_sq:
            pr, pc = grid_pos[idx]
            m_dist = abs(pr - qr) + abs(pc - qc)
            matched.append((m_dist, pid))

    matched.sort()
    return [loc_id for _, loc_id in matched[:limit]]


@app.get("/")
@app.get("/health")
def index():
    return {"status": "ok"}


@app.get("/search")
@app.get("/search/")
def search(lat: float, long: float, cat: str, rad: float):
    res = find_closest(lat, long, cat, rad)
    if res is None:
        raise HTTPException(status_code=400, detail="Query point is not on the grid")
    return {"ids": res}
