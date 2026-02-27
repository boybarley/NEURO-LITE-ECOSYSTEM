#!/bin/bash
# NEURO-LITE INSTALLER
# Version: 1.0
# Strictly for Ubuntu 22.04 LTS

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

LOG_FILE="/var/log/neuro_lite_install.log"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (sudo ./install.sh)${NC}"
    exit 1
fi

# Setup Logging
exec > >(tee -a "$LOG_FILE") 2>&1

log_info() {
    echo -e "${GREEN}[INFO] $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}[WARN] $1${NC}"
}

log_error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

# Idempotency Check
if [ -f "/etc/neuro_lite_installed.flag" ]; then
    log_warn "NEURO-LITE already installed. Re-running modules for idempotency."
fi

# Source config
if [ -f "config.env" ]; then
    export $(grep -v '^#' config.env | xargs)
else
    log_error "config.env not found. Aborting."
    exit 1
fi

# Execute Modules
MODULES_DIR="$(dirname "$0")/modules"

for module in "$MODULES_DIR"/*.sh; do
    if [ -f "$module" ]; then
        log_info "Executing module: $(basename "$module")"
        chmod +x "$module"
        if bash "$module"; then
            log_info "Module $(basename "$module") completed successfully."
        else
            log_error "Module $(basename "$module") failed. Aborting installation."
            exit 1
        fi
    fi
done

# Final Flag
touch /etc/neuro_lite_installed.flag
log_info "NEURO-LITE Installation Complete."
