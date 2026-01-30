"""
Alert System Module
Internal alerts to control room and authorized personnel only
"""

import os
import json
from datetime import datetime, timedelta
import cv2
import config
from core.recognition import FaceRecognitionEngine


class AlertManager:
    """Manages alerts with cooldown and forensic logging."""
    
    def __init__(self, watchlist_manager):
        """
        Initialize alert manager.
        
        Args:
            watchlist_manager: WatchlistManager instance
        """
        self.watchlist_manager = watchlist_manager
        self.alert_cooldowns = {}  # person_id -> last_alert_time
        self.alert_history = []
        self.alert_count = 0
        
        # Ensure alert frames directory exists
        os.makedirs(config.ALERT_FRAMES_DIR, exist_ok=True)
    
    def should_alert(self, person_id):
        """
        Check if an alert should be generated (respecting cooldown).
        
        Args:
            person_id: Person identifier
        
        Returns:
            bool: True if alert should be sent
        """
        now = datetime.now()
        
        # Check if person is in cooldown
        if person_id in self.alert_cooldowns:
            last_alert = self.alert_cooldowns[person_id]
            time_diff = (now - last_alert).total_seconds()
            
            if time_diff < config.ALERT_COOLDOWN_SECONDS:
                return False
        
        # Check hourly rate limit
        one_hour_ago = now - timedelta(hours=1)
        recent_alerts = [a for a in self.alert_history 
                        if datetime.fromisoformat(a["timestamp"]) > one_hour_ago]
        
        if len(recent_alerts) >= config.MAX_ALERTS_PER_HOUR:
            print("[WARNING] Alert rate limit reached. Suppressing alert.")
            return False
        
        return True
    
    def generate_alert(self, detection, frame, camera_id):
        """
        Generate a forensic-grade alert.
        
        Args:
            detection: Detection dictionary from recognition engine
            frame: Original frame (for evidence)
            camera_id: Camera identifier
        
        Returns:
            dict: Alert object or None if alert suppressed
        """
        person_id = detection["person_id"]
        
        if not self.should_alert(person_id):
            return None
        
        # Get person information from watchlist
        person_info = self.watchlist_manager.get_person_info(person_id)
        
        if person_info is None:
            print(f"[ERROR] Person {person_id} not found in watchlist")
            return None
        
        # Determine alert priority
        risk_level = person_info["RiskLevel"]
        risk_config = config.get_risk_level_config(risk_level)
        
        # Save evidence frame
        frame_filename = self._save_alert_frame(frame, detection, person_id)
        frame_hash = FaceRecognitionEngine.hash_frame(frame)
        
        # Create alert object
        alert = {
            "alert_id": f"ALERT-{self.alert_count:06d}",
            "timestamp": detection["timestamp"],
            "person_id": person_id,
            "full_name": person_info["FullName"],
            "case_id": person_info["CaseID"],
            "legal_status": person_info["LegalStatus"],
            "risk_level": risk_level,
            "priority": risk_config["priority"],
            "require_immediate_response": risk_config["require_immediate_response"],
            "camera_id": camera_id,
            "confidence": float(detection["confidence"]),  # Convert numpy float32
            "threshold_used": float(detection["threshold_used"]),  # Convert numpy float32
            "occlusion_level": detection["occlusion_level"],
            "occlusion_percentage": float(detection["occlusion_percentage"]),  # Convert numpy float32
            "mask_detected": bool(detection["mask_detected"]),  # Convert numpy bool
            "bbox": [int(x) for x in detection["bbox"]],  # Convert numpy array
            "evidence_frame": frame_filename,
            "frame_hash": frame_hash,
            "authorized_agency": person_info["AuthorizedAgency"],
            "notes": person_info["Notes"],
            "model_used": config.FACE_DETECTION_MODEL,
            "system_version": config.VERSION
        }
        
        # Update cooldown
        self.alert_cooldowns[person_id] = datetime.now()
        
        # Add to history
        self.alert_history.append(alert)
        self.alert_count += 1
        
        # Log alert
        self._log_alert(alert)
        
        # Update last detected in watchlist
        self.watchlist_manager.update_last_detected(person_id)
        
        print(f"[ALERT] Generated: {alert['alert_id']} - {person_id} ({risk_level})")
        
        return alert
    
    def _save_alert_frame(self, frame, detection, person_id):
        """
        Save frame with detection for forensic evidence.
        
        Args:
            frame: Original frame
            detection: Detection dictionary
            person_id: Person identifier
        
        Returns:
            str: Filename of saved frame
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{person_id}_{timestamp}.jpg"
        filepath = os.path.join(config.ALERT_FRAMES_DIR, filename)
        
        # Draw detection on frame
        annotated_frame = frame.copy()
        x1, y1, x2, y2 = detection["bbox"]
        
        # Draw red bounding box
        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
        
        # Add timestamp and person ID
        info_text = f"{person_id} | {detection['confidence']:.2f}"
        cv2.putText(annotated_frame, info_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        timestamp_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(annotated_frame, timestamp_text, (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Save frame
        cv2.imwrite(filepath, annotated_frame)
        
        return filename
    
    def _log_alert(self, alert):
        """Log alert to forensic alert log."""
        log_entry = json.dumps(alert, indent=2)
        
        with open(config.ALERT_LOG, "a") as f:
            f.write(f"{log_entry}\n")
            f.write("-" * 80 + "\n")
    
    def get_recent_alerts(self, hours=24):
        """
        Get recent alerts within specified time window.
        
        Args:
            hours: Number of hours to look back
        
        Returns:
            List of recent alerts
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent = [a for a in self.alert_history 
                 if datetime.fromisoformat(a["timestamp"]) > cutoff_time]
        
        # Sort by timestamp (newest first)
        recent.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return recent
    
    def get_alerts_by_person(self, person_id):
        """Get all alerts for a specific person."""
        return [a for a in self.alert_history if a["person_id"] == person_id]
    
    def get_alert_statistics(self):
        """Get alert statistics for monitoring."""
        total_alerts = len(self.alert_history)
        
        if total_alerts == 0:
            return {
                "total_alerts": 0,
                "alerts_by_risk": {},
                "alerts_by_status": {},
                "avg_confidence": 0.0
            }
        
        # Group by risk level
        alerts_by_risk = {}
        for alert in self.alert_history:
            risk = alert["risk_level"]
            alerts_by_risk[risk] = alerts_by_risk.get(risk, 0) + 1
        
        # Group by legal status
        alerts_by_status = {}
        for alert in self.alert_history:
            status = alert["legal_status"]
            alerts_by_status[status] = alerts_by_status.get(status, 0) + 1
        
        # Average confidence
        avg_confidence = sum(a["confidence"] for a in self.alert_history) / total_alerts
        
        return {
            "total_alerts": total_alerts,
            "alerts_by_risk": alerts_by_risk,
            "alerts_by_status": alerts_by_status,
            "avg_confidence": avg_confidence,
            "unique_persons": len(set(a["person_id"] for a in self.alert_history))
        }
    
    def clear_cooldowns(self):
        """Clear all alert cooldowns (admin function)."""
        self.alert_cooldowns.clear()
        print("[ADMIN] Alert cooldowns cleared.")


class DetectionLogger:
    """Logs all detections for forensic analysis."""
    
    def __init__(self):
        self.detection_count = 0
    
    def log_detection(self, detection, camera_id):
        """
        Log a detection event.
        
        Args:
            detection: Detection dictionary
            camera_id: Camera identifier
        """
        log_entry = {
            "detection_id": f"DET-{self.detection_count:08d}",
            "timestamp": detection["timestamp"],
            "camera_id": camera_id,
            "person_id": detection["person_id"],
            "confidence": float(detection["confidence"]),  # Convert numpy float32 to Python float
            "occlusion_level": detection["occlusion_level"],
            "mask_detected": bool(detection["mask_detected"]),  # Convert numpy bool to Python bool
            "bbox": [int(x) for x in detection["bbox"]]  # Convert numpy int to Python int
        }
        
        with open(config.DETECTION_LOG, "a") as f:
            f.write(f"{json.dumps(log_entry)}\n")
        
        self.detection_count += 1
    
    def log_frame_processing(self, camera_id, num_faces, processing_time):
        """Log frame processing metrics."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "camera_id": camera_id,
            "num_faces": num_faces,
            "processing_time_ms": processing_time
        }
        
        with open(config.SYSTEM_LOG, "a") as f:
            f.write(f"{json.dumps(log_entry)}\n")


# ==================== POST-INCIDENT TRACING ====================

class PostIncidentTracer:
    """Backtrack suspect movement through historical footage."""
    
    def __init__(self, recognition_engine, detection_logger):
        """
        Initialize post-incident tracer.
        
        Args:
            recognition_engine: FaceRecognitionEngine instance
            detection_logger: DetectionLogger instance
        """
        self.recognition_engine = recognition_engine
        self.detection_logger = detection_logger
    
    def trace_suspect_in_video(self, video_path, person_id, output_path=None):
        """
        Trace a suspect through recorded video footage.
        
        Args:
            video_path: Path to video file
            person_id: Person to trace
            output_path: Optional path to save annotated video
        
        Returns:
            List of detections with timestamps
        """
        print(f"[TRACE] Analyzing video: {video_path}")
        print(f"[TRACE] Looking for: {person_id}")
        
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print(f"[ERROR] Cannot open video: {video_path}")
            return []
        
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        print(f"[TRACE] Video info: {total_frames} frames, {fps} FPS, {duration:.1f}s duration")
        
        detections = []
        frame_count = 0
        
        # Video writer for output (optional)
        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            writer = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Process every Nth frame to speed up
            if frame_count % max(1, fps // 2) != 0:  # Process 2 frames per second
                continue
            
            # Detect and recognize
            frame_detections = self.recognition_engine.process_frame(frame, "HISTORICAL")
            
            for detection in frame_detections:
                if detection["person_id"] == person_id:
                    # Use lower threshold for historical analysis
                    if detection["confidence"] >= config.TRACE_CONFIDENCE_THRESHOLD:
                        timestamp_seconds = frame_count / fps
                        detection["video_timestamp"] = timestamp_seconds
                        detection["frame_number"] = frame_count
                        detections.append(detection)
                        
                        print(f"[TRACE] Found at {timestamp_seconds:.1f}s (frame {frame_count})")
                        
                        # Annotate frame if saving
                        if writer:
                            annotated = self.recognition_engine.draw_detection_on_frame(
                                frame.copy(), detection
                            )
                            writer.write(annotated)
            
            # Progress indicator
            if frame_count % (fps * 10) == 0:  # Every 10 seconds
                progress = (frame_count / total_frames) * 100
                print(f"[TRACE] Progress: {progress:.1f}%")
        
        cap.release()
        if writer:
            writer.release()
        
        print(f"[TRACE] Complete. Found {len(detections)} occurrences.")
        
        # Save trace report
        self._save_trace_report(person_id, video_path, detections)
        
        return detections
    
    def _save_trace_report(self, person_id, video_path, detections):
        """Save post-incident trace report."""
        report_filename = f"trace_{person_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = os.path.join(config.SUSPECT_TRACES_DIR, report_filename)
        
        report = {
            "person_id": person_id,
            "video_source": video_path,
            "analysis_timestamp": datetime.now().isoformat(),
            "total_detections": len(detections),
            "detections": detections,
            "confidence_threshold": config.TRACE_CONFIDENCE_THRESHOLD
        }
        
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"[TRACE] Report saved: {report_path}")


if __name__ == "__main__":
    print("[INFO] Alert system module loaded.")