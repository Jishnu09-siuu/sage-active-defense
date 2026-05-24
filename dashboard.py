import streamlit as st
import json
import os
import time
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# --- Bulletproof Pathing ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, 'fim.log')
ARCHIVE_FILE = os.path.join(BASE_DIR, 'archive.log')
BASELINE_FILE = os.path.join(BASE_DIR, 'baseline.enc')
ENV_FILE = os.path.join(BASE_DIR, '.env')

# Load the secret environment variables
load_dotenv(ENV_FILE)

# --- Page Config ---
st.set_page_config(page_title="SAGE FIM Dashboard", page_icon="🛡️", layout="wide")
st.title("🛡️ SAGE Active Defense: Secured FIM Dashboard")
st.markdown("Live monitoring dashboard for unauthorized system changes. Baseline is cryptographically secured.")

# --- Sidebar for Controls ---
with st.sidebar:
    st.header("⚙️ Dashboard Controls")
    auto_refresh = st.checkbox("Live Auto-Refresh (2s)", value=True)
    
    st.divider()
    st.subheader("🧹 Incident Management")
    st.write("Clear active alerts and move them to history.")
    
    if st.button("Acknowledge & Archive Alerts"):
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                logs = f.readlines()
            with open(ARCHIVE_FILE, 'a') as f:
                f.writelines(logs)
            with open(LOG_FILE, 'w') as f:
                f.write("")
            st.success("Alerts archived! Environment clean.")
            time.sleep(1)
            st.rerun()

# --- Main Layout ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 System Baseline Status")
    
    # Fetch the key from the environment securely
    master_key = os.getenv('SAGE_MASTER_KEY')
    
    if os.path.exists(BASELINE_FILE) and master_key:
        try:
            cipher = Fernet(master_key.encode())
            with open(BASELINE_FILE, 'rb') as f:
                decrypted_data = cipher.decrypt(f.read())
                baseline_data = json.loads(decrypted_data.decode())
                
            st.success(f"🔒 Encrypted Baseline Active. Monitoring {len(baseline_data)} files.")
            st.dataframe([{"File Path": k, "SHA-256 Hash": v} for k, v in baseline_data.items()], use_container_width=True)
            
        except Exception:
             st.error("CRITICAL: Baseline file tampered with or key mismatch! System compromised.")
    else:
        st.warning("No baseline.enc or hidden master key found. Is the FIM engine running?")

with col2:
    st.subheader("🚨 Active Alerts (Unacknowledged)")
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            logs = f.readlines()
            if logs:
                for log in reversed(logs):
                    if log.strip(): st.error(log.strip())
            else:
                st.info("✅ Clean Environment. No active threats detected.")
    else:
        st.info("✅ Clean Environment. Log file standing by.")

# --- Historical Logs Section ---
st.divider()
st.subheader("📂 Alert History (Archived)")

if os.path.exists(ARCHIVE_FILE):
    with open(ARCHIVE_FILE, 'r') as f:
        archived_logs = f.readlines()
        if archived_logs:
            with st.expander(f"View {len(archived_logs)} Past Alerts"):
                for log in reversed(archived_logs[-50:]): 
                    if log.strip(): st.text(log.strip())
        else:
            st.write("No archived alerts yet.")
else:
    st.write("No archived alerts yet.")

# --- Auto Refresh Execution ---
if auto_refresh:
    time.sleep(2)
    st.rerun()