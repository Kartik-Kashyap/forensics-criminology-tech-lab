# SYSTEM ARCHITECTURE

## Forensic Suspect Detection System - Technical Architecture

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    WEB INTERFACE (Flask)                     │
│                  SOC-Style Dashboard @ :5000                 │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Watchlist│  │Recognition│  │  Alert   │  │  Camera  │   │
│  │  Manager │  │  Engine   │  │  Manager │  │  Manager │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   DATA & MODELS LAYER                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Watchlist │  │Face Model│  │Embeddings│  │  Logs &  │   │
│  │   CSV    │  │InsightFace│  │Database  │  │ Evidence │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    HARDWARE LAYER                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Camera  │  │  Camera  │  │   GPU    │  │ Storage  │   │
│  │    1     │  │    2     │  │(Optional)│  │  System  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Modules

### 1. Watchlist Manager (`core/watchlist.py`)

**Responsibilities:**
- Manage suspect database (watchlist.csv)
- Add/remove persons with authorization
- Extract face embeddings from images
- Build and maintain embeddings database
- Audit trail for all operations

**Key Methods:**
```python
add_person(person_id, case_id, full_name, risk_level, legal_status, ...)
remove_person(person_id, removed_by, reason)
extract_embeddings_from_images(person_id, image_dir)
build_embeddings_database(images_base_dir)
load_embeddings()
```

**Data Schema:**
```
PersonID | CaseID | FullName | RiskLevel | LegalStatus | AuthorizedAgency | DateAdded | AddedBy | Notes | LastDetected
```

---

### 2. Recognition Engine (`core/recognition.py`)

**Responsibilities:**
- Face detection in frames
- Embedding extraction
- Occlusion level estimation
- Mask detection
- Face matching against watchlist
- Dynamic threshold adjustment

**Key Components:**

#### OcclusionDetector
```python
estimate_occlusion(face) → (level, percentage)
check_mask_presence(face, frame) → bool
```

#### FaceRecognitionEngine
```python
detect_faces(frame) → [faces]
recognize_face(embedding, occlusion_level) → {person_id, confidence, ...}
process_frame(frame, camera_id) → [detections]
```

**Recognition Pipeline:**
```
Frame Input
    ↓
Face Detection (InsightFace buffalo_l)
    ↓
Embedding Extraction (512-dim vector)
    ↓
Occlusion Estimation
    ↓
Cosine Similarity vs Watchlist
    ↓
Dynamic Threshold Adjustment
    ↓
Match Decision (with confidence)
```

---

### 3. Alert Manager (`core/alerts.py`)

**Responsibilities:**
- Generate forensic-grade alerts
- Manage alert cooldowns (prevent spam)
- Save evidence frames with hashing
- Internal-only alert distribution
- Post-incident video tracing

**Key Components:**

#### AlertManager
```python
should_alert(person_id) → bool  # Cooldown check
generate_alert(detection, frame, camera_id) → alert_object
get_recent_alerts(hours) → [alerts]
get_alert_statistics() → stats_dict
```

#### PostIncidentTracer
```python
trace_suspect_in_video(video_path, person_id) → [detections]
# Analyzes historical footage
# Generates timeline with confidence scores
```

**Alert Object Schema:**
```json
{
  "alert_id": "ALERT-000001",
  "timestamp": "ISO-8601",
  "person_id": "POI-2025-001",
  "full_name": "John Doe",
  "case_id": "CASE-2025-001",
  "legal_status": "WANTED",
  "risk_level": "HIGH",
  "camera_id": "CAM-01",
  "confidence": 0.78,
  "occlusion_level": "mild",
  "mask_detected": false,
  "evidence_frame": "filename.jpg",
  "frame_hash": "sha256...",
  "require_immediate_response": true
}
```

---

### 4. Camera Manager (`core/camera.py`)

**Responsibilities:**
- Multi-camera stream management
- Automatic reconnection on failure
- Thread-safe frame capture
- Camera health monitoring

**Key Components:**

#### CameraStream
```python
start() → None  # Start capture thread
stop() → None
get_frame() → frame
is_alive() → bool
```

#### CameraManager
```python
add_camera(camera_id, camera_index)
remove_camera(camera_id)
start_all()
stop_all()
get_frame(camera_id) → frame
get_all_frames() → {camera_id: frame}
detect_available_cameras() → [indexes]
```

**Threading Model:**
- Each camera runs in separate thread
- Non-blocking frame retrieval
- Automatic reconnection on failure
- Health checks every 5 seconds

---

## Data Flow

### Real-Time Detection Flow

```
1. Camera Capture
   └─> CameraStream thread captures frames

2. Frame Distribution
   └─> CameraManager provides frames to processing loop

3. Face Detection
   └─> RecognitionEngine.detect_faces(frame)
   └─> InsightFace identifies faces
   └─> Returns: bounding boxes, landmarks, embeddings

4. Occlusion Analysis
   └─> OcclusionDetector.estimate_occlusion(face)
   └─> Checks detection quality score
   └─> Returns: level (none/mild/moderate/severe)

5. Face Recognition
   └─> RecognitionEngine.recognize_face(embedding)
   └─> Cosine similarity vs all watchlist embeddings
   └─> Dynamic threshold adjustment for occlusion
   └─> Returns: match result with confidence

6. Alert Generation (if match)
   └─> AlertManager.should_alert(person_id)
   └─> Check cooldown period
   └─> Check rate limits
   └─> AlertManager.generate_alert()
   └─> Save evidence frame
   └─> Hash frame (SHA-256)
   └─> Log to alert.log

7. Detection Logging
   └─> DetectionLogger.log_detection()
   └─> Append to detections.log
   └─> All detections logged (match or not)

8. UI Update
   └─> Flask API serves data
   └─> JavaScript polls for updates
   └─> Real-time dashboard refresh
```

---

## Configuration System

### Key Parameters (`config.py`)

#### Detection Thresholds
```python
MATCH_CONFIDENCE_THRESHOLD = 0.55  # Primary threshold
HIGH_CONFIDENCE_THRESHOLD = 0.70   # High-priority
MEDIUM_CONFIDENCE_THRESHOLD = 0.55 # Standard
LOW_CONFIDENCE_THRESHOLD = 0.45    # Review-only
```

#### Occlusion Handling
```python
OCCLUSION_DETECTION_ENABLED = True
ADJUST_THRESHOLD_FOR_OCCLUSION = True
OCCLUSION_CONFIDENCE_PENALTY = {
    "none": 0.0,
    "mild": 0.05,      # +5% threshold
    "moderate": 0.10,  # +10% threshold
    "severe": 0.15     # +15% threshold
}
```

#### Alert System
```python
ALERT_COOLDOWN_SECONDS = 300  # 5 minutes
MAX_ALERTS_PER_HOUR = 50
REQUIRE_SUPERVISOR_APPROVAL = True  # For HIGH/CRITICAL
```

#### Risk Levels
```python
RISK_LEVELS = {
    "CRITICAL": {
        "color": "#DC2626",
        "priority": 1,
        "require_immediate_response": True
    },
    "HIGH": {...},
    "MEDIUM": {...},
    "LOW": {...}
}
```

---

## Security Architecture

### Authorization Hierarchy
```
AUTHORIZED_AGENCIES:
├── CONTROL_ROOM (Monitor only)
├── SECURITY_OFFICER (Basic access)
├── FORENSIC_INVESTIGATOR (Full access)
└── LAW_ENFORCEMENT (Full access + case management)
```

### Audit Trail
```
All operations logged:
├── Watchlist additions/removals
├── Embeddings database builds
├── System starts/stops
├── Alert generations
├── Configuration changes
└── Evidence access
```

### Evidence Integrity
```
Frame Hashing:
├── SHA-256 cryptographic hash
├── Hash stored with alert
├── Verifiable chain of custody
├── Tamper detection
└── Legal admissibility
```

---

## Performance Characteristics

### Timing Benchmarks (Approximate)

```
Face Detection:       ~30ms per frame
Embedding Extraction: ~50ms per face
Recognition Match:    ~5ms (vs 100 watchlist)
Frame Processing:     ~100ms total (1 face)
Alert Generation:     ~200ms (includes frame save)

Real-time Processing: 10 FPS per camera
Post-incident Trace:  2 FPS (more thorough)
```

### Scalability Limits

```
Concurrent Cameras: 8 (configurable to MAX_CAMERAS)
Watchlist Size:     500+ persons (tested)
Embeddings per Person: 5-20 recommended
Video Analysis:     Multi-hour videos supported
Database Size:      ~1KB per person + ~2KB per embedding
```

---

## Error Handling & Resilience

### Camera Failures
```
Automatic Reconnection:
├── 3 attempts with 5-second delays
├── Graceful degradation (other cameras continue)
├── Health monitoring every 5 seconds
└── Status reporting to UI
```

### Processing Errors
```
try-catch at every level:
├── Failed face detection → skip frame
├── Embedding extraction failure → log warning
├── Match computation error → continue with other faces
└── Alert generation failure → log error, continue
```

### Data Integrity
```
CSV Validation:
├── Check required columns on load
├── Auto-repair missing columns
├── Encoding error handling (UTF-8/Latin-1)
└── Backup before modifications
```

---

## Legal & Ethical Architecture

### Privacy Protection
```
Design Principles:
├── No public data exposure
├── Minimal data collection
├── Time-limited retention
├── Anonymization after investigation
└── GDPR compliance mode
```

### Human-in-Loop Requirements
```
Mandatory Verification:
├── ALL alerts require human review
├── Confidence scores always shown
├── No automated actions
├── Supervisor approval for high-risk
└── Right to dispute any detection
```

### Accountability
```
Audit Trail Includes:
├── Who added person to watchlist
├── Who approved detection action
├── Why person was added (case number)
├── When data was accessed
└── All system operations
```

---

## Deployment Considerations

### Hardware Requirements

**Minimum (Testing):**
- CPU: 4 cores
- RAM: 8GB
- Storage: 50GB
- GPU: Optional

**Production:**
- CPU: 8+ cores
- RAM: 16GB+
- GPU: NVIDIA with CUDA (4GB+ VRAM)
- Storage: 500GB+ SSD
- Network: 1 Gbps for IP cameras

### Network Architecture
```
Recommended Setup:
├── Isolated security network
├── No internet access (air-gapped if possible)
├── VLAN for camera feeds
├── Encrypted connections (HTTPS/TLS)
└── VPN access for remote monitoring
```

### Backup Strategy
```
Critical Data:
├── Watchlist CSV (daily backup)
├── Embeddings database (after each build)
├── Alert logs (real-time replication)
├── Evidence frames (incremental backup)
└── Configuration files (version control)
```

---

## Future Enhancements (Not in MVP)

- [ ] Multi-server deployment (load balancing)
- [ ] Advanced biometric fusion (face + gait)
- [ ] Explainable AI dashboard (show why match occurred)
- [ ] Integration with other security systems
- [ ] Mobile app for field officers
- [ ] Advanced analytics (heatmaps, patterns)
- [ ] Cloud backup with encryption
- [ ] API for external system integration

---

*This architecture prioritizes ethical operation, legal compliance, and human oversight.*
