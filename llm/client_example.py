
# LLM Client Example - PointCare Technical Challenge
# Demonstreert dynamisch opvragen van sensor-data via LLM en MCP server


import requests  # HTTP-requests naar LLM en MCP server
import json      # JSON encoding/decoding
import time      # Voor time.sleep()
from datetime import datetime  # Voor timestamps


# Configuratie van endpoints
MCP_URL = "http://localhost"           # MCP server URL
LLM_URL = "http://localhost:8080"      # LLM server URL


def main():
    # Hoofdfunctie: voert alle demo-proofs uit
    print("\n" + "="*70)
    print("LLM Client Example - PointCare Technical Challenge")
    print("Demonstrating: LLM querying MCP server dynamically")
    print("="*70 + "\n")
    
    # Tools-definitie: beschrijft welke functies de LLM mag aanroepen
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
    
    # === PROOF 1: Verbind met MCP server via HTTP ===
    print("PROOF 1: LLM connects to MCP server over HTTP")
    print("-" * 70)
    print(f"Connection: LLM ({LLM_URL}) -> MCP Server ({MCP_URL})")
    print("Protocol: HTTP (via Nginx reverse proxy)")
    print()
    
    # === PROOF 2a: Aggregatie-query (gemiddelde temperatuur) ===
    print("PROOF 2a: Aggregation Query (average temperature)")
    print("-" * 70)
    
    # aggregation_prompt = "What is the average temperature over the last 10 minutes?"
    aggregation_prompt = "What is the average temperature over the last 5 minutes?" #FIXME
    print(f"User Query: {aggregation_prompt}")
    print("Sending request to LLM...", end="", flush=True)
    
    # Stuur prompt naar LLM, vraag om gemiddelde temperatuur
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
    
    agg_result = agg_response.json()  # Antwoord van LLM (JSON)
    agg_message = agg_result["choices"][0]["message"]  # Eerste message uit response
    print(" Done!\n")
    
    # Check of LLM een functie-aanroep doet (function calling)
    if "tool_calls" in agg_message:
        tool_call = agg_message["tool_calls"][0]  # Pak eerste tool_call
        function_name = tool_call["function"]["name"]  # Functienaam
        arguments = json.loads(tool_call["function"]["arguments"])  # Argumenten als dict
        
        print(f"LLM Function Call: {function_name}")
        print(f"Parameters: {json.dumps(arguments, indent=2)}")
        
        # Stuur parameters door naar MCP server (aggregation endpoint)
        mcp_response = requests.post(
            f"{MCP_URL}/api/aggregate",
            json=arguments
        )
        agg_data = mcp_response.json()  # Antwoord van MCP
        
        print(f"\nMCP Response (JSON):")
        print(json.dumps(agg_data, indent=2))
        print(f"\nResult: {agg_data['value']}°C")
    
    print("\n" + "="*70 + "\n")
    
    # === PROOF 2b: Filter-query (hartslag boven drempel) ===
    print("PROOF 2b: Filtering Query (heart rate above threshold)")
    print("-" * 70)
    
    filtering_prompt = "Show me readings where heart rate exceeds 85 bpm in the 10 minutes."
    print(f"User Query: {filtering_prompt}")
    print("Sending request to LLM...", end="", flush=True)
    
    # Stuur filterprompt naar LLM
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
    
    filter_result = filter_response.json()  # Antwoord van LLM
    filter_message = filter_result["choices"][0]["message"]
    print(" Done!\n")
    
    # Check of LLM een filterfunctie aanroept
    if "tool_calls" in filter_message:
        tool_call = filter_message["tool_calls"][0]
        function_name = tool_call["function"]["name"]
        arguments = json.loads(tool_call["function"]["arguments"])
        
        print(f"LLM Function Call: {function_name}")
        print(f"Parameters: {json.dumps(arguments, indent=2)}")
        
        # Stuur filterparameters naar MCP server (filter endpoint)
        mcp_response = requests.post(
            f"{MCP_URL}/api/filter",
            json=arguments
        )
        filter_data = mcp_response.json()
        
        print(f"\nMCP Response (JSON):")
        # print(json.dumps(filter_data, indent=2))  # Volledige JSON indien gewenst
        print(f"\nFiltered Results: {filter_data['count']} readings exceed threshold")
    
    print("\n" + "="*70 + "\n")
    
    # === PROOF 3: LLM redeneert op basis van JSON-data ===
    print("PROOF 3: LLM uses JSON responses for clinical reasoning")
    print("-" * 70)

    # clinical_prompt = "Analyze the patient's vital signs over the 10 minutes. Provide a brief clinical assessment in maximum 3 sentences."  #FIXME
    clinical_prompt = "Analyze the patient's vital signs over the 5 minutes. Provide a brief clinical assessment in maximum 3 sentences."
    print(f"User Query: {clinical_prompt}\n")
    
    # Haal alle vitale waarden op via MCP (gemiddelde per metric)
    print("Gathering vital signs data via MCP...")
    vital_signs = {}
    metrics = ["temperature", "heart_rate", "blood_pressure", "spo2", "respiration_rate"]
    
    for metric in metrics:
        mcp_response = requests.post(
            f"{MCP_URL}/api/aggregate",
            json={"metric": metric, "function": "mean", "time_range": "10m"}
        )
        data = mcp_response.json()
        vital_signs[metric] = data['value']  # Sla waarde op per metric
        print(f"  {metric}: {data['value']}")
    
    # Geef JSON-data als context aan LLM voor klinische analyse
    reasoning_prompt = f"""Based on these patient vital signs (JSON data from time-series database):
{json.dumps(vital_signs, indent=2)}

Provide a brief clinical assessment in maximum 3 sentences focusing on clinical relevance."""

    print(f"\nLLM Clinical Reasoning (using JSON context)...")
    print("Sending clinical data to LLM for analysis...", end="", flush=True)
    
    # Stuur klinische prompt + data naar LLM
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
    clinical_assessment = reasoning_result["choices"][0]["message"]["content"]  # Antwoord van LLM
    print(" Done!\n")
    print(f"{clinical_assessment}")
    
    print("\n" + "="*70 + "\n")
    
    # === PROOF 4: Toon dynamische data (geen hard-coded waarden) ===
    print("PROOF 4: Data is dynamically retrieved from live database")
    print("-" * 70)
    print("Demonstrating: Two queries with time gap show different results\n")
    
    # Eerste query: hartslag ophalen
    print(f"[Query 1] Timestamp: {datetime.now().strftime('%H:%M:%S')}")
    query1_response = requests.post(
        f"{MCP_URL}/api/aggregate",
        json={"metric": "heart_rate", "function": "mean", "time_range": "5m"}
    )
    query1_data = query1_response.json()
    print(f"Heart Rate (5min avg): {query1_data['value']:.2f} bpm")
    
    # Wacht op nieuwe data
    print("\nWaiting 20 seconds for new sensor data to arrive...")
    time.sleep(20)
    
    # Tweede query: nieuwe hartslag ophalen
    print(f"\n[Query 2] Timestamp: {datetime.now().strftime('%H:%M:%S')}")
    query2_response = requests.post(
        f"{MCP_URL}/api/aggregate",
        json={"metric": "heart_rate", "function": "mean", "time_range": "5m"}
    )
    query2_data = query2_response.json()
    print(f"Heart Rate (5min avg): {query2_data['value']:.2f} bpm")
    
    # Verschil tonen
    difference = abs(query2_data['value'] - query1_data['value'])
    print(f"\n Difference => {difference:.2f} bpm")
if __name__ == "__main__":
    main()
