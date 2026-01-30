"""
Suspect Detection System - Web Interface
SOC-style dashboard for real-time monitoring
"""

from flask import Flask, render_template, Response, jsonify, request
import cv2
import json
import threading
import time
from datetime import datetime, timedelta
import base64
import numpy as np

# Import core modules
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from core.watchlist import WatchlistManager
from core.recognition import FaceRecognitionEngine
from core.alerts import AlertManager, DetectionLogger, PostIncidentTracer
from core.camera import CameraManager
from core.reports import ReportGenerator

app = Flask(__name__, template_folder='gui/templates', static_folder='gui/static')
app.config['SECRET_KEY'] = 'forensic-sds-secret-key-change-in-production'

# ==================== GLOBAL STATE ====================
watchlist_manager = None
recognition_engine = None
alert_manager = None
detection_logger = None
camera_manager = None
post_incident_tracer = None
report_generator = None

system_running = False
processing_thread = None

# ==================== INITIALIZATION ====================

def initialize_system():
    """Initialize all system components."""
    global watchlist_manager, recognition_engine, alert_manager
    global detection_logger, camera_manager, post_incident_tracer
    
    print("[INIT] Initializing Suspect Detection System...")
    
    # Initialize watchlist
    watchlist_manager = WatchlistManager()
    
    # Load embeddings
    embeddings_data = watchlist_manager.load_embeddings()
    
    if embeddings_data is None:
        print("[WARNING] No embeddings found. System will run in demo mode.")
        # Create dummy embeddings for demo
        embeddings_data = {
            "embeddings": np.random.randn(5, 512),
            "person_ids": [f"DEMO-{i:03d}" for i in range(5)],
            "model": "buffalo_l",
            "total_embeddings": 5,
            "total_persons": 5
        }
    
    # Initialize recognition engine
    recognition_engine = FaceRecognitionEngine(embeddings_data)
    
    # Initialize alert system
    alert_manager = AlertManager(watchlist_manager)
    detection_logger = DetectionLogger()
    
    # Initialize post-incident tracer
    post_incident_tracer = PostIncidentTracer(recognition_engine, detection_logger)
    
    # Initialize camera manager
    camera_manager = CameraManager()
    
    # Initialize report generator
    report_generator = ReportGenerator(alert_manager, detection_logger)
    
    print("[INIT] System initialization complete")


def processing_loop():
    """Main processing loop for real-time detection."""
    global system_running
    
    print("[SYSTEM] Processing loop started")
    
    frame_count = 0
    
    while system_running:
        try:
            # Get frames from all cameras
            frames = camera_manager.get_all_frames()
            
            if not frames:
                time.sleep(0.1)
                continue
            
            # Process each frame
            for camera_id, frame in frames.items():
                if frame is None:
                    continue
                
                start_time = time.time()
                
                # Detect and recognize faces
                detections = recognition_engine.process_frame(frame, camera_id)
                
                processing_time = (time.time() - start_time) * 1000  # ms
                
                # Log detections
                for detection in detections:
                    detection_logger.log_detection(detection, camera_id)
                    
                    # Generate alerts for matches
                    if detection["person_id"] is not None:
                        alert = alert_manager.generate_alert(detection, frame, camera_id)
                        if alert:
                            print(f"[ALERT] {alert['alert_id']} - {alert['full_name']} ({alert['risk_level']})")
                
                # Log processing metrics
                detection_logger.log_frame_processing(camera_id, len(detections), processing_time)
            
            frame_count += 1
            
            # Control frame rate
            time.sleep(1.0 / config.DEFAULT_CAMERA_FPS)
            
        except Exception as e:
            print(f"[ERROR] Processing loop error: {e}")
            time.sleep(1.0)
    
    print("[SYSTEM] Processing loop stopped")


# ==================== ROUTES ====================

@app.route('/')
def index():
    """Main dashboard."""
    return render_template('dashboard.html')


@app.route('/api/system/start', methods=['POST'])
def start_system():
    """Start the detection system."""
    global system_running, processing_thread
    
    if system_running:
        return jsonify({"status": "error", "message": "System already running"})
    
    # Auto-detect and add cameras
    if not camera_manager.cameras:
        camera_manager.auto_detect_and_add_cameras()
    
    # Start cameras
    camera_manager.start_all()
    
    # Start processing
    system_running = True
    processing_thread = threading.Thread(target=processing_loop, daemon=True)
    processing_thread.start()
    
    return jsonify({"status": "success", "message": "System started"})


@app.route('/api/system/stop', methods=['POST'])
def stop_system():
    """Stop the detection system."""
    global system_running
    
    if not system_running:
        return jsonify({"status": "error", "message": "System not running"})
    
    system_running = False
    camera_manager.stop_all()
    
    return jsonify({"status": "success", "message": "System stopped"})


@app.route('/api/system/status')
def system_status():
    """Get system status."""
    camera_status = camera_manager.get_camera_status()
    alert_stats = alert_manager.get_alert_statistics()
    
    return jsonify({
        "running": system_running,
        "cameras": camera_status,
        "alerts": alert_stats,
        "watchlist_count": len(watchlist_manager.get_all_persons())
    })


@app.route('/api/alerts/recent')
def recent_alerts():
    """Get recent alerts."""
    hours = request.args.get('hours', 24, type=int)
    alerts = alert_manager.get_recent_alerts(hours)
    return jsonify(alerts)


@app.route('/api/watchlist')
def get_watchlist():
    """Get watchlist."""
    persons = watchlist_manager.get_all_persons()
    return jsonify(persons)


@app.route('/api/watchlist/add', methods=['POST'])
def add_to_watchlist():
    """Add person to watchlist."""
    data = request.json
    
    try:
        success = watchlist_manager.add_person(
            person_id=data['person_id'],
            case_id=data['case_id'],
            full_name=data['full_name'],
            risk_level=data['risk_level'],
            legal_status=data['legal_status'],
            authorized_agency=data['authorized_agency'],
            added_by=data['added_by'],
            notes=data.get('notes', '')
        )
        
        if success:
            return jsonify({"status": "success", "message": "Person added to watchlist"})
        else:
            return jsonify({"status": "error", "message": "Failed to add person"})
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route('/api/report/generate', methods=['POST'])
def generate_report():
    """Generate a detection report."""
    try:
        # Get recent alerts (last 24 hours)
        recent_alerts = alert_manager.get_recent_alerts(hours=24)
        
        if not recent_alerts:
            return jsonify({"status": "error", "message": "No alerts found in the last 24 hours"})
        
        # Generate report
        session_start = datetime.now() - timedelta(hours=24)
        session_end = datetime.now()
        
        report_path = report_generator.generate_session_report(session_start, session_end, output_format="docx")
        
        return jsonify({
            "status": "success", 
            "message": "Report generated successfully",
            "path": report_path,
            "filename": os.path.basename(report_path)
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


def generate_camera_feed(camera_id):
    """Generate MJPEG stream for a camera."""
    while True:
        if not system_running:
            time.sleep(0.5)
            continue
        
        frame = camera_manager.get_frame(camera_id)
        
        if frame is None:
            time.sleep(0.1)
            continue
        
        # Get detections for this frame
        detections = recognition_engine.process_frame(frame, camera_id)
        
        # Draw detections on frame
        for detection in detections:
            frame = recognition_engine.draw_detection_on_frame(frame, detection)
        
        # Add camera ID and timestamp
        cv2.putText(frame, f"{camera_id} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        time.sleep(1.0 / config.DEFAULT_CAMERA_FPS)


@app.route('/video_feed/<camera_id>')
def video_feed(camera_id):
    """Video streaming route."""
    return Response(generate_camera_feed(camera_id),
                   mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/camera/list')
def list_cameras():
    """List all cameras."""
    cameras = list(camera_manager.cameras.keys())
    return jsonify(cameras)


@app.route('/api/trace', methods=['POST'])
def trace_suspect():
    """Trace suspect in uploaded video."""
    data = request.json
    video_path = data.get('video_path')
    person_id = data.get('person_id')
    
    if not video_path or not person_id:
        return jsonify({"status": "error", "message": "Missing parameters"})
    
    # Run trace in background thread
    def run_trace():
        detections = post_incident_tracer.trace_suspect_in_video(video_path, person_id)
        print(f"[TRACE] Found {len(detections)} occurrences")
    
    thread = threading.Thread(target=run_trace, daemon=True)
    thread.start()
    
    return jsonify({"status": "success", "message": "Trace started"})


# ==================== MAIN ====================

if __name__ == '__main__':
    # Initialize system
    initialize_system()
    
    print(f"\n{'='*60}")
    print(f"  {config.SYSTEM_NAME}")
    print(f"  Version: {config.VERSION}")
    print(f"  Deployment: {config.DEPLOYMENT_ID}")
    print(f"{'='*60}\n")
    
    print("Starting web interface on http://localhost:5000")
    print("Press CTRL+C to stop\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)