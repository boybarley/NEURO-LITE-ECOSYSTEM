#!/bin/bash
set -e

echo "[SERVICE] Creating systemd service..."

USER_NAME=${SUDO_USER:-$USER}
GROUP_NAME=${SUDO_USER:-$USER}

cat <<EOF > /etc/systemd/system/neuro-lite.service
[Unit]
Description=Neuro-Lite AI Server
After=network.target

[Service]
Type=simple
User=${USER_NAME}
Group=${GROUP_NAME}
WorkingDirectory=/opt/neuro-lite
Environment="PATH=/opt/neuro-lite/venv/bin"
ExecStart=/opt/neuro-lite/venv/bin/python3 /opt/neuro-lite/core/main_server.py
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=neuro-lite

# Resource Limits for 4GB RAM
MemoryMax=3G
CPUQuota=80%

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable neuro-lite.service
echo "[SERVICE] Service installed. Start with: systemctl start neuro-lite"

exit 0
