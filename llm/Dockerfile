FROM ghcr.io/ggml-org/llama.cpp:server

WORKDIR /app

# Llama-3.2-1B: Meta's latest small language model
# Excellent for function calling and JSON interpretation
# Fast inference with low memory requirements

# Expose llama.cpp server port
EXPOSE 8080

# Run llama.cpp server with Llama-3.2-1B
# The base image already has ENTRYPOINT ["/app/llama-server"]
# So we only need to provide arguments via CMD
CMD ["--model", "/models/llama-3.2-1b-q4.gguf", \
     "--host", "0.0.0.0", \
     "--port", "8080", \
     "--ctx-size", "4096", \
     "--n-gpu-layers", "0", \
     "--threads", "4", \
     "--jinja"]
