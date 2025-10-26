#include <iostream>
#include <curl/curl.h>
#include <thread>
#include <chrono>
#include <random>
#include <string>
#include <ctime>
#include <cstdlib>

using namespace std; //Niet te veel gebruiken in productie code (kan voor naming conflicts zorgen) std heeft veel componenten met namen die vaak voorkomen

void sendDataPoint(string sensor_id, string metric, double value);
double getRandomValue(double min, double max);

int main() {
    srand(time(NULL));
    
    cout << "Starting sensor simulating" << '\n';
    cout << "Sending data every 5s to InfluxDB" << '\n';
    
    while(true) {
        time_t now = time(NULL);
        cout << "\n" << ctime(&now);
        
        double temperature = getRandomValue(36.0, 38.5);
        double heart_rate = getRandomValue(60.0, 100.0);
        double blood_pressure = getRandomValue(110.0, 140.0);
        double spo2 = getRandomValue(95.0, 100.0);
        double respiration_rate = getRandomValue(12.0, 20.0);
        
        sendDataPoint("sensor_001", "temperature", temperature);
        sendDataPoint("sensor_002", "heart_rate", heart_rate);
        sendDataPoint("sensor_003", "blood_pressure", blood_pressure);
        sendDataPoint("sensor_004", "spo2", spo2);
        sendDataPoint("sensor_005", "respiration_rate", respiration_rate);
        
        this_thread::sleep_for(chrono::seconds(5));       
    }
    
    return 0;
}


void sendDataPoint(string sensor_id, string metric, double value) {
    CURL *curl;
    CURLcode res;
    
    curl = curl_easy_init();
    
    if(curl) {
        

        string url = "http://influxdb:8086/api/v2/write?org=pointcare&bucket=sensors&precision=s";
        
        
        string data = metric + ",sensor_id=" + sensor_id + " value=" + to_string(value); // data formatteren in influxdb "line-protocol format"

        struct curl_slist *headers = NULL;        // headers meegeven voor authenticatie
        headers = curl_slist_append(headers, "Authorization: Token 700d5d63-ef50-47b5-a90c-cdeff2f823b7"); // influxdb requires the format => Authorization: Token <your-token-here>
        headers = curl_slist_append(headers, "Content-Type: text/plain");
        
        
        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());// CURL opties 
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, data.c_str());
        
        
        res = curl_easy_perform(curl);// send het request
        
        if(res != CURLE_OK) {
            cerr << "curl_easy_perform() failed: " << curl_easy_strerror(res) << endl;
        } else {
            cout << "Data sent: " << metric << ": " << value << " (sensor: " << sensor_id << ")" << endl;
        }
        
        curl_slist_free_all(headers); // cleanup voor headers
        curl_easy_cleanup(curl); //same hier voor curl
    } else {
        cerr << "Failed to initialize CURL" << endl;
    }
}

double getRandomValue(double min, double max) 
{
    double range = max - min;
    double randomFraction = (double)rand() / RAND_MAX;
    double scaledValue = randomFraction * range;
    double result = min + scaledValue;
    return result;
}
