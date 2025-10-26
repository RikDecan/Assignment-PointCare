cmake_minimum_required(VERSION 3.10)
project(SensorSimulator)

set(CMAKE_CXX_STANDARD 17)

find_package(CURL REQUIRED)

add_executable(sensor_simulator src/main.cpp)
target_link_libraries(sensor_simulator CURL::libcurl pthread)