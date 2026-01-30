"""
Face Detection & Recognition Engine
Handles real-time detection with occlusion awareness
"""

import cv2
import numpy as np
from scipy.spatial.distance import cosine
from insightface.app import FaceAnalysis
import config
from datetime import datetime
import hashlib


class OcclusionDetector:
    """Estimates face occlusion level using facial landmarks."""
    
    @staticmethod
    def estimate_occlusion(face):
        """
        Estimate occlusion level from InsightFace detection.
        
        Args:
            face: InsightFace face object with landmarks
        
        Returns:
            tuple: (occlusion_level, occlusion_percentage)
            occlusion_level: "none", "mild", "moderate", "severe"
        """
        # Use face quality score as proxy for occlusion
        # InsightFace provides detection score
        det_score = face.det_score if hasattr(face, 'det_score') else 1.0
        
        # Lower detection score suggests occlusion
        if det_score > 0.95:
            return "none", 0.0
        elif det_score > 0.85:
            return "mild", 0.15
        elif det_score > 0.70:
            return "moderate", 0.35
        else:
            return "severe", 0.55
    
    @staticmethod
    def check_mask_presence(face, frame):
        """
        Check if person is wearing a mask using simple heuristics.
        
        Args:
            face: InsightFace face object
            frame: Original frame
        
        Returns:
            bool: True if mask detected
        """
        # Extract face region
        x1, y1, x2, y2 = list(map(int, face.bbox))
        
        # Ensure coordinates are within frame bounds
        h, w = frame.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        
        face_region = frame[y1:y2, x1:x2]
        
        if face_region.size == 0:
            return False
        
        # Check lower half of face (where mask would be)
        face_h = y2 - y1
        lower_half_y = int(face_h * 0.5)
        lower_region = face_region[lower_half_y:, :]
        
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(lower_region, cv2.COLOR_BGR2HSV)
        
        # Detect typical mask colors (blue, white, black)
        # More strict thresholds to reduce false positives
        blue_mask = cv2.inRange(hsv, (100, 80, 80), (130, 255, 255))
        white_mask = cv2.inRange(hsv, (0, 0, 220), (180, 30, 255))
        black_mask = cv2.inRange(hsv, (0, 0, 0), (180, 50, 40))
        
        combined = cv2.bitwise_or(blue_mask, cv2.bitwise_or(white_mask, black_mask))
        mask_percentage = np.count_nonzero(combined) / combined.size
        
        # Require at least 50% coverage to consider it a mask (more strict)
        return mask_percentage > 0.50


class FaceRecognitionEngine:
    """Core recognition engine with occlusion handling."""
    
    def __init__(self, embeddings_data):
        """
        Initialize recognition engine.
        
        Args:
            embeddings_data: Dictionary with 'embeddings' and 'person_ids'
        """
        self.known_embeddings = embeddings_data["embeddings"]
        self.known_person_ids = embeddings_data["person_ids"]
        self.model_name = embeddings_data.get("model", "unknown")
        
        self.face_analyzer = None
        self.occlusion_detector = OcclusionDetector()
        
        print(f"[ENGINE] Recognition engine initialized with {len(self.known_embeddings)} embeddings")
    
    def _init_face_analyzer(self):
        """Lazy initialization of face analyzer."""
        if self.face_analyzer is None:
            print("[ENGINE] Loading InsightFace model...")
            self.face_analyzer = FaceAnalysis(name=config.FACE_DETECTION_MODEL)
            ctx_id = 0 if config.GPU_ENABLED else -1
            self.face_analyzer.prepare(ctx_id=ctx_id)
    
    def detect_faces(self, frame):
        """
        Detect all faces in a frame.
        
        Args:
            frame: OpenCV image (BGR)
        
        Returns:
            List of face objects from InsightFace
        """
        self._init_face_analyzer()
        
        try:
            faces = self.face_analyzer.get(frame)
            return faces
        except Exception as e:
            print(f"[ERROR] Face detection failed: {e}")
            return []
    
    def recognize_face(self, face_embedding, adjust_for_occlusion=True, 
                      occlusion_level="none"):
        """
        Match a face embedding against the watchlist.
        
        Args:
            face_embedding: Face embedding vector
            adjust_for_occlusion: Whether to adjust threshold for occlusion
            occlusion_level: Level of occlusion detected
        
        Returns:
            dict: {
                "person_id": matched person ID or None,
                "confidence": match confidence (0-1),
                "distance": cosine distance,
                "threshold_used": threshold applied,
                "occlusion_adjusted": whether adjustment was made
            }
        """
        if len(self.known_embeddings) == 0:
            return {
                "person_id": None,
                "confidence": 0.0,
                "distance": 1.0,
                "threshold_used": config.MATCH_CONFIDENCE_THRESHOLD,
                "occlusion_adjusted": False
            }
        
        # Calculate distances to all known embeddings
        distances = [cosine(face_embedding, known_emb) 
                    for known_emb in self.known_embeddings]
        
        min_distance = min(distances)
        min_index = distances.index(min_distance)
        matched_person_id = self.known_person_ids[min_index]
        
        # Convert distance to confidence (1 - distance)
        confidence = 1.0 - min_distance
        
        # Adjust threshold based on occlusion
        threshold = config.MATCH_CONFIDENCE_THRESHOLD
        occlusion_adjusted = False
        
        if adjust_for_occlusion and config.ADJUST_THRESHOLD_FOR_OCCLUSION:
            penalty = config.OCCLUSION_CONFIDENCE_PENALTY.get(occlusion_level, 0.0)
            threshold = threshold + penalty
            occlusion_adjusted = penalty > 0.0
        
        # Determine if match is valid
        is_match = confidence >= threshold
        
        return {
            "person_id": matched_person_id if is_match else None,
            "confidence": confidence,
            "distance": min_distance,
            "threshold_used": threshold,
            "occlusion_adjusted": occlusion_adjusted,
            "all_distances": distances  # For debugging
        }
    
    def process_frame(self, frame, camera_id="unknown"):
        """
        Process a single frame and detect all faces with recognition.
        
        Args:
            frame: OpenCV image
            camera_id: Identifier for the camera
        
        Returns:
            List of detection results
        """
        detections = []
        
        faces = self.detect_faces(frame)
        
        for face in faces:
            # Extract face embedding
            embedding = face.embedding
            
            # Detect occlusion
            occlusion_level, occlusion_pct = self.occlusion_detector.estimate_occlusion(face)
            mask_detected = self.occlusion_detector.check_mask_presence(face, frame)
            
            # Recognize face
            recognition_result = self.recognize_face(
                embedding, 
                adjust_for_occlusion=True,
                occlusion_level=occlusion_level
            )
            
            # Get bounding box
            bbox = list(map(int, face.bbox))
            
            detection = {
                "camera_id": camera_id,
                "timestamp": datetime.now().isoformat(),
                "bbox": bbox,
                "embedding": embedding,
                "person_id": recognition_result["person_id"],
                "confidence": recognition_result["confidence"],
                "distance": recognition_result["distance"],
                "threshold_used": recognition_result["threshold_used"],
                "occlusion_level": occlusion_level,
                "occlusion_percentage": occlusion_pct,
                "mask_detected": mask_detected,
                "occlusion_adjusted": recognition_result["occlusion_adjusted"],
                "detection_score": face.det_score if hasattr(face, 'det_score') else 1.0
            }
            
            detections.append(detection)
        
        return detections
    
    def draw_detection_on_frame(self, frame, detection, show_confidence=True):
        """
        Draw detection box and information on frame.
        
        Args:
            frame: OpenCV image
            detection: Detection dictionary
            show_confidence: Whether to show confidence score
        
        Returns:
            Annotated frame
        """
        x1, y1, x2, y2 = detection["bbox"]
        person_id = detection["person_id"]
        confidence = detection["confidence"]
        occlusion_level = detection["occlusion_level"]
        mask_detected = detection["mask_detected"]
        
        # Color based on match status and confidence
        if person_id is None:
            color = (128, 128, 128)  # Gray for no match
            label = "Unknown"
        else:
            # Color by confidence level
            if confidence >= config.HIGH_CONFIDENCE_THRESHOLD:
                color = (0, 0, 255)  # Red for high confidence match
            elif confidence >= config.MEDIUM_CONFIDENCE_THRESHOLD:
                color = (0, 165, 255)  # Orange for medium
            else:
                color = (0, 255, 255)  # Yellow for low
            
            label = f"{person_id}"
            if show_confidence:
                label += f" ({confidence:.2f})"
        
        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        # Draw label background
        label_height = 25
        cv2.rectangle(frame, (x1, y1 - label_height), (x2, y1), color, -1)
        
        # Draw label text
        cv2.putText(frame, label, (x1 + 5, y1 - 7),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Draw occlusion indicator
        if occlusion_level != "none" or mask_detected:
            indicator = f"Occlusion: {occlusion_level}"
            if mask_detected:
                indicator += " [MASK]"
            
            cv2.putText(frame, indicator, (x1, y2 + 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        
        return frame
    
    @staticmethod
    def hash_frame(frame):
        """
        Generate cryptographic hash of a frame for forensic integrity.
        
        Args:
            frame: OpenCV image
        
        Returns:
            str: SHA-256 hash
        """
        if config.ENABLE_FRAME_HASHING:
            frame_bytes = frame.tobytes()
            return hashlib.sha256(frame_bytes).hexdigest()
        return None


# ==================== TESTING UTILITIES ====================

def test_recognition_engine():
    """Test the recognition engine with a sample image."""
    print("[TEST] Recognition engine test...")
    
    # This would require actual embeddings to be loaded
    # For now, just verify initialization
    
    sample_data = {
        "embeddings": np.random.randn(10, 512),  # 10 random embeddings
        "person_ids": [f"TEST-{i:03d}" for i in range(10)],
        "model": "buffalo_l"
    }
    
    engine = FaceRecognitionEngine(sample_data)
    print("[TEST] Engine initialized successfully")


if __name__ == "__main__":
    test_recognition_engine()