#include <iostream>
#include <thread>
#include <chrono>
#include <random>
#include <string>
#include <ctime>
#include <cstdlib>
#include <sstream>
#include <iomanip>

//Boost voor de HTTP requests
#include <boost/beast/core.hpp>
#include <boost/beast/http.hpp>
#include <boost/asio/connect.hpp>
#include <boost/asio/ip/tcp.hpp>

using namespace std; //Niet te veel gebruiken in productie code (kan voor naming conflicts zorgen) std heeft veel componenten met namen die vaak voorkomen
namespace beast = boost::beast;
namespace http = beast::http;
namespace net = boost::asio;
using tcp = net::ip::tcp;


class InfluxSender {
public:
    InfluxSender(const string& host, const string& port, const string& target)
        : host_(host), port_(port), target_(target), stream_(ioc_) {
        auto const results = resolver_.resolve(host_, port_);
        stream_.connect(results);
    }

    ~InfluxSender() {
        beast::error_code ec;
        stream_.socket().shutdown(tcp::socket::shutdown_both, ec);
    }

    void sendDataPoint(const string& sensor_id, const string& metric, double value) {
        // Format value to 2 decimal places
        ostringstream oss;
        oss << fixed << setprecision(2) << value;
        string value_str = oss.str();
        string data = metric + ",sensor_id=" + sensor_id + " value=" + value_str;

        http::request<http::string_body> req{http::verb::post, target_, 11};
        req.set(http::field::host, host_);
        req.set(http::field::authorization, "Token 700d5d63-ef50-47b5-a90c-cdeff2f823b7");
        req.set(http::field::content_type, "text/plain");
        req.body() = data;
        req.prepare_payload();

        http::write(stream_, req);

        beast::flat_buffer buffer;
        http::response<http::dynamic_body> res;
        http::read(stream_, buffer, res);

        if (res.result() != http::status::no_content && res.result() != http::status::ok) {
            cerr << "HTTP error: " << res.result_int() << " - " << res.reason() << endl;
        } else {
            cout << "Data sent: " << metric << ": " << value << " (sensor: " << sensor_id << ")" << endl;
        }
    }

private:
    string host_;
    string port_;
    string target_;
    net::io_context ioc_;
    tcp::resolver resolver_{ioc_};
    beast::tcp_stream stream_;
};


double getRandomValue(double min, double max) 
{
    double range = max - min;
    double randomFraction = (double)rand() / RAND_MAX;
    double scaledValue = randomFraction * range;
    double result = min + scaledValue;
    return result;
}


void sendDataPoint(string sensor_id, string metric, double value);
double getRandomValue(double min, double max);

int main() {
    srand(time(0));
    InfluxSender sender("influxdb", "8086", "/api/v2/write?org=pointcare&bucket=sensors&precision=s");

    while(true) {
        time_t now = time(0);
        cout << "\n" << ctime(&now);

        double temperature = getRandomValue(36.0, 38.5);
        double heart_rate = getRandomValue(60.0, 100.0);
        double blood_pressure = getRandomValue(110.0, 140.0);
        double spo2 = getRandomValue(95.0, 100.0);
        double respiration_rate = getRandomValue(12.0, 20.0);

        sender.sendDataPoint("sensor_001", "temperature", temperature);
        sender.sendDataPoint("sensor_002", "heart_rate", heart_rate);
        sender.sendDataPoint("sensor_003", "blood_pressure", blood_pressure);
        sender.sendDataPoint("sensor_004", "spo2", spo2);
        sender.sendDataPoint("sensor_005", "respiration_rate", respiration_rate);

        this_thread::sleep_for(chrono::seconds(5));       
    }

    return 0;
}



