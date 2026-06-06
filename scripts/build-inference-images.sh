#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

docker build -t ai-platform/inference-sklearn:latest "${ROOT_DIR}/inference/sklearn"
docker build -t ai-platform/inference-onnx:latest "${ROOT_DIR}/inference/onnx"
docker build -t ai-platform/inference-pytorch:latest "${ROOT_DIR}/inference/pytorch"

echo "Inference images built successfully."
