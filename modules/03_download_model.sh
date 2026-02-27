#!/bin/bash
# Source config
source "$(dirname "$0")/../config.env"

MODEL_PATH="${PROJECT_DIR}/models/${MODEL_FILENAME}"

echo "[MODEL] Checking model existence..."
mkdir -p "${PROJECT_DIR}/models"

if [ -f "$MODEL_PATH" ]; then
    CURRENT_SIZE=$(stat -c%s "$MODEL_PATH")
    # Basic check for file size > 100MB to assume valid start
    if [ "$CURRENT_SIZE" -gt 100000000 ]; then
        echo "[MODEL] Model already exists. Skipping download."
        exit 0
    fi
fi

echo "[MODEL] Downloading Qwen2.5-3B-Instruct-Q4_K_M.gguf (Resume enabled)..."
curl -L -C - --progress-bar -o "$MODEL_PATH" "$MODEL_URL"

# Verification (File size check, GGUF magic number check)
# GGUF Magic: 0x46554747
MAGIC=$(xxd -l 4 -p "$MODEL_PATH")
if [ "$MAGIC" == "47475546" ]; then
    echo "[MODEL] Download complete and GGUF format verified."
else
    echo "[MODEL] ERROR: Invalid GGUF magic number. File corrupt."
    rm "$MODEL_PATH"
    exit 1
fi

exit 0
