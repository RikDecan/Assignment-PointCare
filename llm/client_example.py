"""
LLM Client Example - PointCare Technical Challenge
Demonstrates LLM querying MCP server dynamically using function calling

Author: Rik Decan
"""

import requests
import json
import time
from datetime import datetime

# Configuration
MCP_URL = "http://localhost"
LLM_URL = "http://localhost:8080"


def main():
    print("\n" + "="*70)
    print("LLM Client Example - PointCare Technical Challenge")
    print("Demonstrating: LLM querying MCP server dynamically")
    print("="*70 + "\n")
    
    # Define tools for LLM to query sensor data
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_sensor_aggregate",
                "description": "Get aggregated sensor data from time-series database",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "metric": {
                            "type": "string",
                            "enum": ["temperature", "heart_rate", "blood_pressure", "spo2", "respiration_rate"]
                        },
                        "function": {
                            "type": "string",
                            "enum": ["mean", "max", "min"]
                        },
                        "time_range": {
                            "type": "string",
                            "enum": ["5m", "10m", "1h"]
                        }
                    },
                    "required": ["metric", "function", "time_range"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "filter_sensor_data",
                "description": "Filter sensor readings based on threshold",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "metric": {
                            "type": "string",
                            "enum": ["temperature", "heart_rate", "blood_pressure", "spo2", "respiration_rate"]
                        },
                        "operator": {
                            "type": "string",
                            "enum": ["greater", "less"]
                        },
                        "threshold": {
                            "type": "number"
                        },
                        "time_range": {
                            "type": "string",
                            "enum": ["5m", "10m", "1h"]
                        }
                    },
                    "required": ["metric", "operator", "threshold", "time_range"]
                }
            }
        }
    ]
    
    # ========================================================================
    # PROOF 1: Connect to MCP server over HTTP
    # ========================================================================
    print("PROOF 1: LLM connects to MCP server over HTTP")
    print("-" * 70)
    print(f"Connection: LLM ({LLM_URL}) -> MCP Server ({MCP_URL})")
    print("Protocol: HTTP (via Nginx reverse proxy)")
    print()
    
    # ========================================================================
    # PROOF 2: Query time-series database for AGGREGATION
    # ========================================================================
    print("PROOF 2a: Aggregation Query (average temperature)")
    print("-" * 70)
    
    # aggregation_prompt = "What is the average temperature over the last 10 minutes?"
    aggregation_prompt = "What is the average temperature over the last 5 minutes?" #FIXME
    print(f"User Query: {aggregation_prompt}")
    print("Sending request to LLM...", end="", flush=True)
    
    agg_response = requests.post(
        f"{LLM_URL}/v1/chat/completions",
        json={
            "model": "llama-3.2-1b",
            "messages": [
                {"role": "system", "content": "Use tools to query sensor data from the time-series database."},
                {"role": "user", "content": aggregation_prompt}
            ],
            "tools": tools,
            "temperature": 0.1
        },
        timeout=30
    )
    
    agg_result = agg_response.json()
    agg_message = agg_result["choices"][0]["message"]
    print(" Done!\n")
    
    if "tool_calls" in agg_message:
        tool_call = agg_message["tool_calls"][0]
        function_name = tool_call["function"]["name"]
        arguments = json.loads(tool_call["function"]["arguments"])
        
        print(f"LLM Function Call: {function_name}")
        print(f"Parameters: {json.dumps(arguments, indent=2)}")
        
        # Execute MCP query
        mcp_response = requests.post(
            f"{MCP_URL}/api/aggregate",
            json=arguments
        )
        agg_data = mcp_response.json()
        
        print(f"\nMCP Response (JSON):")
        print(json.dumps(agg_data, indent=2))
        print(f"\nResult: {agg_data['value']}°C")
    
    print("\n" + "="*70 + "\n")
    
    # ========================================================================
    # PROOF 2: Query time-series database for FILTERING
    # ========================================================================
    print("PROOF 2b: Filtering Query (heart rate above threshold)")
    print("-" * 70)
    
    filtering_prompt = "Show me readings where heart rate exceeds 85 bpm in the last hour"
    print(f"User Query: {filtering_prompt}")
    print("Sending request to LLM...", end="", flush=True)
    
    filter_response = requests.post(
        f"{LLM_URL}/v1/chat/completions",
        json={
            "model": "llama-3.2-1b",
            "messages": [
                {"role": "system", "content": "Use tools to query and filter sensor data from the time-series database."},
                {"role": "user", "content": filtering_prompt}
            ],
            "tools": tools,
            "temperature": 0.1
        },
        timeout=30
    )
    
    filter_result = filter_response.json()
    filter_message = filter_result["choices"][0]["message"]
    print(" Done!\n")
    
    if "tool_calls" in filter_message:
        tool_call = filter_message["tool_calls"][0]
        function_name = tool_call["function"]["name"]
        arguments = json.loads(tool_call["function"]["arguments"])
        
        print(f"LLM Function Call: {function_name}")
        print(f"Parameters: {json.dumps(arguments, indent=2)}")
        
        # Execute MCP filter query
        mcp_response = requests.post(
            f"{MCP_URL}/api/filter",
            json=arguments
        )
        filter_data = mcp_response.json()
        
        print(f"\nMCP Response (JSON):")
        # Uncommenten om volledige JSON te zien vv
        # print(json.dumps(filter_data, indent=2))
        print(f"\nFiltered Results: {filter_data['count']} readings exceed threshold")
    
    print("\n" + "="*70 + "\n")
    
    # ========================================================================
    # PROOF 3: Use JSON responses for reasoning and meaningful answers
    # ========================================================================
    print("PROOF 3: LLM uses JSON responses for clinical reasoning")
    print("-" * 70)

    # clinical_prompt = "Analyze the patient's vital signs over the 10 minutes. Provide a brief clinical assessment in maximum 3 sentences."  #FIXME:
    clinical_prompt = "Analyze the patient's vital signs over the 5 minutes. Provide a brief clinical assessment in maximum 3 sentences."
    print(f"User Query: {clinical_prompt}\n")
    
    # Gather all vital signs data
    print("Gathering vital signs data via MCP...")
    vital_signs = {}
    metrics = ["temperature", "heart_rate", "blood_pressure", "spo2", "respiration_rate"]
    
    for metric in metrics:
        mcp_response = requests.post(
            f"{MCP_URL}/api/aggregate",
            json={"metric": metric, "function": "mean", "time_range": "10m"}
        )
        data = mcp_response.json()
        vital_signs[metric] = data['value']
        print(f"  {metric}: {data['value']}")
    
    # LLM reasoning with collected JSON data
    reasoning_prompt = f"""Based on these patient vital signs (JSON data from time-series database):
{json.dumps(vital_signs, indent=2)}

Provide a brief clinical assessment in maximum 3 sentences focusing on clinical relevance."""

    print(f"\nLLM Clinical Reasoning (using JSON context)...")
    print("Sending clinical data to LLM for analysis...", end="", flush=True)
    
    reasoning_response = requests.post(
        f"{LLM_URL}/v1/chat/completions",
        json={
            "model": "llama-3.2-1b",
            "messages": [
                {"role": "system", "content": "You are a medical professional. Analyze the provided vital signs data and give a concise clinical assessment."},
                {"role": "user", "content": reasoning_prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 150
        },
        timeout=30
    )
    
    reasoning_result = reasoning_response.json()
    clinical_assessment = reasoning_result["choices"][0]["message"]["content"]
    print(" Done!\n")
    print(f"{clinical_assessment}")
    
    print("\n" + "="*70 + "\n")
    
    # ========================================================================
    # PROOF 4: Demonstrate DYNAMIC data (not hard-coded)
    # ========================================================================
    print("PROOF 4: Data is dynamically retrieved from live database")
    print("-" * 70)
    print("Demonstrating: Two queries with time gap show different results\n")
    
    # First query
    print(f"[Query 1] Timestamp: {datetime.now().strftime('%H:%M:%S')}")
    query1_response = requests.post(
        f"{MCP_URL}/api/aggregate",
        json={"metric": "heart_rate", "function": "mean", "time_range": "5m"}
    )
    query1_data = query1_response.json()
    print(f"Heart Rate (5min avg): {query1_data['value']:.2f} bpm")
    
    # new data to arrive
    print("\nWaiting 20 seconds for new sensor data to arrive...")
    time.sleep(20)
    

    print(f"\n[Query 2] Timestamp: {datetime.now().strftime('%H:%M:%S')}")
    query2_response = requests.post(
        f"{MCP_URL}/api/aggregate",
        json={"metric": "heart_rate", "function": "mean", "time_range": "5m"}
    )
    query2_data = query2_response.json()
    print(f"Heart Rate (5min avg): {query2_data['value']:.2f} bpm")
    
    difference = abs(query2_data['value'] - query1_data['value'])
    print(f"\n Difference => {difference:.2f} bpm")
    

if __name__ == "__main__":
    main()
