#!/bin/bash
# Download Phi-3-mini GGUF model for llama.cpp
# This model supports function calling and is lightweight (2.3GB)

echo "Downloading Phi-3-mini-4k GGUF model..."
wget https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf -O models/phi-3-mini-4k-instruct-q4.gguf

echo "Phi-3-mini download successful"
