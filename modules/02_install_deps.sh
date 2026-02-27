#!/bin/bash
set -e

echo "[DEPS] Updating package lists..."
apt-get update -qq

echo "[DEPS] Installing core packages..."
DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3-venv \
    python3-pip \
    python3-dev \
    sqlite3 \
    git \
    curl \
    build-essential

echo "[DEPS] Creating Python virtual environment..."
mkdir -p /opt/neuro-lite
python3 -m venv /opt/neuro-lite/venv

# Install Python requirements
CORE_REQ="$(dirname "$0")/../core/requirements.txt"
if [ -f "$CORE_REQ" ]; then
    echo "[DEPS] Installing Python libraries..."
    /opt/neuro-lite/venv/bin/pip install --upgrade pip
    /opt/neuro-lite/venv/bin/pip install -r "$CORE_REQ"
else
    echo "[DEPS] requirements.txt not found."
    exit 1
fi

exit 0
