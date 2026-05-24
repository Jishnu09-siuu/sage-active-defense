import os
import hashlib
import json
import time
import requests
from cryptography.fernet import Fernet, InvalidToken
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv, set_key

# --- Bulletproof Pathing ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')
BASELINE_FILE = os.path.join(BASE_DIR, 'baseline.enc')
ENV_FILE = os.path.join(BASE_DIR, '.env')
LOG_FILE = os.path.join(BASE_DIR, 'fim.log')

# Load environment variables into memory
load_dotenv(ENV_FILE)

# --- Custom Safe Logging ---
def write_log(level, message):
    """Safely opens, writes, and closes to prevent dashboard clashes."""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a') as f:
        f.write(f"{timestamp} - [{level}] - {message}\n")

# --- Cryptography Engine (Secrets Management) ---
def get_cipher():
    """Loads the master key from the secure environment vault."""
    key = os.getenv('SAGE_MASTER_KEY')
    if not key:
        print("Generating new master encryption key and saving to secure .env vault...")
        key = Fernet.generate_key().decode()
        set_key(ENV_FILE, 'SAGE_MASTER_KEY', key)
        load_dotenv(ENV_FILE) # Reload to pull the new key
    return Fernet(key.encode())

cipher = get_cipher()

# --- External Alerting ---
def send_discord_alert(message):
    webhook_url = "YOUR_DISCORD_WEBHOOK_URL_HERE" 
    if webhook_url != "YOUR_DISCORD_WEBHOOK_URL_HERE":
        try: requests.post(webhook_url, json={"content": f"🚨 **SAGE FIM ALERT** 🚨\n{message}"})
        except Exception as e: print(f"Failed to send external alert: {e}")

# --- Baseline Operations ---
def load_config():
    with open(CONFIG_FILE, 'r') as file: return json.load(file)

def get_file_hash(filepath):
    hasher = hashlib.sha256()
    try:
        with open(filepath, 'rb') as file:
            while chunk := file.read(8192): hasher.update(chunk)
        return hasher.hexdigest()
    except FileNotFoundError: return None

def scan_directories(directories):
    file_hashes = {}
    for directory in directories:
        if not os.path.exists(directory): continue
        for root, _, files in os.walk(directory):
            for file in files:
                filepath = os.path.join(root, file)
                file_hashes[filepath] = get_file_hash(filepath)
    return file_hashes

def save_baseline(baseline_data):
    json_data = json.dumps(baseline_data).encode()
    encrypted_data = cipher.encrypt(json_data)
    with open(BASELINE_FILE, 'wb') as file:
        file.write(encrypted_data)

def load_baseline():
    if not os.path.exists(BASELINE_FILE): return None
    with open(BASELINE_FILE, 'rb') as file:
        encrypted_data = file.read()
    try:
        decrypted_data = cipher.decrypt(encrypted_data)
        return json.loads(decrypted_data.decode())
    except InvalidToken:
        msg = "CRITICAL: baseline.enc has been tampered with! System compromised."
        print(msg); write_log("CRITICAL", msg); send_discord_alert(msg)
        os._exit(1) # Immediate hard kill

def create_baseline(directories):
    print("Creating new encrypted baseline...")
    baseline_data = scan_directories(directories)
    save_baseline(baseline_data)
    print(f"Encrypted baseline saved. Tracking {len(baseline_data)} files.")

# --- Real-Time Kernel Hooks ---
class SAGEEventHandler(FileSystemEventHandler):
    def __init__(self, directories):
        self.directories = directories
        self.baseline = load_baseline()
        if not self.baseline:
            create_baseline(directories)
            self.baseline = load_baseline()

    def process_event(self, filepath, action):
        # Ignore SAGE's own critical files to prevent feedback loops
        if filepath in [LOG_FILE, BASELINE_FILE, ENV_FILE]: return
        
        load_baseline() # Self-Integrity Check

        if action == 'deleted':
            if filepath in self.baseline:
                alert_msg = f"ALERT: File deleted - {filepath}"
                print(alert_msg); write_log("WARNING", alert_msg); send_discord_alert(alert_msg)
                del self.baseline[filepath]
                save_baseline(self.baseline)
        else:
            current_hash = get_file_hash(filepath)
            if not current_hash: return

            if action == 'created':
                if filepath not in self.baseline:
                    alert_msg = f"ALERT: New file added - {filepath}"
                    print(alert_msg); write_log("WARNING", alert_msg); send_discord_alert(alert_msg)
                    self.baseline[filepath] = current_hash
                    save_baseline(self.baseline)
            elif action == 'modified':
                if filepath in self.baseline and self.baseline[filepath] != current_hash:
                    alert_msg = f"ALERT: File modified - {filepath}"
                    print(alert_msg); write_log("WARNING", alert_msg); send_discord_alert(alert_msg)
                    self.baseline[filepath] = current_hash
                    save_baseline(self.baseline)

    def on_modified(self, event):
        if not event.is_directory: self.process_event(os.path.abspath(event.src_path), 'modified')

    def on_created(self, event):
        if not event.is_directory: self.process_event(os.path.abspath(event.src_path), 'created')

    def on_deleted(self, event):
        if not event.is_directory: self.process_event(os.path.abspath(event.src_path), 'deleted')

def monitor(config):
    directories = [os.path.abspath(d) for d in config['directories_to_watch']]
    event_handler = SAGEEventHandler(directories)
    observer = Observer()
    
    for directory in directories:
        if os.path.exists(directory):
            observer.schedule(event_handler, directory, recursive=True)
            
    observer.start()
    print("🛡️ SAGE Active Defense Engine Online.")
    print("📡 Kernel hooks established. Awaiting real-time file events...")
    
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nMonitoring stopped.")
    observer.join()

if __name__ == "__main__": 
    monitor(load_config())