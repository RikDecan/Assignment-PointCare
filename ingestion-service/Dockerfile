FROM gcc:latest

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    libcurl4-openssl-dev \
    cmake \
    && rm -rf /var/lib/apt/lists/*

COPY CMakeLists.txt .
COPY src/ ./src/

RUN cmake . && make

CMD ["./sensor_simulator"]