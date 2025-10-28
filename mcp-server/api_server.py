"""
HTTP API endpoints voor MCP Server - Voor gebruik met reverse proxy
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from influxdb_queries import get_aggregate_data, get_filtered_data

app = FastAPI(title="PointCare MCP API", version="1.0.0")


class AggregateRequest(BaseModel):
    metric: str = "temperature"
    function: str = "mean"
    time_range: str = "10m"


class FilterRequest(BaseModel):
    metric: str = "temperature"
    threshold: float = 37.5
    operator: str = "greater"
    time_range: str = "10m"


@app.get("/")
def root():
    return {
        "service": "PointCare MCP Server",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/api/aggregate")
def aggregate(request: AggregateRequest):
    """AGGREGATION: Get aggregated sensor data"""
    try:
        results = get_aggregate_data(request.metric, request.function, request.time_range)
        if results:
            return {
                "query_type": "aggregation",
                "metric": request.metric,
                "function": request.function,
                "value": results[0]["value"],
                "time_range": request.time_range,
                "status": "success"
            }
        raise HTTPException(status_code=404, detail="No data found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/filter")
def filter_data(request: FilterRequest):
    """FILTERING: Get sensor readings exceeding threshold"""
    try:
        results = get_filtered_data(request.metric, request.operator, request.threshold, request.time_range)
        return {
            "query_type": "filtering",
            "metric": request.metric,
            "threshold": request.threshold,
            "operator": request.operator,
            "time_range": request.time_range,
            "count": len(results),
            "exceeding_readings": results,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
