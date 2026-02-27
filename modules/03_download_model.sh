#!/bin/bash
# Source config
source "$(dirname "$0")/../config.env"

MODEL_PATH="${PROJECT_DIR}/models/${MODEL_FILENAME}"

echo "[MODEL] Checking model existence..."
mkdir -p "${PROJECT_DIR}/models"

# Check if file exists and is valid (> 100MB)
if [ -f "$MODEL_PATH" ]; then
    CURRENT_SIZE=$(stat -c%s "$MODEL_PATH")
    # Basic check for file size > 100MB to assume valid start
    if [ "$CURRENT_SIZE" -gt 100000000 ]; then
        echo "[MODEL] Model already exists (${MODEL_FILENAME}). Skipping download."
        exit 0
    else
        echo "[MODEL] Existing file is too small or corrupt. Removing..."
        rm -f "$MODEL_PATH"
    fi
fi

echo "[MODEL] Downloading ${MODEL_FILENAME} (Resume enabled)..."

# ADDED: -f flag to fail silently on server errors (404, 500, etc.)
# This prevents curl from saving an HTML error page as the model file.
if ! curl -L -f -C - --progress-bar -o "$MODEL_PATH" "$MODEL_URL"; then
    echo "[MODEL] ERROR: Download failed (HTTP error or connection issue)."
    # Clean up partial file
    rm -f "$MODEL_PATH"
    exit 1
fi

# Verification (File size check, GGUF magic number check)
# GGUF Magic Hex: 0x46554747 (Little Endian storage usually, xxd reads raw bytes)
# Standard GGUF magic bytes are 'G' 'G' 'U' 'F' -> Hex: 47 47 55 46
MAGIC=$(xxd -l 4 -p "$MODEL_PATH")

if [ "$MAGIC" == "47475546" ]; then
    echo "[MODEL] Download complete and GGUF format verified."
else
    echo "[MODEL] ERROR: Invalid GGUF magic number (${MAGIC}). File corrupt or not a GGUF model."
    rm "$MODEL_PATH"
    exit 1
fi

exit 0
