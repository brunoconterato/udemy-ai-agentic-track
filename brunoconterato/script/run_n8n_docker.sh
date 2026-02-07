#!/usr/bin/env bash
set -euo pipefail

# Directory on host to persist n8n data (can be overridden with N8N_DATA_DIR)
N8N_DATA_DIR="${N8N_DATA_DIR:-$PWD/.n8n}"
mkdir -p "$N8N_DATA_DIR"

docker run -it --rm \
    --name n8n \
    -v "$N8N_DATA_DIR":/home/node/.n8n \
    -p 5678:5678 \
    -e GENERIC_TIMEZONE="America/Sao_Paulo" \
    -e TZ="America/Sao_Paulo" \
    -e N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true \
    -e N8N_RUNNERS_ENABLED=true \
    docker.n8n.io/n8nio/n8n