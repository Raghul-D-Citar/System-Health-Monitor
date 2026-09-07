#!/usr/bin/env bash
set -euo pipefail

# Generates a local self-signed certificate for Nginx Phase 5 testing.
# Output files:
#   nginx/certs/dev.crt
#   nginx/certs/dev.key

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CERT_DIR="${SCRIPT_DIR}/../certs"

mkdir -p "${CERT_DIR}"

openssl req -x509 -nodes -newkey rsa:2048 \
  -keyout "${CERT_DIR}/dev.key" \
  -out "${CERT_DIR}/dev.crt" \
  -days 365 \
  -subj "/C=XX/ST=Local/L=Local/O=SystemHealthMonitor/OU=Phase5/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"

echo "Created: ${CERT_DIR}/dev.crt"
echo "Created: ${CERT_DIR}/dev.key"
