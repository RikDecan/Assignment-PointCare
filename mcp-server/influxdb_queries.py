import os
from influxdb_client import InfluxDBClient

# connection config influxdb
INFLUXDB_URL = os.getenv('INFLUXDB_URL', 'http://influxdb:8086')
INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN', '700d5d63-ef50-47b5-a90c-cdeff2f823b7')
INFLUXDB_ORG = os.getenv('INFLUXDB_ORG', 'pointcare')
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET', 'sensors')

# init influxdb client
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
query_api = client.query_api()


def get_aggregate_data(metric: str, function: str, time_range: str) -> list:
    """
    AGGREGATION: Query InfluxDB for aggregated sensor data
    
    Args:
        metric: Sensor metric (temperature, heart_rate, etc.)
        function: Aggregation function (mean, max, min, count)
        time_range: Time range (5m, 10m, 1h, 24h)
    
    Returns:
        List of aggregated data points
    """
    query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
        |> range(start: -{time_range})
        |> filter(fn: (r) => r._measurement == "{metric}")
        |> {function}()
    '''
    
    result = query_api.query(query=query)
    
    aggregated_data = []
    for table in result:
        for record in table.records:
            data_point = {
                'measurement': record.get_measurement(),
                'value': round(record.get_value(), 2),
                'function': function,
                'time_range': time_range
            }
           
            if '_time' in record.values:
                data_point['timestamp'] = record.values['_time'].isoformat()
            
            aggregated_data.append(data_point)
    
    return aggregated_data


def get_filtered_data(metric: str, operator: str, threshold: float, time_range: str) -> list:
    """
    FILTERING: Query InfluxDB for sensor data exceeding threshold
    
    Args:
        metric: Sensor metric
        operator: Comparison operator (greater, less, equal)
        threshold: Threshold value
        time_range: Time range
    
    Returns:
        List of filtered data points exceeding threshold
    """
    operator_map = {
        'greater': '>',
        'less': '<',
        'equal': '=='
    }
    flux_operator = operator_map.get(operator, '>')
    
    query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
        |> range(start: -{time_range})
        |> filter(fn: (r) => r._measurement == "{metric}")
        |> filter(fn: (r) => r._value {flux_operator} {threshold})
    '''
    
    result = query_api.query(query=query)
    
    filtered_data = []
    for table in result:
        for record in table.records:
            filtered_data.append({
                'sensor_id': record.values.get('sensor_id', 'unknown'),
                'measurement': record.get_measurement(),
                'value': round(record.get_value(), 2),
                'timestamp': record.get_time().isoformat(),
                'exceeded_threshold': True
            })
    
    return filtered_data
