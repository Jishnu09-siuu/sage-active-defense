# 🛡️ SAGE Active Defense System
**Enterprise-Grade Cryptographic File Integrity Monitor (FIM)**

SAGE is a lightweight, real-time Host Intrusion Detection System (HIDS) designed to protect critical directories from unauthorized modifications, deletions, and additions. It utilizes OS-level kernel hooks and cryptographic hashing to ensure zero-trust file integrity.

## Core Features
* **Real-Time Kernel Hooks:** Bypasses traditional timer-based polling by utilizing the `watchdog` library to intercept OS-level file events the millisecond they occur.
* **Cryptographic Baselines:** Uses SHA-256 algorithms to generate mathematically irreversible fingerprints of all protected files.
* **Symmetric Encryption Vault:** The core database (`baseline.enc`) is cryptographically locked using Fernet symmetric encryption.
* **Secure Secrets Management:** The master decryption key is isolated from the application directory and stored locally in a hidden `.env` vault.
* **Active Self-Integrity Checks:** The engine actively monitors its own core files and instantly terminates if cryptographic tampering is detected to prevent poisoning.

##  Tech Stack
* **Engine:** Python 3 (hashlib, cryptography, watchdog)
* **Dashboard:** Streamlit (Real-time UI rendering)
* **Secrets Management:** python-dotenv

##  How to Run
1. Ensure your `.env` vault and `fim.log` files are created (or allow the engine to generate them).
2. Configure your target directories in `config.json`.
3. Start the core engine: `python fim.py`
4. Launch the SOC Dashboard: `streamlit run dashboard.py`