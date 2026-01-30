# 🚀 QUICK START GUIDE

## Forensic Suspect Detection System

### 5-Minute Setup

---

## Step 1: Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

---

## Step 2: Create Demo Watchlist (Testing)

```bash
python utils/init_demo.py
```

This creates 3 demo entries for testing the interface.

---

## Step 3: Start the System

```bash
python app.py
```

Open browser: **http://localhost:5000**

---

## Step 4: Click "START SYSTEM"

The GUI will:
- Auto-detect webcams
- Start live video feeds
- Display alerts when matches occur

---

## For Production Use

### 1. Add Real Persons to Watchlist

```bash
python utils/add_person.py
```

Follow prompts to enter:
- Person ID (e.g., POI-2025-001)
- Case ID
- Full name
- Risk level
- Legal status
- Authorized agency

### 2. Collect Training Photos (LIVE)

**Option A: Live Webcam Capture (Recommended)**

```bash
python utils/collect_samples.py
```

This will:
- Show you the watchlist
- Let you select a person
- Guide you through capturing 50 normal + 50 masked photos
- Automatically save to correct directories
- Capture from multiple angles as you move

**Instructions during capture:**
- Phase 1: NORMAL FACE
  - Look at camera
  - Slowly rotate head left/right
  - Tilt up/down
  - Move closer/farther
  
- Phase 2: MASKED FACE
  - Put on mask
  - Repeat same movements
  - Try different occlusion levels

**Option B: Manual Image Upload**

Create directory structure:
```
data/images/
├── POI-2025-001/
│   ├── normal/
│   │   ├── photo1.jpg
│   │   └── photo2.jpg
│   └── masked/
│       ├── photo1.jpg
│       └── photo2.jpg
```

**Requirements:**
- 5-20 images per mode (50 recommended)
- Clear frontal face visible
- Various lighting/angles
- Multiple poses

### 3. Build Embeddings

```bash
python utils/build_embeddings.py
```

This creates the facial recognition database from all captured images.

### 4. Start Detection

```bash
python app.py
```

---

## Post-Incident Video Analysis

Backtrack suspect through recorded footage:

```bash
python utils/analyze_video.py
```

Follow prompts to:
1. Select video file
2. Choose suspect
3. Generate timeline

---

## Key Features

### ✅ Real-Time Detection
- Multi-camera support
- Occlusion handling
- Mask detection
- Live alerts

### ✅ Watchlist Management
- Risk levels (CRITICAL → LOW)
- Legal status tracking
- Case-based organization

### ✅ Post-Incident Tracing
- Historical video analysis
- Timeline generation
- Evidence extraction

### ✅ Forensic Logging
- Audit trail
- Frame hashing
- Chain of custody

### ✅ SOC-Style Interface
- Dark theme dashboard
- Live camera feeds
- Alert monitoring
- System status

---

## Configuration

Edit `config.py` to adjust:

```python
# Detection thresholds
MATCH_CONFIDENCE_THRESHOLD = 0.55
HIGH_CONFIDENCE_THRESHOLD = 0.70

# Camera settings
MAX_CAMERAS = 8
DEFAULT_CAMERA_FPS = 10

# Alert settings
ALERT_COOLDOWN_SECONDS = 300
```

---

## Troubleshooting

### No cameras detected?
```bash
# Check available cameras
python -c "from core.camera import CameraManager; print(CameraManager.detect_available_cameras())"
```

### Low accuracy?
- Add more training images (10-20 per person)
- Ensure clear frontal faces
- Include variety: lighting, angles
- Lower confidence threshold

### High false positives?
- Increase MATCH_CONFIDENCE_THRESHOLD
- Improve image quality
- Check camera positioning

---

## Safety Reminders

⚠️ **Human verification REQUIRED for every detection**

This system:
- ✅ Assists investigators
- ✅ Provides probabilistic confidence scores
- ✅ Logs all operations for audit
- ❌ Does NOT accuse or punish
- ❌ Does NOT send public alerts
- ❌ Does NOT make arrest decisions

**Respect privacy. Respect rights. Respect dignity.**

---

## Documentation

- **Full README:** [README.md](README.md)
- **System Architecture Detail:** [ARCHITECTURE.md](ARCHITECTURE.md)
- **System Config:** [config.py](config.py)
- **API Routes:** [app.py](app.py)
- **Logs:** `logs/` directory

---

## Support

For issues or questions:
1. Check [README.md](README.md) for detailed documentation
2. Review logs/ directory for system errors
3. Verify configuration in [config.py](config.py)

---

*Built with ethical AI principles and legal safeguards.*