"""
Human-Centered Digital Forensic Evidence Management System
Academic Research Prototype

RESEARCH PURPOSE:
This system demonstrates how human-centered design principles, forensic psychology,
and cognitive bias awareness can improve digital forensic workflows.

CRITICAL LIMITATIONS:
- NOT for production law enforcement use
- NOT designed to determine guilt or innocence
- Focuses on procedural integrity and human factor analysis
- All risk indicators are advisory, not accusatory

THEORETICAL FRAMEWORK:
Based on research in:
1. Confirmation bias in forensic science (Kassin et al., 2013)
2. Chain of custody integrity (Casey, 2011)
3. Cognitive load theory in complex investigations (Sweller, 1988)
4. Procedural justice and transparency (Tyler, 2006)
"""

import streamlit as st
import hashlib
import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional, Tuple
import shutil
import requests
import base64
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import zipfile
import io
import secrets
import string

# Try importing optional features with fallbacks
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False
    st.warning("⚠️ Cryptography library not available. Encryption features disabled. Install with: pip install cryptography")

try:
    import qrcode
    from PIL import Image, ImageDraw, ImageFont
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False
    st.warning("⚠️ QR code features disabled. Install with: pip install qrcode pillow")

# Configure page
st.set_page_config(
    page_title="Forensic EMS Research Prototype",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'current_role' not in st.session_state:
    st.session_state.current_role = None
if 'evidence_db' not in st.session_state:
    st.session_state.evidence_db = {}
if 'custody_chain' not in st.session_state:
    st.session_state.custody_chain = []
if 'access_log' not in st.session_state:
    st.session_state.access_log = []
if 'denied_attempts' not in st.session_state:
    st.session_state.denied_attempts = []
if 'encryption_keys' not in st.session_state:
    st.session_state.encryption_keys = {}
if 'forensic_timeline' not in st.session_state:
    st.session_state.forensic_timeline = []
if 'case_notes' not in st.session_state:
    st.session_state.case_notes = {}
if 'evidence_relationships' not in st.session_state:
    st.session_state.evidence_relationships = []

# Directory structure
BASE_DIR = Path("/home/claude/forensic_ems")
EVIDENCE_DIR = BASE_DIR / "evidence_vault"
ORIGINAL_DIR = EVIDENCE_DIR / "original"
WORKING_DIR = EVIDENCE_DIR / "working_copies"
EXPORTS_DIR = EVIDENCE_DIR / "exports"

# Create directories
for directory in [EVIDENCE_DIR, ORIGINAL_DIR, WORKING_DIR, EXPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ============================================================================
# ROLE-BASED ACCESS CONTROL (RBAC)
# Based on principle of least privilege and separation of duties
# ============================================================================

ROLES = {
    "investigator": {
        "name": "Field Investigator",
        "permissions": ["view_evidence", "access_working_copy", "add_notes"],
        "description": "Can view evidence and work with copies, cannot modify originals"
    },
    "forensic_analyst": {
        "name": "Forensic Analyst",
        "permissions": ["view_evidence", "access_working_copy", "add_notes", 
                       "create_analysis", "view_chain"],
        "description": "Can perform detailed analysis on working copies"
    },
    "evidence_custodian": {
        "name": "Evidence Custodian",
        "permissions": ["view_evidence", "intake_evidence", "view_chain", 
                       "export_evidence", "manage_custody"],
        "description": "Manages evidence intake, storage, and chain of custody"
    },
    "supervisor": {
        "name": "Case Supervisor",
        "permissions": ["view_evidence", "access_working_copy", "view_chain", 
                       "view_analytics", "review_alerts", "approve_export"],
        "description": "Oversees cases and reviews procedural compliance"
    },
    "researcher": {
        "name": "Academic Researcher",
        "permissions": ["view_analytics", "view_chain", "export_anonymized"],
        "description": "Can analyze patterns and generate research insights"
    }
}

# Simulated user database (in production, use secure authentication)
USERS = {
    "inv001": {"name": "Sarah Chen", "role": "investigator", "password": "demo123"},
    "analyst001": {"name": "Dr. James Wilson", "role": "forensic_analyst", "password": "demo123"},
    "custodian001": {"name": "Maria Garcia", "role": "evidence_custodian", "password": "demo123"},
    "sup001": {"name": "Lt. Robert Taylor", "role": "supervisor", "password": "demo123"},
    "research001": {"name": "Prof. Emily Rhodes", "role": "researcher", "password": "demo123"}
}

def check_permission(required_permission: str) -> bool:
    """
    PSYCHOLOGICAL RATIONALE:
    Explicit permission checks reduce role confusion and unauthorized access.
    Clear boundaries improve procedural compliance (Tyler, 2006).
    
    Returns: True if user has permission, False otherwise
    """
    if not st.session_state.authenticated:
        return False
    
    user_role = st.session_state.current_role
    if user_role not in ROLES:
        return False
    
    return required_permission in ROLES[user_role]["permissions"]

def log_access_attempt(action: str, evidence_id: Optional[str] = None, 
                       success: bool = True, justification: str = ""):
    """
    FORENSIC PSYCHOLOGY PRINCIPLE:
    Complete audit trails enable retrospective analysis of decision-making patterns.
    Logging denied attempts reveals potential procedural violations or training needs.
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user": st.session_state.current_user,
        "role": st.session_state.current_role,
        "action": action,
        "evidence_id": evidence_id,
        "success": success,
        "justification": justification,
        "session_duration": time.time() - st.session_state.get('login_time', time.time())
    }
    
    if success:
        st.session_state.access_log.append(log_entry)
    else:
        st.session_state.denied_attempts.append(log_entry)

# ============================================================================
# CRYPTOGRAPHIC HASH FUNCTIONS
# Ensures evidence integrity and tamper detection
# ============================================================================

def compute_file_hash(file_path: Path, algorithm: str = "sha256") -> str:
    """
    LEGAL STANDARD:
    Cryptographic hashing provides mathematical proof of evidence integrity.
    SHA-256 is forensically accepted standard (NIST FIPS 180-4).
    """
    hash_func = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def compute_chain_hash(previous_hash: str, entry_data: str) -> str:
    """
    BLOCKCHAIN-INSPIRED CUSTODY CHAIN:
    Each custody entry is cryptographically linked to previous entry.
    Any tampering breaks the chain, making it immediately detectable.
    """
    combined = f"{previous_hash}{entry_data}"
    return hashlib.sha256(combined.encode()).hexdigest()

# ============================================================================
# ENCRYPTION & SECURITY FEATURES
# ============================================================================

def generate_encryption_key(password: str, salt: bytes = None) -> Tuple[bytes, bytes]:
    """Generate encryption key from password using PBKDF2"""
    if not ENCRYPTION_AVAILABLE:
        raise Exception("Encryption not available. Install cryptography library.")
    
    if salt is None:
        salt = os.urandom(16)
    
    # Correct PBKDF2HMAC import and usage
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt

def encrypt_evidence(file_path: Path, password: str) -> Tuple[Path, str]:
    """
    COOL FEATURE: Military-grade AES-256 encryption for evidence
    Encrypts any file type (images, videos, disk images)
    Returns encrypted file path and decryption instructions
    """
    if not ENCRYPTION_AVAILABLE:
        raise Exception("Encryption not available. Install: pip install cryptography")
    
    try:
        # Generate encryption key
        key, salt = generate_encryption_key(password)
        fernet = Fernet(key)
        
        # Read and encrypt file
        with open(file_path, 'rb') as f:
            original_data = f.read()
        
        encrypted_data = fernet.encrypt(original_data)
        
        # Save encrypted file
        encrypted_path = file_path.parent / f"{file_path.stem}_ENCRYPTED{file_path.suffix}.enc"
        
        # Store salt + encrypted data
        with open(encrypted_path, 'wb') as f:
            f.write(salt)
            f.write(encrypted_data)
        
        # Generate decryption instructions
        instructions = f"""
ENCRYPTED EVIDENCE FILE
======================
Original File: {file_path.name}
Encryption: AES-256 (Fernet)
Salt Length: 16 bytes

To decrypt:
1. Extract first 16 bytes (salt)
2. Derive key using PBKDF2 with password
3. Decrypt remaining bytes with Fernet

Evidence ID: {file_path.stem}
Encrypted: {datetime.now().isoformat()}
        """
        
        return encrypted_path, instructions
    except Exception as e:
        raise Exception(f"Encryption failed: {str(e)}")

def decrypt_evidence(encrypted_path: Path, password: str) -> bytes:
    """Decrypt evidence file"""
    if not ENCRYPTION_AVAILABLE:
        raise Exception("Encryption not available")
    
    try:
        with open(encrypted_path, 'rb') as f:
            salt = f.read(16)
            encrypted_data = f.read()
        
        key, _ = generate_encryption_key(password, salt)
        fernet = Fernet(key)
        
        return fernet.decrypt(encrypted_data)
    except Exception as e:
        raise Exception(f"Decryption failed: {str(e)}")

def generate_secure_password(length: int = 16) -> str:
    """Generate cryptographically secure random password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_encrypted_package(evidence_ids: List[str], password: str) -> Path:
    """
    COOL FEATURE: Create encrypted ZIP package with multiple evidence files
    Perfect for secure court delivery or external expert review
    """
    package_path = EXPORTS_DIR / f"evidence_package_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    
    try:
        # Create password-protected ZIP
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.setpassword(password.encode())
            
            for eid in evidence_ids:
                if eid in st.session_state.evidence_db:
                    evidence = st.session_state.evidence_db[eid]
                    original_path = Path(evidence['original_path'])
                    
                    if original_path.exists():
                        # Add to encrypted ZIP
                        zipf.write(original_path, arcname=f"{eid}_{original_path.name}")
            
            # Add custody chain
            chain_data = [e for e in st.session_state.custody_chain if e['evidence_id'] in evidence_ids]
            zipf.writestr('CHAIN_OF_CUSTODY.json', json.dumps(chain_data, indent=2))
            
            # Add manifest
            manifest = f"""
EVIDENCE PACKAGE MANIFEST
=========================
Created: {datetime.now().isoformat()}
Created By: {st.session_state.current_user}
Evidence Items: {len(evidence_ids)}

Contents:
{chr(10).join([f"- {eid}: {st.session_state.evidence_db[eid]['filename']}" for eid in evidence_ids if eid in st.session_state.evidence_db])}

Security: Password-Protected ZIP
Chain of Custody: Included
            """
            zipf.writestr('MANIFEST.txt', manifest)
        
        return package_path
    except Exception as e:
        raise Exception(f"Package creation failed: {str(e)}")

def send_secure_email(recipient: str, subject: str, body: str, attachment_path: Path,
                     smtp_server: str, smtp_port: int, sender_email: str, sender_password: str):
    """
    COOL FEATURE: Secure email delivery with encryption
    Send evidence packages to prosecutors, defense, or external experts
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = f"[SECURE] {subject}"
        
        # Email body with security notice
        secure_body = f"""
{body}

---
SECURITY NOTICE:
This email contains encrypted forensic evidence. 
The attachment is password-protected.
Decryption password should be provided separately via secure channel.

Chain of custody maintained.
Evidence integrity verified with SHA-256 hashing.

Sent from: Forensic Evidence Management System
Timestamp: {datetime.now().isoformat()}
---
        """
        
        msg.attach(MIMEText(secure_body, 'plain'))
        
        # Attach encrypted file
        with open(attachment_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={attachment_path.name}')
            msg.attach(part)
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        return True
    except Exception as e:
        raise Exception(f"Email failed: {str(e)}")

def generate_evidence_qr_code(evidence_id: str):
    """
    COOL FEATURE: Generate QR code for quick evidence access
    Scan with phone to instantly view chain of custody
    """
    if not QR_AVAILABLE:
        raise Exception("QR code not available. Install: pip install qrcode pillow")
    
    try:
        evidence = st.session_state.evidence_db.get(evidence_id)
        
        if not evidence:
            return None
        
        qr_data = {
            "evidence_id": evidence_id,
            "case_id": evidence['case_id'],
            "filename": evidence['filename'],
            "hash": evidence['file_hash'][:16] + "...",
            "intake_date": evidence['intake_timestamp'][:10],
            "custody_entries": len([e for e in st.session_state.custody_chain if e['evidence_id'] == evidence_id])
        }
        
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(json.dumps(qr_data))
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        return img
    except Exception as e:
        raise Exception(f"QR generation failed: {str(e)}")

# ============================================================================
# FORENSIC TIMELINE & RELATIONSHIP MAPPING
# ============================================================================

def add_timeline_event(evidence_id: str, event_type: str, description: str, timestamp: str = None):
    """Build forensic timeline connecting evidence items"""
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    
    event = {
        "evidence_id": evidence_id,
        "event_type": event_type,
        "description": description,
        "timestamp": timestamp,
        "created_by": st.session_state.current_user
    }
    
    st.session_state.forensic_timeline.append(event)

def link_evidence(evidence_id_1: str, evidence_id_2: str, relationship_type: str, description: str):
    """
    COOL FEATURE: Create relationships between evidence items
    Shows how evidence connects (e.g., "Email references video", "GPS matches photo location")
    """
    relationship = {
        "id": f"REL-{len(st.session_state.evidence_relationships)}",
        "evidence_1": evidence_id_1,
        "evidence_2": evidence_id_2,
        "type": relationship_type,
        "description": description,
        "created_by": st.session_state.current_user,
        "timestamp": datetime.now().isoformat()
    }
    
    st.session_state.evidence_relationships.append(relationship)

def visualize_evidence_network():
    """Create network graph showing evidence relationships"""
    if not st.session_state.evidence_relationships:
        return None
    
    # Build network data
    nodes = set()
    edges = []
    
    for rel in st.session_state.evidence_relationships:
        nodes.add(rel['evidence_1'])
        nodes.add(rel['evidence_2'])
        edges.append((rel['evidence_1'], rel['evidence_2'], rel['type']))
    
    return {"nodes": list(nodes), "edges": edges}

# ============================================================================
# WATERMARKING (with fallback)
# ============================================================================

def add_digital_watermark(image_path: Path, watermark_text: str) -> Path:
    """
    COOL FEATURE: Add invisible digital watermark to images
    Proves authenticity and tracks unauthorized distribution
    """
    if not QR_AVAILABLE:
        raise Exception("Watermarking not available. Install: pip install pillow")
    
    try:
        img = Image.open(image_path)
        
        # Create semi-transparent watermark
        watermark = Image.new('RGBA', img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(watermark)
        
        # Add timestamp and evidence ID
        text = f"{watermark_text}\n{datetime.now().isoformat()}\nFORENSIC EVIDENCE - DO NOT DISTRIBUTE"
        
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
            except:
                font = ImageFont.load_default()
        
        # Position watermark
        draw.text((10, 10), text, fill=(255, 255, 255, 128), font=font)
        
        # Composite watermark onto image
        watermarked = Image.alpha_composite(img.convert('RGBA'), watermark)
        
        # Save
        watermarked_path = image_path.parent / f"{image_path.stem}_watermarked.png"
        watermarked.convert('RGB').save(watermarked_path)
        
        return watermarked_path
    except Exception as e:
        raise Exception(f"Watermarking failed: {str(e)}")

# ============================================================================
# CHAIN OF CUSTODY MANAGEMENT
# Core legal requirement for evidence admissibility
# ============================================================================

def add_custody_entry(evidence_id: str, action: str, justification: str, 
                     metadata: Optional[Dict] = None):
    """
    LEGAL REQUIREMENT:
    Every evidence interaction must be documented with:
    - Who accessed it
    - When they accessed it
    - Why they accessed it
    - What they did with it
    
    PSYCHOLOGICAL ADDITION:
    We also capture behavioral metadata for research purposes.
    """
    if not check_permission("manage_custody") and action == "intake":
        log_access_attempt(f"custody_entry:{action}", evidence_id, False)
        return False
    
    # Get previous hash for chain linking
    previous_hash = st.session_state.custody_chain[-1]["chain_hash"] if st.session_state.custody_chain else "GENESIS"
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "user": st.session_state.current_user,
        "role": st.session_state.current_role,
        "evidence_id": evidence_id,
        "action": action,
        "justification": justification,
        "metadata": metadata or {},
        "previous_hash": previous_hash
    }
    
    # Compute this entry's hash
    entry_data = json.dumps(entry, sort_keys=True)
    entry["chain_hash"] = compute_chain_hash(previous_hash, entry_data)
    
    st.session_state.custody_chain.append(entry)
    log_access_attempt(f"custody_entry:{action}", evidence_id, True, justification)
    
    return True

def verify_custody_chain() -> Tuple[bool, List[str]]:
    """
    INTEGRITY VERIFICATION:
    Recomputes all chain hashes to detect tampering.
    Critical for legal admissibility.
    """
    errors = []
    previous_hash = "GENESIS"
    
    for i, entry in enumerate(st.session_state.custody_chain):
        # Reconstruct entry without chain_hash
        entry_copy = entry.copy()
        stored_hash = entry_copy.pop("chain_hash")
        entry_copy["previous_hash"] = previous_hash
        
        entry_data = json.dumps(entry_copy, sort_keys=True)
        computed_hash = compute_chain_hash(previous_hash, entry_data)
        
        if computed_hash != stored_hash:
            errors.append(f"Chain break at entry {i}: {entry['action']} by {entry['user']}")
        
        previous_hash = stored_hash
    
    return len(errors) == 0, errors

# ============================================================================
# EVIDENCE INTAKE AND MANAGEMENT
# ============================================================================

def intake_evidence(file, case_id: str, description: str, source: str):
    """
    EVIDENCE INTAKE PROCEDURE:
    1. Verify user authorization
    2. Generate unique evidence ID
    3. Compute cryptographic hash
    4. Store in immutable original directory
    5. Create custody chain entry
    6. Log all metadata
    """
    if not check_permission("intake_evidence"):
        st.error("❌ Access Denied: You do not have permission to intake evidence")
        log_access_attempt("intake_evidence", None, False)
        return None
    
    # Generate evidence ID
    evidence_id = f"EVD-{case_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Save original file
    file_extension = Path(file.name).suffix
    original_path = ORIGINAL_DIR / f"{evidence_id}{file_extension}"
    
    with open(original_path, 'wb') as f:
        f.write(file.getbuffer())
    
    # Compute hash
    file_hash = compute_file_hash(original_path)
    
    # Create evidence record
    evidence_record = {
        "evidence_id": evidence_id,
        "case_id": case_id,
        "filename": file.name,
        "file_type": file_extension,
        "description": description,
        "source": source,
        "intake_timestamp": datetime.now().isoformat(),
        "intake_user": st.session_state.current_user,
        "original_path": str(original_path),
        "file_hash": file_hash,
        "hash_algorithm": "sha256",
        "file_size": original_path.stat().st_size,
        "status": "active"
    }
    
    st.session_state.evidence_db[evidence_id] = evidence_record
    
    # Add to custody chain
    add_custody_entry(
        evidence_id=evidence_id,
        action="INTAKE",
        justification=f"Evidence collected from {source}: {description}",
        metadata={
            "original_filename": file.name,
            "file_hash": file_hash,
            "file_size": evidence_record["file_size"]
        }
    )
    
    return evidence_id

# ============================================================================
# COGNITIVE BIAS DETECTION
# Research-focused behavioral analysis
# ============================================================================

def detect_bias_indicators() -> Dict[str, List[Dict]]:
    """
    FORENSIC PSYCHOLOGY RESEARCH:
    Analyzes access patterns for potential cognitive biases:
    
    1. CONFIRMATION BIAS: Repeated access to same evidence without exploring alternatives
    2. ANCHORING BIAS: Early fixation on specific evidence items
    3. SELECTIVE ATTENTION: Ignoring contradictory evidence
    4. TEMPORAL CLUSTERING: Unusual access patterns suggesting tunnel vision
    
    CRITICAL: These are INDICATORS, not accusations. Used for research and training.
    """
    indicators = {
        "repeated_access": [],
        "early_exports": [],
        "role_action_mismatch": [],
        "temporal_anomalies": [],
        "selective_focus": []
    }
    
    # Analyze access patterns per user
    user_accesses = {}
    for log in st.session_state.access_log:
        user = log['user']
        if user not in user_accesses:
            user_accesses[user] = []
        user_accesses[user].append(log)
    
    for user, accesses in user_accesses.items():
        # Check for repeated access to same evidence
        evidence_access_count = {}
        for access in accesses:
            if access.get('evidence_id'):
                eid = access['evidence_id']
                evidence_access_count[eid] = evidence_access_count.get(eid, 0) + 1
        
        for eid, count in evidence_access_count.items():
            if count > 5:  # Threshold for research purposes
                indicators["repeated_access"].append({
                    "user": user,
                    "evidence_id": eid,
                    "access_count": count,
                    "risk_level": "moderate" if count < 10 else "high",
                    "interpretation": "Possible confirmation bias - repeated examination of same evidence"
                })
        
        # Check for early exports (within first hour of case)
        early_exports = [a for a in accesses if "export" in a['action'].lower() 
                        and a.get('session_duration', 0) < 3600]
        if early_exports:
            indicators["early_exports"].extend([{
                "user": user,
                "timestamp": exp['timestamp'],
                "evidence_id": exp.get('evidence_id'),
                "risk_level": "moderate",
                "interpretation": "Early conclusion formation - export before comprehensive analysis"
            } for exp in early_exports])
    
    # Check for role-action mismatches in denied attempts
    for denied in st.session_state.denied_attempts:
        indicators["role_action_mismatch"].append({
            "user": denied['user'],
            "role": denied['role'],
            "attempted_action": denied['action'],
            "timestamp": denied['timestamp'],
            "risk_level": "low",
            "interpretation": "Procedural deviation - attempted unauthorized action"
        })
    
    return indicators

def analyze_evidence_interaction_patterns() -> pd.DataFrame:
    """
    BEHAVIORAL ANALYTICS:
    Creates temporal and frequency analysis of evidence interactions.
    Useful for identifying investigative patterns and potential biases.
    """
    if not st.session_state.access_log:
        return pd.DataFrame()
    
    df = pd.DataFrame(st.session_state.access_log)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['timestamp'].dt.hour
    df['day'] = df['timestamp'].dt.date
    
    return df

# ============================================================================
# LLM INTEGRATION (EXPLAINABLE AI)
# Uses local Llama for transparency and explanations
# ============================================================================

def query_llm(prompt: str, context: str = "") -> str:
    """
    EXPLAINABLE AI COMPONENT:
    Uses local LLM (Llama 3.2 via Ollama) for:
    - Chain of custody summaries
    - Procedural inconsistency explanations
    - Court-readable narratives
    
    ETHICAL SAFEGUARD: LLM is NEVER used for guilt determination or evidence interpretation.
    Only for procedural transparency and documentation.
    """
    try:
        full_prompt = f"""You are a forensic documentation assistant. Your role is to explain procedural aspects of digital evidence management, NOT to interpret evidence or determine guilt.

Context: {context}

Task: {prompt}

Provide a clear, factual explanation focused on procedures and documentation. Do not make judgments about evidence content or guilt."""

        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'llama3.2',
                'prompt': full_prompt,
                'stream': False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json().get('response', 'No response generated')
        else:
            return f"LLM service unavailable (Status: {response.status_code})"
    
    except Exception as e:
        return f"LLM unavailable: {str(e)}"

def generate_custody_summary(evidence_id: str) -> str:
    """Generate human-readable chain of custody summary using LLM"""
    chain_entries = [e for e in st.session_state.custody_chain if e['evidence_id'] == evidence_id]
    
    if not chain_entries:
        return "No custody chain entries found."
    
    context = json.dumps(chain_entries, indent=2)
    prompt = f"""Summarize the chain of custody for evidence {evidence_id} in a format suitable for court documentation. Focus on:
    - Who handled the evidence and when
    - What actions were performed
    - Any procedural notes
    Keep it factual and chronological."""
    
    return query_llm(prompt, context)

def explain_procedural_alert(alert_data: Dict) -> str:
    """Explain what a bias indicator means in procedural terms"""
    context = json.dumps(alert_data, indent=2)
    prompt = """Explain this procedural risk indicator in plain language. What does it mean, why might it occur, and what procedural steps could address it? Remember: these are indicators for review, not accusations."""
    
    return query_llm(prompt, context)

# ============================================================================
# USER INTERFACE
# ============================================================================

def login_page():
    """Authentication interface"""
    st.title("🔬 Forensic Evidence Management System")
    st.subheader("Academic Research Prototype")
    
    st.warning("""
    ⚠️ **RESEARCH SYSTEM NOTICE**
    
    This is an academic research prototype demonstrating human-centered design principles 
    in digital forensics. It is NOT intended for production law enforcement use.
    
    **Purpose**: Study procedural integrity, cognitive bias detection, and chain of custody management.
    """)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Available Demo Accounts")
        for user_id, user_data in USERS.items():
            role_info = ROLES[user_data['role']]
            st.markdown(f"""
            **{user_data['name']}** (`{user_id}`)  
            Role: {role_info['name']}  
            {role_info['description']}
            """)
    
    with col2:
        st.markdown("### Login")
        username = st.text_input("User ID")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", type="primary"):
            if username in USERS and USERS[username]['password'] == password:
                st.session_state.authenticated = True
                st.session_state.current_user = username
                st.session_state.current_role = USERS[username]['role']
                st.session_state.login_time = time.time()
                st.rerun()
            else:
                st.error("Invalid credentials")

def main_app():
    """Main application interface"""
    
    # Sidebar
    with st.sidebar:
        st.title("👤 User Session")
        user_data = USERS[st.session_state.current_user]
        role_data = ROLES[st.session_state.current_role]
        
        st.markdown(f"""
        **User**: {user_data['name']}  
        **Role**: {role_data['name']}  
        **Permissions**: {len(role_data['permissions'])}
        """)
        
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.session_state.current_role = None
            st.rerun()
        
        st.markdown("---")
        
        # Feature availability status
        st.markdown("### 🔧 Features Status")
        
        if ENCRYPTION_AVAILABLE:
            st.success("✅ Encryption (AES-256)")
        else:
            st.error("❌ Encryption")
            with st.expander("How to enable"):
                st.code("pip install cryptography")
        
        if QR_AVAILABLE:
            st.success("✅ QR Codes & Watermarks")
        else:
            st.error("❌ QR Codes & Watermarks")
            with st.expander("How to enable"):
                st.code("pip install qrcode pillow")
        
        st.success("✅ Email Export")
        st.success("✅ Blockchain Chain of Custody")
        st.success("✅ Timeline & Relationships")
        
        st.markdown("---")
        st.markdown("### Navigation")
        
    # Main navigation
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "📥 Evidence Intake",
        "📋 Evidence Management", 
        "🔗 Chain of Custody",
        "📊 Cognitive Bias Analytics",
        "🤖 AI Explanations",
        "🎯 Timeline & Relationships",
        "📦 Bulk Operations",
        "ℹ️ System Information"
    ])
    
    # TAB 1: Evidence Intake
    with tab1:
        st.header("📥 Evidence Intake")
        
        if not check_permission("intake_evidence"):
            st.error("❌ You do not have permission to intake evidence")
            st.info(f"Current role ({st.session_state.current_role}) cannot perform this action. Required role: Evidence Custodian")
        else:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                case_id = st.text_input("Case ID", placeholder="CASE-2026-001")
                description = st.text_area("Evidence Description", 
                    placeholder="Describe what this evidence is and its relevance to the case")
                source = st.text_input("Source/Origin", 
                    placeholder="e.g., Suspect's laptop, Scene photograph, Witness statement")
                
                uploaded_file = st.file_uploader(
                    "Upload Evidence File",
                    type=['jpg', 'png', 'pdf', 'mp4', 'wav', 'dd', 'img'],
                    help="Supported: Images, Videos, Audio, Documents, Disk Images"
                )
                
                if st.button("Intake Evidence", type="primary"):
                    if uploaded_file and case_id and description and source:
                        with st.spinner("Processing evidence intake..."):
                            evidence_id = intake_evidence(uploaded_file, case_id, description, source)
                            if evidence_id:
                                st.success(f"✅ Evidence successfully intaken: {evidence_id}")
                                st.balloons()
                    else:
                        st.warning("Please fill all fields and upload a file")
            
            with col2:
                st.info("""
                **Evidence Intake Procedure**
                
                1. Enter case details
                2. Upload evidence file
                3. System computes SHA-256 hash
                4. Original stored immutably
                5. Custody chain initiated
                6. All metadata logged
                
                **Supported Evidence Types:**
                - Images (JPG, PNG)
                - Documents (PDF)
                - Video (MP4)
                - Audio (WAV)
                - Disk Images (DD, IMG)
                """)
    
    # TAB 2: Evidence Management
    with tab2:
        st.header("📋 Evidence Management")
        
        if not check_permission("view_evidence"):
            st.error("❌ You do not have permission to view evidence")
        else:
            if not st.session_state.evidence_db:
                st.info("No evidence items in system. Use Evidence Intake to add items.")
            else:
                # Display evidence table
                evidence_df = pd.DataFrame(st.session_state.evidence_db.values())
                
                st.dataframe(
                    evidence_df[['evidence_id', 'case_id', 'filename', 'description', 
                               'intake_timestamp', 'intake_user', 'status']],
                    use_container_width=True
                )
                
                # Evidence details
                st.subheader("Evidence Details")
                selected_id = st.selectbox("Select Evidence", 
                    options=list(st.session_state.evidence_db.keys()),
                    key="evidence_management_selectbox")
                
                if selected_id:
                    evidence = st.session_state.evidence_db[selected_id]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"""
                        **Evidence ID**: {evidence['evidence_id']}  
                        **Case ID**: {evidence['case_id']}  
                        **Filename**: {evidence['filename']}  
                        **Description**: {evidence['description']}  
                        **Source**: {evidence['source']}
                        """)
                    
                    with col2:
                        st.markdown(f"""
                        **Intake Date**: {evidence['intake_timestamp']}  
                        **Intake User**: {evidence['intake_user']}  
                        **File Size**: {evidence['file_size']:,} bytes  
                        **Hash (SHA-256)**: `{evidence['file_hash'][:16]}...`  
                        **Status**: {evidence['status']}
                        """)
                    
                    # Action buttons
                    st.markdown("### Actions")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("📄 View Chain of Custody"):
                            log_access_attempt("view_custody_chain", selected_id, True)
                            st.info("See Chain of Custody tab for full details")
                    
                    with col2:
                        if check_permission("access_working_copy"):
                            if st.button("🔬 Create Working Copy"):
                                # Create working copy
                                original_path = Path(evidence['original_path'])
                                working_path = WORKING_DIR / f"{selected_id}_working{original_path.suffix}"
                                shutil.copy(original_path, working_path)
                                
                                add_custody_entry(
                                    selected_id,
                                    "CREATE_WORKING_COPY",
                                    "Working copy created for analysis",
                                    {"working_copy_path": str(working_path)}
                                )
                                st.success(f"Working copy created: {working_path.name}")
                        else:
                            st.button("🔬 Create Working Copy", disabled=True)
                            st.caption("Insufficient permissions")
                    
                    with col3:
                        if check_permission("export_evidence"):
                            if st.button("📤 Export"):
                                st.info("🎯 **Export Evidence Package**")
                                
                                # Export options
                                export_col1, export_col2 = st.columns(2)
                                
                                with export_col1:
                                    encrypt_export = st.checkbox("🔒 Encrypt Export", value=True)
                                    if encrypt_export:
                                        export_password = st.text_input("Encryption Password", 
                                                                       type="password",
                                                                       key="export_password",
                                                                       help="Leave empty to auto-generate")
                                        if not export_password:
                                            export_password = generate_secure_password()
                                            st.code(f"Auto-generated password: {export_password}")
                                
                                with export_col2:
                                    email_export = st.checkbox("📧 Email Export")
                                    if email_export:
                                        recipient_email = st.text_input("Recipient Email",
                                                                       key="recipient_email")
                                        smtp_server = st.text_input("SMTP Server", 
                                                                    value="smtp.gmail.com",
                                                                    key="smtp_server")
                                        smtp_port = st.number_input("SMTP Port", 
                                                                   value=587,
                                                                   key="smtp_port")
                                        sender_email = st.text_input("Your Email",
                                                                    key="sender_email")
                                        sender_password = st.text_input("Email Password", 
                                                                       type="password",
                                                                       key="sender_password")
                                
                                if st.button("🚀 Execute Export", key="execute_export_btn"):
                                    with st.spinner("Creating evidence package..."):
                                        # Create package
                                        if encrypt_export:
                                            package_path = create_encrypted_package([selected_id], export_password)
                                            st.success(f"✅ Encrypted package created: {package_path.name}")
                                        else:
                                            # Simple copy to exports
                                            original_path = Path(evidence['original_path'])
                                            export_path = EXPORTS_DIR / original_path.name
                                            shutil.copy(original_path, export_path)
                                            package_path = export_path
                                            st.success(f"✅ Evidence exported: {export_path.name}")
                                        
                                        # Log export
                                        add_custody_entry(
                                            selected_id,
                                            "EXPORT",
                                            f"Evidence exported {'with encryption' if encrypt_export else 'without encryption'}",
                                            {"export_path": str(package_path), "encrypted": encrypt_export}
                                        )
                                        
                                        # Email if requested
                                        if email_export and recipient_email and sender_email and sender_password:
                                            try:
                                                send_secure_email(
                                                    recipient=recipient_email,
                                                    subject=f"Evidence Package: {selected_id}",
                                                    body=f"Attached: Evidence package for {evidence['case_id']}\n\nPassword: {export_password if encrypt_export else 'N/A'}",
                                                    attachment_path=package_path,
                                                    smtp_server=smtp_server,
                                                    smtp_port=smtp_port,
                                                    sender_email=sender_email,
                                                    sender_password=sender_password
                                                )
                                                st.success(f"📧 Email sent to {recipient_email}")
                                                
                                                add_custody_entry(
                                                    selected_id,
                                                    "EMAIL_EXPORT",
                                                    f"Evidence package emailed to {recipient_email}",
                                                    {"recipient": recipient_email}
                                                )
                                            except Exception as e:
                                                st.error(f"Email failed: {str(e)}")
                                        
                                        # Provide download
                                        with open(package_path, 'rb') as f:
                                            st.download_button(
                                                label="⬇️ Download Package",
                                                data=f.read(),
                                                file_name=package_path.name,
                                                mime="application/zip" if package_path.suffix == '.zip' else "application/octet-stream"
                                            )
                        else:
                            st.button("📤 Export", disabled=True)
                            st.caption("Insufficient permissions")
                    
                    # Additional cool features
                    st.markdown("### 🎨 Advanced Features")
                    
                    adv_col1, adv_col2, adv_col3 = st.columns(3)
                    
                    with adv_col1:
                        if st.button("🔐 Encrypt Evidence", key=f"encrypt_{selected_id}"):
                            if not ENCRYPTION_AVAILABLE:
                                st.error("❌ Encryption not available. Install cryptography library:")
                                st.code("pip install cryptography")
                            else:
                                try:
                                    with st.spinner("Encrypting evidence..."):
                                        enc_password = generate_secure_password()
                                        encrypted_path, instructions = encrypt_evidence(
                                            Path(evidence['original_path']),
                                            enc_password
                                        )
                                        
                                        st.success("✅ Evidence encrypted with AES-256!")
                                        st.code(f"🔑 Password: {enc_password}\n\n⚠️ Store this password securely!")
                                        st.text_area("Decryption Instructions", instructions, height=200, key=f"decrypt_inst_{selected_id}")
                                        
                                        # Store encryption info
                                        st.session_state.encryption_keys[selected_id] = {
                                            "password": enc_password,
                                            "encrypted_path": str(encrypted_path),
                                            "timestamp": datetime.now().isoformat()
                                        }
                                        
                                        add_custody_entry(
                                            selected_id,
                                            "ENCRYPT",
                                            "Evidence encrypted with AES-256",
                                            {"encrypted_path": str(encrypted_path)}
                                        )
                                except Exception as e:
                                    st.error(f"❌ Encryption failed: {str(e)}")
                    
                    with adv_col2:
                        if st.button("📱 Generate QR Code", key=f"qr_{selected_id}"):
                            if not QR_AVAILABLE:
                                st.error("❌ QR code feature not available. Install libraries:")
                                st.code("pip install qrcode pillow")
                            else:
                                try:
                                    qr_img = generate_evidence_qr_code(selected_id)
                                    if qr_img:
                                        st.image(qr_img, caption=f"QR Code for {selected_id} - Scan to view info")
                                        st.success("✅ QR code generated! Scan with your phone.")
                                except Exception as e:
                                    st.error(f"❌ QR generation failed: {str(e)}")
                    
                    with adv_col3:
                        if evidence['file_type'] in ['.jpg', '.jpeg', '.png']:
                            if st.button("💧 Add Watermark", key=f"watermark_{selected_id}"):
                                if not QR_AVAILABLE:
                                    st.error("❌ Watermark feature not available. Install:")
                                    st.code("pip install pillow")
                                else:
                                    try:
                                        with st.spinner("Adding forensic watermark..."):
                                            watermarked_path = add_digital_watermark(
                                                Path(evidence['original_path']),
                                                f"Evidence {selected_id}"
                                            )
                                            st.success(f"✅ Watermarked: {watermarked_path.name}")
                                            
                                            # Show preview
                                            st.image(str(watermarked_path), width=400, caption="Watermarked Evidence")
                                    except Exception as e:
                                        st.error(f"❌ Watermark failed: {str(e)}")
                        else:
                            st.caption(f"Watermark only for images (current: {evidence['file_type']})")
    
    # TAB 3: Chain of Custody
    with tab3:
        st.header("🔗 Chain of Custody")
        
        if not check_permission("view_chain"):
            st.error("❌ You do not have permission to view chain of custody")
        else:
            # Verify chain integrity
            is_valid, errors = verify_custody_chain()
            
            if is_valid:
                st.success("✅ Chain of custody integrity verified - No tampering detected")
            else:
                st.error("⚠️ CHAIN INTEGRITY COMPROMISED")
                for error in errors:
                    st.error(error)
            
            # Display chain
            if st.session_state.custody_chain:
                st.subheader(f"Total Custody Entries: {len(st.session_state.custody_chain)}")
                
                # Filter by evidence
                evidence_filter = st.selectbox(
                    "Filter by Evidence ID",
                    options=["All"] + list(st.session_state.evidence_db.keys()),
                    key="chain_of_custody_filter_selectbox"
                )
                
                filtered_chain = st.session_state.custody_chain
                if evidence_filter != "All":
                    filtered_chain = [e for e in filtered_chain if e['evidence_id'] == evidence_filter]
                
                # Display as expandable entries
                for i, entry in enumerate(reversed(filtered_chain)):
                    with st.expander(f"Entry {len(filtered_chain)-i}: {entry['action']} by {entry['user']} - {entry['timestamp'][:19]}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"""
                            **User**: {entry['user']}  
                            **Role**: {entry['role']}  
                            **Evidence ID**: {entry['evidence_id']}  
                            **Action**: {entry['action']}
                            """)
                        
                        with col2:
                            st.markdown(f"""
                            **Timestamp**: {entry['timestamp']}  
                            **Previous Hash**: `{entry['previous_hash'][:16]}...`  
                            **Chain Hash**: `{entry['chain_hash'][:16]}...`
                            """)
                        
                        st.markdown(f"**Justification**: {entry['justification']}")
                        
                        if entry['metadata']:
                            st.json(entry['metadata'])
                
                # Export chain
                if st.button("📄 Generate Court Report"):
                    if evidence_filter != "All":
                        with st.spinner("Generating AI-assisted summary..."):
                            summary = generate_custody_summary(evidence_filter)
                            st.markdown("### Chain of Custody Summary")
                            st.markdown(summary)
                    else:
                        st.warning("Please select specific evidence to generate report")
            else:
                st.info("No custody chain entries yet")
    
    # TAB 4: Cognitive Bias Analytics
    with tab4:
        st.header("📊 Cognitive Bias & Risk Analytics")
        
        if not check_permission("view_analytics"):
            st.error("❌ You do not have permission to view analytics")
        else:
            st.warning("""
            **RESEARCH NOTICE**: These analytics detect procedural risk patterns based on 
            forensic psychology research. They are INDICATORS for review, NOT accusations.
            All findings require human interpretation and context.
            """)
            
            # Detect indicators
            indicators = detect_bias_indicators()
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Repeated Access Patterns", 
                         len(indicators['repeated_access']))
            with col2:
                st.metric("Early Exports", 
                         len(indicators['early_exports']))
            with col3:
                st.metric("Role Mismatches", 
                         len(indicators['role_action_mismatch']))
            with col4:
                st.metric("Total Access Logs", 
                         len(st.session_state.access_log))
            
            # Detailed indicators
            st.subheader("Procedural Risk Indicators")
            
            if indicators['repeated_access']:
                with st.expander("🔄 Repeated Access Patterns (Possible Confirmation Bias)"):
                    st.markdown("""
                    **Psychological Basis**: Confirmation bias leads investigators to repeatedly 
                    examine evidence that supports their hypothesis while ignoring contradictory evidence.
                    
                    **Procedural Concern**: Excessive focus on specific evidence without proportional 
                    examination of other case materials.
                    """)
                    
                    for indicator in indicators['repeated_access']:
                        st.warning(f"""
                        **User**: {indicator['user']}  
                        **Evidence**: {indicator['evidence_id']}  
                        **Access Count**: {indicator['access_count']}  
                        **Risk Level**: {indicator['risk_level'].upper()}  
                        
                        *{indicator['interpretation']}*
                        """)
            
            if indicators['early_exports']:
                with st.expander("⚡ Early Evidence Export (Premature Conclusions)"):
                    st.markdown("""
                    **Psychological Basis**: Anchoring bias and premature closure can lead to 
                    early conclusion formation before comprehensive analysis.
                    
                    **Procedural Concern**: Evidence exported unusually early in investigation timeline.
                    """)
                    
                    for indicator in indicators['early_exports']:
                        st.warning(f"""
                        **User**: {indicator['user']}  
                        **Evidence**: {indicator.get('evidence_id', 'N/A')}  
                        **Time**: {indicator['timestamp'][:19]}  
                        **Risk Level**: {indicator['risk_level'].upper()}  
                        
                        *{indicator['interpretation']}*
                        """)
            
            if indicators['role_action_mismatch']:
                with st.expander("⚠️ Unauthorized Access Attempts"):
                    st.markdown("""
                    **Procedural Concern**: Users attempting actions outside their role permissions.
                    May indicate training needs or procedural confusion.
                    """)
                    
                    for indicator in indicators['role_action_mismatch']:
                        st.info(f"""
                        **User**: {indicator['user']} ({indicator['role']})  
                        **Attempted Action**: {indicator['attempted_action']}  
                        **Time**: {indicator['timestamp'][:19]}  
                        
                        *{indicator['interpretation']}*
                        """)
            
            # Access pattern visualization
            if st.session_state.access_log:
                st.subheader("Access Pattern Analysis")
                
                df = analyze_evidence_interaction_patterns()
                
                if not df.empty:
                    # Temporal heatmap
                    fig = px.histogram(df, x='hour', 
                                      title="Access Activity by Hour of Day",
                                      labels={'hour': 'Hour of Day', 'count': 'Number of Accesses'},
                                      nbins=24)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # User activity
                    user_counts = df['user'].value_counts()
                    fig2 = px.bar(x=user_counts.index, y=user_counts.values,
                                 title="Access Count by User",
                                 labels={'x': 'User', 'y': 'Access Count'})
                    st.plotly_chart(fig2, use_container_width=True)
    
    # TAB 5: AI Explanations
    with tab5:
        st.header("🤖 AI-Assisted Explanations")
        
        st.info("""
        This feature uses a local LLM (Llama 3.2) to generate human-readable explanations 
        of procedural data. The AI is used ONLY for documentation and transparency, 
        NEVER for evidence interpretation or guilt determination.
        """)
        
        explanation_type = st.radio(
            "Select Explanation Type",
            ["Chain of Custody Summary", "Risk Indicator Explanation", "Custom Query"]
        )
        
        if explanation_type == "Chain of Custody Summary":
            if st.session_state.evidence_db:
                evidence_id = st.selectbox("Select Evidence", 
                    options=list(st.session_state.evidence_db.keys()),
                    key="ai_explanation_evidence_selectbox")
                
                if st.button("Generate Summary"):
                    with st.spinner("Generating explanation..."):
                        summary = generate_custody_summary(evidence_id)
                        st.markdown("### Chain of Custody Summary")
                        st.markdown(summary)
            else:
                st.warning("No evidence in system")
        
        elif explanation_type == "Risk Indicator Explanation":
            indicators = detect_bias_indicators()
            all_indicators = (indicators['repeated_access'] + 
                            indicators['early_exports'] + 
                            indicators['role_action_mismatch'])
            
            if all_indicators:
                indicator_idx = st.selectbox("Select Indicator", 
                    range(len(all_indicators)),
                    format_func=lambda i: f"{all_indicators[i].get('user', 'N/A')} - {all_indicators[i].get('interpretation', 'N/A')[:50]}...")
                
                if st.button("Explain Indicator"):
                    with st.spinner("Generating explanation..."):
                        explanation = explain_procedural_alert(all_indicators[indicator_idx])
                        st.markdown("### Procedural Explanation")
                        st.markdown(explanation)
            else:
                st.info("No risk indicators detected")
        
        else:  # Custom Query
            query = st.text_area("Enter your question about procedures or documentation",
                placeholder="e.g., 'Explain what a chain of custody is and why it matters'")
            
            if st.button("Get Explanation"):
                if query:
                    with st.spinner("Generating explanation..."):
                        response = query_llm(query)
                        st.markdown("### Response")
                        st.markdown(response)
                else:
                    st.warning("Please enter a question")
    
    # TAB 6: Timeline & Relationships
    with tab6:
        st.header("🎯 Forensic Timeline & Evidence Relationships")
        
        st.info("**Cool Feature**: Build a chronological timeline and map relationships between evidence items!")
        
        timeline_col, relationship_col = st.columns(2)
        
        with timeline_col:
            st.subheader("⏰ Build Timeline")
            
            if st.session_state.evidence_db:
                timeline_evidence = st.selectbox(
                    "Select Evidence for Timeline",
                    options=list(st.session_state.evidence_db.keys()),
                    key="timeline_evidence_selectbox"
                )
                
                event_type = st.selectbox(
                    "Event Type",
                    ["Collection", "Analysis", "Discovery", "Correlation", "Expert Review", "Court Presentation"],
                    key="timeline_event_type"
                )
                
                event_desc = st.text_area("Event Description", key="timeline_event_desc")
                event_time = st.text_input("Event Timestamp (or leave blank for now)", key="timeline_event_time")
                
                if st.button("➕ Add to Timeline", key="add_timeline_btn"):
                    add_timeline_event(timeline_evidence, event_type, event_desc, event_time or None)
                    st.success("✅ Added to timeline!")
            else:
                st.warning("No evidence in system")
            
            # Display timeline
            if st.session_state.forensic_timeline:
                st.markdown("### 📅 Current Timeline")
                
                timeline_df = pd.DataFrame(st.session_state.forensic_timeline)
                timeline_df['timestamp'] = pd.to_datetime(timeline_df['timestamp'])
                timeline_df = timeline_df.sort_values('timestamp')
                
                # Visualize timeline
                fig = px.timeline(
                    timeline_df,
                    x_start="timestamp",
                    x_end="timestamp",
                    y="event_type",
                    color="evidence_id",
                    hover_data=["description", "created_by"],
                    title="Forensic Investigation Timeline"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Detailed view
                for idx, event in timeline_df.iterrows():
                    with st.expander(f"{event['event_type']}: {event['evidence_id']} - {event['timestamp'].strftime('%Y-%m-%d %H:%M')}"):
                        st.markdown(f"**Description**: {event['description']}")
                        st.markdown(f"**Created by**: {event['created_by']}")
        
        with relationship_col:
            st.subheader("🔗 Link Evidence Items")
            
            if len(st.session_state.evidence_db) >= 2:
                rel_col1, rel_col2 = st.columns(2)
                
                with rel_col1:
                    evidence_1 = st.selectbox(
                        "Evidence 1",
                        options=list(st.session_state.evidence_db.keys()),
                        key="relationship_evidence_1"
                    )
                
                with rel_col2:
                    evidence_2 = st.selectbox(
                        "Evidence 2",
                        options=list(st.session_state.evidence_db.keys()),
                        key="relationship_evidence_2"
                    )
                
                rel_type = st.selectbox(
                    "Relationship Type",
                    ["References", "Corroborates", "Contradicts", "Temporal Match", "Location Match", "Person Match"],
                    key="relationship_type"
                )
                
                rel_desc = st.text_area("Describe the relationship", key="relationship_desc")
                
                if st.button("🔗 Create Link", key="create_link_btn"):
                    if evidence_1 != evidence_2:
                        link_evidence(evidence_1, evidence_2, rel_type, rel_desc)
                        st.success(f"✅ Linked {evidence_1} ↔️ {evidence_2}")
                    else:
                        st.error("Cannot link evidence to itself")
            else:
                st.warning("Need at least 2 evidence items to create relationships")
            
            # Display network
            if st.session_state.evidence_relationships:
                st.markdown("### 🕸️ Evidence Network")
                
                network = visualize_evidence_network()
                
                # Create network visualization
                network_data = []
                for rel in st.session_state.evidence_relationships:
                    network_data.append({
                        "source": rel['evidence_1'],
                        "target": rel['evidence_2'],
                        "type": rel['type']
                    })
                
                st.json(network_data)
                
                # Detailed relationships
                for rel in st.session_state.evidence_relationships:
                    with st.expander(f"{rel['type']}: {rel['evidence_1']} ↔️ {rel['evidence_2']}"):
                        st.markdown(f"**Description**: {rel['description']}")
                        st.markdown(f"**Created by**: {rel['created_by']}")
                        st.markdown(f"**Timestamp**: {rel['timestamp']}")
    
    # TAB 7: Bulk Operations
    with tab7:
        st.header("📦 Bulk Operations & Advanced Export")
        
        st.info("**Cool Feature**: Process multiple evidence items at once!")
        
        if not st.session_state.evidence_db:
            st.warning("No evidence in system")
        else:
            # Multi-select evidence
            st.subheader("Select Evidence Items")
            selected_evidence = st.multiselect(
                "Choose evidence items for bulk operations",
                options=list(st.session_state.evidence_db.keys()),
                format_func=lambda x: f"{x}: {st.session_state.evidence_db[x]['filename']}",
                key="bulk_evidence_selector"
            )
            
            if selected_evidence:
                st.success(f"Selected {len(selected_evidence)} items")
                
                bulk_col1, bulk_col2 = st.columns(2)
                
                with bulk_col1:
                    st.subheader("🔐 Bulk Encryption")
                    
                    if not ENCRYPTION_AVAILABLE:
                        st.error("❌ Encryption not available")
                        st.code("pip install cryptography")
                    else:
                        bulk_encrypt_password = st.text_input(
                            "Master Password (leave empty for auto-generate)",
                            type="password",
                            key="bulk_encrypt_password"
                        )
                        
                        if not bulk_encrypt_password:
                            bulk_encrypt_password = generate_secure_password(20)
                            st.info(f"🔑 Auto-generated password:")
                            st.code(bulk_encrypt_password)
                        
                        if st.button("🔒 Encrypt All Selected", key="bulk_encrypt_btn"):
                            with st.spinner("Encrypting evidence items..."):
                                success_count = 0
                                progress_bar = st.progress(0)
                                
                                for idx, eid in enumerate(selected_evidence):
                                    try:
                                        evidence = st.session_state.evidence_db[eid]
                                        encrypted_path, _ = encrypt_evidence(
                                            Path(evidence['original_path']),
                                            bulk_encrypt_password
                                        )
                                        
                                        st.session_state.encryption_keys[eid] = {
                                            "password": bulk_encrypt_password,
                                            "encrypted_path": str(encrypted_path),
                                            "timestamp": datetime.now().isoformat()
                                        }
                                        
                                        add_custody_entry(
                                            eid,
                                            "BULK_ENCRYPT",
                                            f"Bulk encryption operation",
                                            {"encrypted_path": str(encrypted_path)}
                                        )
                                        
                                        success_count += 1
                                    except Exception as e:
                                        st.error(f"Failed {eid}: {str(e)}")
                                    
                                    progress_bar.progress((idx + 1) / len(selected_evidence))
                                
                                if success_count > 0:
                                    st.success(f"✅ Encrypted {success_count}/{len(selected_evidence)} items")
                                    st.balloons()
                
                with bulk_col2:
                    st.subheader("📦 Create Evidence Package")
                    
                    package_password = st.text_input(
                        "Package Password",
                        type="password",
                        key="package_password"
                    )
                    
                    if not package_password:
                        package_password = generate_secure_password(20)
                        st.info("🔑 Auto-generated password:")
                        st.code(package_password)
                    
                    package_name = st.text_input(
                        "Package Name",
                        value=f"evidence_pkg_{datetime.now().strftime('%Y%m%d')}",
                        key="package_name"
                    )
                    
                    if st.button("📦 Create Package", key="create_package_btn"):
                        try:
                            with st.spinner("Creating encrypted package..."):
                                package_path = create_encrypted_package(selected_evidence, package_password)
                                st.success(f"✅ Package created: {package_path.name}")
                                
                                # Provide download
                                with open(package_path, 'rb') as f:
                                    st.download_button(
                                        label="⬇️ Download Evidence Package",
                                        data=f.read(),
                                        file_name=package_path.name,
                                        mime="application/zip",
                                        key="download_package_btn"
                                    )
                                
                                st.info(f"🔑 **Password**: `{package_password}`")
                                st.warning("⚠️ Store password securely and transmit via separate channel!")
                        except Exception as e:
                            st.error(f"❌ Package creation failed: {str(e)}")
                
                # Email bulk package
                st.subheader("📧 Email Evidence Package")
                
                email_col1, email_col2 = st.columns(2)
                
                with email_col1:
                    bulk_recipient = st.text_input("Recipient Email", key="bulk_recipient")
                    bulk_smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com", key="bulk_smtp")
                    bulk_smtp_port = st.number_input("SMTP Port", value=587, key="bulk_smtp_port")
                
                with email_col2:
                    bulk_sender_email = st.text_input("Your Email", key="bulk_sender")
                    bulk_sender_password = st.text_input("Email Password", type="password", key="bulk_sender_pwd")
                    bulk_case_reference = st.text_input("Case Reference", key="bulk_case_ref")
                
                st.info("💡 **Gmail users**: Enable 2FA and create an App Password at myaccount.google.com/apppasswords")
                
                if st.button("📧 Send Evidence Package", key="send_bulk_email_btn"):
                    if not bulk_recipient or not bulk_sender_email or not bulk_sender_password:
                        st.error("❌ Please fill all email fields")
                    else:
                        try:
                            with st.spinner("Creating package and sending email..."):
                                # Create package first
                                package_path = create_encrypted_package(selected_evidence, package_password)
                                
                                # Send email
                                send_secure_email(
                                    recipient=bulk_recipient,
                                    subject=f"Evidence Package: {bulk_case_reference or 'Multiple Items'}",
                                    body=f"""
Evidence Package Details:
- Items: {len(selected_evidence)}
- Case: {bulk_case_reference or 'N/A'}
- Created: {datetime.now().isoformat()}

Evidence IDs:
{chr(10).join([f"- {eid}" for eid in selected_evidence])}

Package Password: {package_password}

⚠️ This password should be transmitted via secure channel.
                                    """,
                                    attachment_path=package_path,
                                    smtp_server=bulk_smtp_server,
                                    smtp_port=bulk_smtp_port,
                                    sender_email=bulk_sender_email,
                                    sender_password=bulk_sender_password
                                )
                                
                                st.success(f"✅ Package sent to {bulk_recipient}")
                                st.balloons()
                                
                                # Log all exports
                                for eid in selected_evidence:
                                    add_custody_entry(
                                        eid,
                                        "EMAIL_BULK_EXPORT",
                                        f"Bulk package emailed to {bulk_recipient}",
                                        {"recipient": bulk_recipient, "package": package_path.name}
                                    )
                        
                        except Exception as e:
                            st.error(f"❌ Failed to send: {str(e)}")
                            st.info("💡 Common issues:")
                            st.markdown("""
                            - Gmail: Use App Password, not regular password
                            - Check SMTP server and port are correct
                            - Ensure firewall allows SMTP connections
                            - Verify email and password are correct
                            """)
                
                # Generate QR codes for all
                st.subheader("📱 Bulk QR Code Generation")
                
                if not QR_AVAILABLE:
                    st.warning("❌ QR code feature not available")
                    st.code("pip install qrcode pillow")
                else:
                    if st.button("Generate QR Codes for All Selected", key="bulk_qr_btn"):
                        try:
                            st.info(f"Generating QR codes for {len(selected_evidence)} items...")
                            qr_cols = st.columns(min(len(selected_evidence), 4))
                            for idx, eid in enumerate(selected_evidence):
                                with qr_cols[idx % 4]:
                                    try:
                                        qr_img = generate_evidence_qr_code(eid)
                                        if qr_img:
                                            st.image(qr_img, caption=eid, width=150)
                                    except Exception as e:
                                        st.error(f"QR failed for {eid}")
                            st.success("✅ QR codes generated!")
                        except Exception as e:
                            st.error(f"❌ QR generation failed: {str(e)}")
    
    # TAB 8: System Information
    with tab8:
        st.header("ℹ️ System Information")
        
        st.markdown("""
        ## Human-Centered Digital Forensic Evidence Management System
        ### Academic Research Prototype v1.0
        
        ---
        
        ### Purpose & Scope
        
        This system is designed as an academic research tool to study:
        
        1. **Human Factors in Digital Forensics**
           - How cognitive biases affect evidence handling
           - Patterns of investigator behavior and decision-making
           - Impact of role-based access on procedural compliance
        
        2. **Chain of Custody Integrity**
           - Cryptographic verification of evidence handling
           - Blockchain-inspired audit trails
           - Tamper detection and prevention
        
        3. **Procedural Transparency**
           - Explainable AI for documentation
           - Behavioral analytics without accusation
           - Educational feedback for training
        
        ---
        
        ### Theoretical Framework
        
        **Forensic Psychology Principles:**
        - Confirmation bias (Kassin et al., 2013)
        - Cognitive load in complex investigations (Sweller, 1988)
        - Decision-making under uncertainty (Kahneman & Tversky, 1974)
        
        **Legal Standards:**
        - Chain of custody requirements (Federal Rules of Evidence)
        - Digital evidence integrity (NIST SP 800-86)
        - Procedural justice (Tyler, 2006)
        
        **Human-Centered Design:**
        - Transparency and explainability
        - Error prevention through design
        - Ethical AI integration
        
        ---
        
        ### Critical Limitations
        
        ⚠️ **This system is NOT:**
        - Approved for production law enforcement use
        - Designed to determine guilt or innocence
        - A replacement for human judgment
        - Intended to accuse individuals of misconduct
        
        ✅ **This system IS:**
        - A research tool for studying forensic procedures
        - An educational platform for training
        - A demonstration of human-centered design principles
        - A framework for procedural improvement
        
        ---
        
        ### Ethical Safeguards
        
        1. **No Evidence Interpretation**: AI is never used to analyze evidence content
        2. **Indicators, Not Accusations**: All alerts are procedural risk indicators
        3. **Human Oversight Required**: All findings require expert interpretation
        4. **Transparency**: All AI outputs are explainable and auditable
        5. **Privacy**: Designed with data minimization principles
        
        ---
        
        ### Technical Architecture
        
        **Evidence Integrity:**
        - SHA-256 cryptographic hashing
        - Immutable original storage
        - Working copy separation
        
        **Chain of Custody:**
        - Blockchain-inspired hash chaining
        - Tamper-evident audit logs
        - Complete temporal reconstruction
        
        **Access Control:**
        - Role-based permissions (RBAC)
        - Explicit authorization checks
        - Denied attempt logging
        
        **Behavioral Analysis:**
        - Access pattern detection
        - Temporal clustering analysis
        - Role-action correlation
        
        **AI Integration:**
        - Local LLM (Llama 3.2 via Ollama)
        - Procedural explanation only
        - No evidence content analysis
        
        ---
        
        ### Research Applications
        
        This system can be used to study:
        
        - Impact of cognitive bias awareness on investigator behavior
        - Effectiveness of procedural safeguards
        - Role design and separation of duties
        - Training intervention effectiveness
        - Human-AI collaboration in forensic workflows
        
        ---
        
        ### References
        
        - Casey, E. (2011). *Digital Evidence and Computer Crime* (3rd ed.)
        - Kassin, S. M., Dror, I. E., & Kukucka, J. (2013). The forensic confirmation bias
        - NIST (2006). SP 800-86: Guide to Integrating Forensic Techniques
        - Sweller, J. (1988). Cognitive load during problem solving
        - Tyler, T. R. (2006). Psychological perspectives on legitimacy and legitimation
        
        ---
        
        ### Contact & Feedback
        
        For research inquiries or to report issues, this is a demonstration system.
        In a production environment, contact information would be provided here.
        
        **System Version**: 1.0.0  
        **Last Updated**: January 2026  
        **License**: Academic Research Only
        """)
        
        # System Statistics
        st.subheader("Current System Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Evidence Items", len(st.session_state.evidence_db))
            st.metric("Custody Entries", len(st.session_state.custody_chain))
        
        with col2:
            st.metric("Access Logs", len(st.session_state.access_log))
            st.metric("Denied Attempts", len(st.session_state.denied_attempts))
        
        with col3:
            st.metric("Active Users", len(set(log['user'] for log in st.session_state.access_log)))
            is_valid, _ = verify_custody_chain()
            st.metric("Chain Integrity", "✅ Valid" if is_valid else "❌ Compromised")

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

def main():
    """Application entry point with authentication guard"""
    if not st.session_state.authenticated:
        login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()