# Download Phi-3-mini GGUF model for llama.cpp
# Lightweight model (2.3GB) with function calling support

Write-Host "Downloading Phi-3-mini-4k GGUF model..." -ForegroundColor Green

$modelUrl = "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf"
$modelPath = "models/phi-3-mini-4k-instruct-q4.gguf"

# create models directory if it doesn't exist
if (-not (Test-Path "models")) {
    New-Item -ItemType Directory -Path "models"
}

# download model
Write-Host "Downloading from HuggingFace..." -ForegroundColor Yellow
Invoke-WebRequest -Uri $modelUrl -OutFile $modelPath -UseBasicParsing

Write-Host "Model downloaded successfully to $modelPath!" -ForegroundColor Green
Write-Host "Size: $((Get-Item $modelPath).Length / 1GB) GB" -ForegroundColor Cyan
