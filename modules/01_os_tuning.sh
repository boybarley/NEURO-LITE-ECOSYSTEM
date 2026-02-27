#!/bin/bash
set -e

echo "[OS TUNING] Applying kernel parameters..."

# Swappiness (Persistent)
if grep -q "vm.swappiness" /etc/sysctl.conf; then
    sed -i 's/vm.swappiness=.*/vm.swappiness=10/' /etc/sysctl.conf
else
    echo "vm.swappiness=10" >> /etc/sysctl.conf
fi
sysctl -p > /dev/null 2>&1

# CPU Governor
for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    if [ -f "$cpu" ]; then
        echo "performance" > "$cpu"
    fi
done

# Hugepage Detection (Advisory only for 4GB RAM systems)
HUGEPAGES=$(cat /proc/meminfo | grep HugePages_Total | awk '{print $2}')
if [ "$HUGEPAGES" -gt 0 ]; then
    echo "[OS TUNING] Hugepages detected ($HUGEPAGES). Recommended for performance, ensure model fits."
fi

# Swap Creation
SWAP_EXIST=$(swapon --show | wc -l)
if [ "$SWAP_EXIST" -lt 1 ]; then
    echo "[OS TUNING] Creating 2GB swap file..."
    fallocate -l 2G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=2048
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo "/swapfile none swap sw 0 0" >> /etc/fstab
else
    echo "[OS TUNING] Swap already present. Skipping creation."
fi

exit 0
