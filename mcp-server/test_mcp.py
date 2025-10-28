"""
Test script voor MCP Server - Simuleert een LLM client
Run from mcp-server folder: uv run python test_mcp.py
"""
import os

# env vars voor connection met influx -> Docker
os.environ['INFLUXDB_URL'] = 'http://localhost:8087'
os.environ['INFLUXDB_TOKEN'] = '700d5d63-ef50-47b5-a90c-cdeff2f823b7'
os.environ['INFLUXDB_ORG'] = 'pointcare'
os.environ['INFLUXDB_BUCKET'] = 'sensors'

from influxdb_queries import get_aggregate_data, get_filtered_data

# print(" Testing InfluxDB Queries...\n")

#T1: avg temperatuur
print("Test 1: avg temperature -> last 10 minutes")
try:
    result = get_aggregate_data("temperature", "mean", "10m")
    if result:
        print(f"success: {result[0]['value']} C")
        print(f"raw data: {result[0]}")
    else:
        print("no data found")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*60 + "\n")

# T2: maximum heart rate
print("T2: max heart rate -> last 40 minutes")
try:
    result = get_aggregate_data("heart_rate", "max", "40m")
    if result:
        print(f"success: {result[0]['value']} bpm")
        print(f"raw data: {result[0]}")
    else:
        print("No data found")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*60 + "\n")

# T3: filter high temperatures
print("T3: temps above 37.5°C -> last 30 minutes")
try:
    result = get_filtered_data("temperature", "greater", 37.5, "30m")
    print(f"success: found {len(result)} readings above threshold")
    if result:
        print(f"sample: {result[0]}")
    else:
        print("   (no readings exceeded threshold)")
except Exception as e:
    print(f"error: {e}")

print("\n" + "="*60 + "\n")

# T4: count all temp readings
print("T4: Count temperature readings -> last 30 minutes")
try:
    result = get_aggregate_data("temperature", "count", "30m")
    if result:
        print(f"success: {int(result[0]['value'])} total readings")
        print(f"raw data: {result[0]}")
    else:
        print("no data found")
except Exception as e:
    print(f"error: {e}")

print("\n testing complete...")
