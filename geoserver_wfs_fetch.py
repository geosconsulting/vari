from fastapi import FastAPI, Query, Request, HTTPException
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from shapely.geometry import shape, box
from shapely import wkt
import requests
import json

app = FastAPI()
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

GEOSERVER_WFS_URL = "http://192.168.1.41:8080/geoserver/ows"
MAX_FEATURES = 500
MAX_POLYGON_AREA = 1_000_000  # square meters

"""
res = requests.get(
    "http://localhost:8080/geoserver/ows?service=WFS&version=2.0.0&request=GetCapabilities"
)
print(res.status_code)
print(res.text[:500])
"""


@app.get("/")
def root():
    return {"message": "Welcome to the GeoServer WFS Fetch API"}


@app.get("/filtered-wfs")
@limiter.limit("10/minute")  # 🚦 max 10 requests per IP per minute
def filtered_wfs(
    request: Request,
    country: str = Query(
        ..., description="Name of the country table, e.g., 'italy', 'germany'"
    ),
    cql_filter: str = Query(None, description="CQL_FILTER expression"),
    bbox: str = Query(None, description="xmin,ymin,xmax,ymax"),
    polygon_wkt: str = Query(None, description="WKT polygon to filter by"),
    maxfeatures: int = Query(MAX_FEATURES, le=MAX_FEATURES),
):
    typename = f"dbsm:dbsm_{country.lower()}"  # auto-build typename

    # Spatial filter
    if bbox:
        try:
            xmin, ymin, xmax, ymax = map(float, bbox.split(","))
            bounds_geom = box(xmin, ymin, xmax, ymax)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid bbox format")
    elif polygon_wkt:
        try:
            polygon_geom = wkt.loads(polygon_wkt)
            if polygon_geom.area > MAX_POLYGON_AREA:
                raise HTTPException(
                    status_code=400,
                    detail=f"Polygon area exceeds {MAX_POLYGON_AREA} m²",
                )
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid polygon WKT")
    else:
        bounds_geom = None

    # Build CQL_FILTER
    filters = []
    if cql_filter:
        filters.append(f"({cql_filter})")
    if bbox:
        filters.append(f"BBOX(geom, {xmin}, {ymin}, {xmax}, {ymax})")
    if polygon_wkt:
        filters.append(f"INTERSECTS(geom, {polygon_wkt})")

    full_filter = " AND ".join(filters)

    params = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "GetFeature",
        "typeName": typename,
        "outputFormat": "application/json",
        "maxFeatures": str(maxfeatures),
        "CQL_FILTER": full_filter,
    }

    response = requests.get(GEOSERVER_WFS_URL, params=params)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return JSONResponse(content=response.json())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("geoserver_wfs_fetch:app", host="0.0.0.0", port=8000, reload=True)
