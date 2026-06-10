#!/usr/bin/env bash
set -euo pipefail

mkdir -p storage/models storage/builds storage/prometheus
echo '[]' > storage/prometheus/inference_targets.json

echo "Storage directories ready."
