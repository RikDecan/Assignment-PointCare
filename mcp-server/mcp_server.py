from mcp.server.fastmcp import FastMCP
from influxdb_queries import get_aggregate_data, get_filtered_data

mcp = FastMCP("PointCareSensors")


@mcp.tool()
def aggregate_sensor_data(
    metric: str = "temperature",
    function: str = "mean",
    time_range: str = "30m"
) -> dict:
    """
    AGGREGATION: Query time-series database for aggregated sensor data
    
    Args:
        metric: Sensor metric (temperature, heart_rate, blood_pressure, spo2, respiration_rate)
        function: Aggregation function (mean, max, min, count)
        time_range: Time range (5m, 10m, 1h, 24h)
    
    Returns:
        Structured JSON with aggregated result
    """
    try:
        results = get_aggregate_data(metric, function, time_range)
        if results:
            return {
                "query_type": "aggregation",
                "metric": metric,
                "function": function,
                "value": results[0]["value"],
                "time_range": time_range,
                "status": "success"
            }
        return {"status": "error", "message": "No data found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
def filter_sensor_data(
    metric: str = "temperature",
    threshold: float = 37.5,
    time_range: str = "10m"
) -> dict:
    """
    FILTERING: Query sensors exceeding a threshold
    
    Args:
        metric: Sensor metric
        threshold: Threshold value to exceed
        time_range: Time range
    
    Returns:
        Structured JSON with filtered readings
    """
    try:
        results = get_filtered_data(metric, "greater", threshold, time_range)
        return {
            "query_type": "filtering",
            "metric": metric,
            "threshold": threshold,
            "time_range": time_range,
            "count": len(results),
            "exceeding_readings": results,
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
