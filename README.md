
<div align="center">

# NEURO-LITE ECOSYSTEM
**The Speculative Empathic Engine**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Ubuntu](https://img.shields.io/badge/OS-Ubuntu%2022.04%20LTS-E95420?logo=ubuntu&logoColor=white)](https://ubuntu.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Hardware](https://img.shields.io/badge/Optimized-4GB%20RAM%20%7C%20i3%20CPU-success)]()

*An illusion of intelligence designed for extreme hardware constraints.*

[Features](#-key-features) • [Installation](#-installation) • [Usage](#-usage) • [Architecture](#-architecture)

</div>

---

## 📜 Overview

**NEURO-LITE ECOSYSTEM** is a production-grade, conversational AI system architected specifically for low-resource environments. It is designed to run entirely on an **Intel i3 CPU with 4GB RAM** without GPU acceleration.

### The Philosophy: "Illusion of Intelligence"
Instead of relying on massive model parameters, this system achieves a "fast, professional, and empathetic" feel through:
1.  **Single Pass Inference:** No chain-of-thought or multi-step reasoning. One inference call only.
2.  **Rule-Based Polishing:** Python logic modifies tone and formatting in < 2ms post-inference.
3.  **Micro-RAG:** SQLite FTS5 for deterministic, sub-10ms knowledge retrieval (no vector DBs).

---

## ✨ Key Features

-   **Ultra-Lightweight:** Optimized for 4GB RAM and Dual-Core CPUs.
-   **Low Latency Perception:** Emotional analysis and RAG retrieval happen almost instantly before inference.
-   **Zero-Trust Data Ingestion:** Developer tools to strip PII and toxic content from training data.
-   **Self-Healing Service:** Systemd service with auto-restart and graceful shutdown.
-   **Complete Pipeline:** Includes OS tuning, dependency setup, model downloading, and service deployment.

---

## 🛠️ Prerequisites

Before installing, ensure you have:
-   **OS:** Ubuntu 22.04 LTS (Clean install recommended).
-   **Hardware:** 
    -   Intel i3 (or equivalent).
    -   4GB RAM.
    -   ~5GB Disk Space (for OS, Swap, and Model).
-   **Privileges:** `sudo` root access.

---

## 🚀 Installation

Follow these steps to install the full ecosystem on your server.

### 1. Clone the Repository
Clone the project into the `/opt` directory for system-wide access.

```bash
sudo git clone https://github.com/boybarley/NEURO-LITE-ECOSYSTEM.git /opt/neuro-lite
cd /opt/neuro-lite
```

### 2. Make Installer Executable
Grant execution permissions to the main installer script.

```bash
sudo chmod +x install.sh
```

### 3. Run the Installer
Execute the installer script. This process is **idempotent** (safe to run multiple times) and fully automated. It will:
1.  Tune OS parameters (Swappiness, CPU Governor).
2.  Create a 2GB swap file if missing.
3.  Install Python dependencies.
4.  Download the `Qwen2.5-3B-Instruct-Q4_K_M.gguf` model.
5.  Setup the systemd service.

```bash
sudo ./install.sh
```

*Note: The model download is approx 2GB. Please wait for the process to complete.*

---

## 💻 Usage

### Accessing the Web Interface
Once the installation completes, the service starts automatically.

1.  Open your web browser.
2.  Navigate to:
    ```
    http://<YOUR_SERVER_IP>:8000
    ```
    *(If running locally, use `http://localhost:8000`)*

### Managing the Service
You can control the background service using standard `systemctl` commands:

**Check Status:**
```bash
sudo systemctl status neuro-lite
```

**Stop the Service:**
```bash
sudo systemctl stop neuro-lite
```

**Restart the Service:**
```bash
sudo systemctl restart neuro-lite
```

**View Logs:**
```bash
journalctl -u neuro-lite -f
```

---

## 🏗️ Architecture

The system prioritizes speed over reasoning complexity using a linear pipeline.

```mermaid
graph TD
    A[User Input] --> B(Emotional Analyzer)
    B -->|Regex Scoring| C{RAG Engine}
    C -->|SQLite FTS5| D[Context Manager]
    D -->|Sliding Window| E[Llama.cpp Inference]
    E -->|CPU Optimized| F[Post Processor]
    F -->|Rule Polisher| G[User Output]
```

### Component Specs
| Component | Technology | Constraint |
| :--- | :--- | :--- |
| **LLM** | Llama.cpp (Qwen 2.5 3B) | Single Pass, No GPU |
| **RAG** | SQLite FTS5 | Sub-10ms retrieval |
| **Emotion** | Regex + Heuristics | < 1ms execution |
| **Memory** | Sliding Window + Heuristic Bridge | Prevents context overflow |

---

## 🛠️ Developer Tools

Located in the `developer_tools/` directory for pre-release data preparation.

1.  **`distill_knowledge.py`**: Generates SOP Q&A from a Premium AI API and stores it in SQLite.
2.  **`validate_data.py`**: Scans crowdsourced data for PII, toxicity, and duplicates (Zero Trust).
3.  **`build_release.py`**: Packages the system into a deployable `tar.gz` artifact.

---

## 📁 Project Structure

```text
NEURO-LITE-ECOSYSTEM/
├── install.sh              # Main entry point for installation
├── config.env              # Configuration variables
├── modules/                # Installation scripts
│   ├── 01_os_tuning.sh
│   ├── 02_install_deps.sh
│   ├── 03_download_model.sh
│   └── 04_setup_service.sh
├── core/                   # Application logic
│   ├── main_server.py      # FastAPI entry point
│   ├── rag_engine.py       # Retrieval logic
│   ├── emotional_state.py  # Sentiment analysis
│   └── ...
├── webui/                  # Frontend assets
└── developer_tools/        # Factory side scripts
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
Made with ☕ and engineering pragmatism by <a href="https://boybarley.com">boybarley</a>.
</div>
```
