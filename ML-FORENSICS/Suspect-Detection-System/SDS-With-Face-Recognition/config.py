"""
Suspect Detection System - Configuration
Forensic-grade configuration with security defaults
"""

import os
from datetime import datetime

# ==================== SYSTEM IDENTITY ====================
SYSTEM_NAME = "Forensic Suspect Detection System (SDS)"
VERSION = "1.0.0-MVP"
DEPLOYMENT_ID = f"SDS-{datetime.now().strftime('%Y%m%d')}"

# ==================== SECURITY SETTINGS ====================
# CRITICAL: Human-in-the-loop mandatory
REQUIRE_HUMAN_VERIFICATION = True
AUTO_ALERT_ENABLED = False  # Never auto-alert publicly

# Alert authority levels
AUTHORIZED_AGENCIES = [
    "CONTROL_ROOM",
    "SECURITY_OFFICER", 
    "FORENSIC_INVESTIGATOR",
    "LAW_ENFORCEMENT"
]

# ==================== DETECTION PARAMETERS ====================
# Confidence thresholds (probabilistic, not binary)
MATCH_CONFIDENCE_THRESHOLD = 0.55  # Primary threshold
HIGH_CONFIDENCE_THRESHOLD = 0.70   # High-priority alerts
MEDIUM_CONFIDENCE_THRESHOLD = 0.55 # Standard alerts
LOW_CONFIDENCE_THRESHOLD = 0.45    # Review-only (no alert)

# Occlusion handling
OCCLUSION_DETECTION_ENABLED = True
OCCLUSION_MILD_THRESHOLD = 0.20    # 20% face occluded
OCCLUSION_MODERATE_THRESHOLD = 0.40 # 40% face occluded
OCCLUSION_SEVERE_THRESHOLD = 0.60   # 60% face occluded

# Dynamic threshold adjustment based on occlusion
ADJUST_THRESHOLD_FOR_OCCLUSION = True
OCCLUSION_CONFIDENCE_PENALTY = {
    "none": 0.0,
    "mild": 0.05,
    "moderate": 0.10,
    "severe": 0.15
}

# ==================== MODEL CONFIGURATION ====================
FACE_DETECTION_MODEL = "buffalo_l"  # InsightFace pretrained
EMBEDDING_DIMENSION = 512
MIN_FACE_SIZE = 30  # Minimum face size in pixels

# ==================== DATA PATHS ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
EVIDENCE_DIR = os.path.join(BASE_DIR, "evidence")

# Database files
WATCHLIST_CSV = os.path.join(DATA_DIR, "watchlist.csv")
EMBEDDINGS_FILE = os.path.join(DATA_DIR, "watchlist_embeddings.pkl")
CASE_DATABASE = os.path.join(DATA_DIR, "cases.csv")

# Logs
DETECTION_LOG = os.path.join(LOGS_DIR, "detections.log")
ALERT_LOG = os.path.join(LOGS_DIR, "alerts.log")
SYSTEM_LOG = os.path.join(LOGS_DIR, "system.log")
AUDIT_LOG = os.path.join(LOGS_DIR, "audit.log")

# Evidence storage
ALERT_FRAMES_DIR = os.path.join(EVIDENCE_DIR, "alert_frames")
SUSPECT_TRACES_DIR = os.path.join(EVIDENCE_DIR, "suspect_traces")

# ==================== CAMERA SETTINGS ====================
MAX_CAMERAS = 1  # Maximum simultaneous camera feeds
DEFAULT_CAMERA_FPS = 10  # Process 10 frames per second
CAMERA_RECONNECT_ATTEMPTS = 3
CAMERA_RECONNECT_DELAY = 5  # seconds

# ==================== ALERT SYSTEM ====================
# Internal alerts only - NO public notifications
ALERT_CHANNELS = ["GUI", "LOG"]  # NO SMS, NO PUBLIC

# Alert cooldown to prevent spam
ALERT_COOLDOWN_SECONDS = 300  # 5 minutes between alerts for same person

# ==================== FORENSIC LOGGING ====================
# Append-only logging with cryptographic integrity
ENABLE_FRAME_HASHING = True
HASH_ALGORITHM = "sha256"
LOG_ROTATION_SIZE_MB = 100
MAX_LOG_FILES = 50

# Evidence retention
EVIDENCE_RETENTION_DAYS = 365  # 1 year minimum for legal requirements

# ==================== POST-INCIDENT TRACING ====================
# Backtracking system for suspect movement analysis
ENABLE_POST_INCIDENT_MODE = True
TRACE_HISTORY_HOURS = 72  # Look back 72 hours maximum
TRACE_CONFIDENCE_THRESHOLD = 0.50  # Lower threshold for historical review

# ==================== UI CONFIGURATION ====================
UI_THEME = "dark"  # SOC-style dark theme
UI_UPDATE_INTERVAL_MS = 100  # GUI refresh rate
MAX_DISPLAYED_ALERTS = 100
ENABLE_LIVE_FEED_PREVIEW = True

# ==================== ETHICAL SAFEGUARDS ====================
# CRITICAL: Privacy and rights protection
BLUR_NON_MATCHES = True  # Blur faces that don't match watchlist
ANONYMIZE_LOGS_AFTER_DAYS = 90  # Remove PII after investigation period
REQUIRE_CASE_NUMBER = True  # Every detection needs case context

# Legal compliance
GDPR_COMPLIANT_MODE = True
DATA_RETENTION_POLICY = "STRICT"
REQUIRE_LEGAL_JUSTIFICATION = True

# ==================== PERFORMANCE ====================
BATCH_PROCESSING_SIZE = 4  # Process 4 frames simultaneously
GPU_ENABLED = True
GPU_DEVICE_ID = 0

# ==================== LIMITS & SAFEGUARDS ====================
MAX_DETECTIONS_PER_HOUR = 1000  # Safety limit to prevent system abuse
MAX_ALERTS_PER_HOUR = 50  # Alert rate limiting
REQUIRE_SUPERVISOR_APPROVAL = True  # For high-risk level matches

# ==================== RISK LEVELS ====================
RISK_LEVELS = {
    "CRITICAL": {"color": "#DC2626", "priority": 1, "require_immediate_response": True},
    "HIGH": {"color": "#EA580C", "priority": 2, "require_immediate_response": True},
    "MEDIUM": {"color": "#F59E0B", "priority": 3, "require_immediate_response": False},
    "LOW": {"color": "#84CC16", "priority": 4, "require_immediate_response": False},
    "REVIEW": {"color": "#6B7280", "priority": 5, "require_immediate_response": False}
}

# ==================== LEGAL STATUS TYPES ====================
LEGAL_STATUS_TYPES = [
    "WANTED",           # Arrest warrant issued
    "POI",              # Person of Interest - investigation only
    "MISSING",          # Missing person case
    "WITNESS",          # Material witness
    "UNDER_INVESTIGATION"  # Active investigation
]

# ==================== HELPER FUNCTIONS ====================
def ensure_directories():
    """Create all required directories if they don't exist."""
    for directory in [DATA_DIR, LOGS_DIR, EVIDENCE_DIR, ALERT_FRAMES_DIR, SUSPECT_TRACES_DIR]:
        os.makedirs(directory, exist_ok=True)

def get_risk_level_config(risk_level):
    """Get configuration for a specific risk level."""
    return RISK_LEVELS.get(risk_level.upper(), RISK_LEVELS["REVIEW"])

def is_authorized_agency(agency):
    """Check if an agency is authorized to access the system."""
    return agency in AUTHORIZED_AGENCIES

# Initialize directories on import
ensure_directories()