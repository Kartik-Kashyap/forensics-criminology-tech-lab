import streamlit as st
import hashlib
import json
import datetime
import pandas as pd
import plotly.express as px
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

# --- CONFIGURATION & CONSTANTS ---
st.set_page_config(page_title="Human-Centered Forensic System", layout="wide")

class UserRole(str, Enum):
    INVESTIGATOR = "Investigator"
    ANALYST = "Forensic Analyst"
    SUPERVISOR = "Supervisor"
    AUDITOR = "External Auditor"

# Mock Database of Users
USERS = {
    "j_doe": {"role": UserRole.INVESTIGATOR, "name": "John Doe (Inv)"},
    "s_smith": {"role": UserRole.ANALYST, "name": "Sarah Smith (Analyst)"},
    "m_boss": {"role": UserRole.SUPERVISOR, "name": "Mike Boss (Super)"},
}

# --- CORE FORENSIC LOGIC (The Research Contribution) ---

@dataclass
class CustodyBlock:
    index: int
    timestamp: str
    user: str
    role: str
    action: str
    evidence_id: str
    details: str
    previous_hash: str
    block_hash: str

    @staticmethod
    def calculate_hash(index, timestamp, user, role, action, evidence_id, details, previous_hash):
        payload = f"{index}{timestamp}{user}{role}{action}{evidence_id}{details}{previous_hash}"
        return hashlib.sha256(payload.encode()).hexdigest()

class ForensicSystem:
    def __init__(self):
        if 'chain' not in st.session_state:
            st.session_state.chain = []
        if 'evidence_db' not in st.session_state:
            st.session_state.evidence_db = {}
        
    def log_action(self, user_id: str, action: str, evidence_id: str, details: str):
        chain = st.session_state.chain
        prev_hash = chain[-1].block_hash if chain else "0" * 64
        index = len(chain)
        timestamp = datetime.datetime.now().isoformat()
        user_role = USERS[user_id]['role']
        
        # Human-Centered Check: Is this role allowed? (RBAC)
        if not self._check_permission(user_role, action):
            # Log the DENIAL as a risk indicator
            details = f"[DENIED ATTEMPT] {details}"
            # We log it anyway to track risky behavior
        
        block_hash = CustodyBlock.calculate_hash(
            index, timestamp, user_id, user_role, action, evidence_id, details, prev_hash
        )
        
        new_block = CustodyBlock(
            index, timestamp, user_id, user_role, action, evidence_id, details, prev_hash, block_hash
        )
        chain.append(new_block)

    def _check_permission(self, role: UserRole, action: str) -> bool:
        # Simple RBAC rules for demo
        if action == "DELETE": return False # Immutability rule
        if role == UserRole.INVESTIGATOR and action == "EXPORT": return False
        if role == UserRole.AUDITOR and action == "UPLOAD": return False
        return True

    def add_evidence(self, file_obj, user_id):
        file_bytes = file_obj.getvalue()
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        
        if file_hash in st.session_state.evidence_db:
            st.error("Duplicate evidence detected! This file is already in custody.")
            self.log_action(user_id, "UPLOAD_ATTEMPT", "N/A", f"Duplicate file attempt: {file_obj.name}")
            return False

        # Store Metadata (Immutable Original)
        evidence_record = {
            "id": file_hash[:8],
            "filename": file_obj.name,
            "size": len(file_bytes),
            "type": file_obj.type,
            "original_hash": file_hash,
            "status": "LOCKED",
            "uploaded_by": user_id
        }
        
        st.session_state.evidence_db[file_hash[:8]] = evidence_record
        self.log_action(user_id, "INGESTION", file_hash[:8], f"Original Ingestion: {file_obj.name}")
        return True

# --- BEHAVIORAL ANALYSIS (The Psychology Part) ---

def analyze_risk_indicators(df_logs):
    risks = []
    if df_logs.empty:
        return risks
    
    # RISK 1: Obsessive Access (Cognitive Bias Indicator)
    # Checking if one user accesses the same evidence > 3 times in short session
    access_counts = df_logs[df_logs['action'] == 'VIEW'].groupby(['user', 'evidence_id']).size()
    for (user, ev_id), count in access_counts.items():
        if count > 3:
            risks.append(f"⚠️ **Bias Risk**: User '{user}' viewed Evidence {ev_id} {count} times (Potential Tunnel Vision).")

    # RISK 2: Unauthorized Attempts
    denials = df_logs[df_logs['details'].str.contains("DENIED")]
    for _, row in denials.iterrows():
        risks.append(f"🚫 **Procedural Error**: {row['user']} attempted unauthorized '{row['action']}'.")

    # RISK 3: Rapid Export (Rushed Handling)
    # (Simplified logic for MVP)
    exports = df_logs[df_logs['action'] == 'EXPORT']
    for _, row in exports.iterrows():
        # Check time since ingestion... (omitted for brevity, but this is where it goes)
        pass

    return risks

# --- UI LAYOUT ---

def main():
    system = ForensicSystem()

    # Sidebar: Authentication
    st.sidebar.title("🔐 Secure Login")
    user_id = st.sidebar.selectbox("Select User Profile", list(USERS.keys()))
    current_user = USERS[user_id]
    st.sidebar.info(f"Logged in as: **{current_user['name']}**\nRole: {current_user['role']}")

    st.title("🛡️ Human-Centered Evidence Management")
    st.markdown("### *Research Prototype v1.0*")

    # Tabs for workflow
    tab1, tab2, tab3 = st.tabs(["📂 Evidence Ingestion", "⛓️ Chain of Custody", "🧠 Behavioral Analysis"])

    # TAB 1: EVIDENCE INGESTION
    with tab1:
        st.subheader("Secure Evidence Ingestion")
        st.write("Supported: Images, Video, Audio, Disk Images (.dd, .img), PDF")
        
        uploaded_file = st.file_uploader("Drop Evidence Here (Originals Only)", 
                                         type=['png', 'jpg', 'mp4', 'wav', 'pdf', 'txt', 'dd'])
        
        if uploaded_file:
            if st.button("Cryptographically Lock & Ingest"):
                success = system.add_evidence(uploaded_file, user_id)
                if success:
                    st.success(f"Evidence '{uploaded_file.name}' secured. Hash generated and locked.")

        st.divider()
        st.subheader("Current Locked Evidence")
        if st.session_state.evidence_db:
            df_ev = pd.DataFrame(st.session_state.evidence_db.values())
            st.dataframe(df_ev)
            
            # Action Buttons for Testing
            st.write("#### Perform Actions (For Log Generation)")
            col1, col2 = st.columns(2)
            sel_ev = st.selectbox("Select Evidence ID", list(st.session_state.evidence_db.keys()))
            
            with col1:
                if st.button("👁️ View Evidence"):
                    system.log_action(user_id, "VIEW", sel_ev, "Routine verification")
                    st.toast("Action Logged: View")
            with col2:
                if st.button("📤 Export Copy"):
                    system.log_action(user_id, "EXPORT", sel_ev, "Exporting working copy for analysis")
                    st.toast("Action Logged: Export")

    # TAB 2: CHAIN OF CUSTODY (The "Why" it works)
    with tab2:
        st.subheader("Immutable Hash-Chained Logs")
        st.markdown("This ledger uses **SHA-256 linking**. Modifying any past entry breaks the entire chain.")
        
        if st.session_state.chain:
            # Convert chain to DataFrame for display
            chain_data = [vars(block) for block in st.session_state.chain]
            df_chain = pd.DataFrame(chain_data)
            
            # Reorder columns for readability
            df_chain = df_chain[['timestamp', 'user', 'role', 'action', 'details', 'block_hash']]
            st.dataframe(df_chain, use_container_width=True)

            # Verification Widget
            st.markdown("#### 🕵️ Integrity Verify")
            last_hash = st.session_state.chain[-1].block_hash
            st.code(f"Current Chain Tip Hash: {last_hash}", language="text")
        else:
            st.info("Chain is empty. Upload evidence to begin.")

    # TAB 3: BEHAVIORAL ANALYSIS (The "Research" Gold)
    with tab3:
        st.subheader("Procedural Risk & Bias Indicators")
        st.markdown("""
        *This module analyzes logs for human error patterns, cognitive bias (tunnel vision), 
        and procedural anomalies.*
        """)
        
        if st.session_state.chain:
            df_logs = pd.DataFrame([vars(b) for b in st.session_state.chain])
            
            # 1. Timeline Visualization
            st.write("#### ⏳ Interaction Timeline")
            fig = px.scatter(df_logs, x="timestamp", y="user", color="action", 
                             title="Investigator Interaction Patterns", symbol="role")
            st.plotly_chart(fig, use_container_width=True)

            # 2. Risk Indicators
            st.write("#### ⚠️ Generated Advisory Alerts")
            risks = analyze_risk_indicators(df_logs)
            
            if risks:
                for risk in risks:
                    st.warning(risk)
            else:
                st.success("No significant procedural risks detected in current session.")
                
            # 3. LLM Explanation Stub
            st.divider()
            st.markdown("#### 🤖 Explainable Summary (Simulated)")
            st.info(f"**Generated Narrative:** User {user_id} ({USERS[user_id]['role']}) has been the primary handler. "
                    f"Activity shows consistent adherence to protocol, though frequency of 'VIEW' actions suggests "
                    f"high focus on specific evidence items.")

if __name__ == "__main__":
    main()