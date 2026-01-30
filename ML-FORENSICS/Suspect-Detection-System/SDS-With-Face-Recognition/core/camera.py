"""
Camera Manager Module
Handles multiple camera feeds with fallback and reconnection
"""

import cv2
import threading
import time
from datetime import datetime
import config


class CameraStream:
    """Individual camera stream handler with reconnection logic."""
    
    def __init__(self, camera_id, camera_index):
        """
        Initialize camera stream.
        
        Args:
            camera_id: Logical camera identifier (e.g., "CAM-01")
            camera_index: Physical camera index or RTSP URL
        """
        self.camera_id = camera_id
        self.camera_index = camera_index
        self.cap = None
        self.frame = None
        self.running = False
        self.thread = None
        self.last_frame_time = None
        self.reconnect_attempts = 0
        self.is_connected = False
    
    def start(self):
        """Start camera stream in separate thread."""
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        print(f"[CAMERA] {self.camera_id} stream started")
    
    def stop(self):
        """Stop camera stream."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        if self.cap:
            self.cap.release()
        print(f"[CAMERA] {self.camera_id} stream stopped")
    
    def _capture_loop(self):
        """Main capture loop running in separate thread."""
        while self.running:
            # Connect if not connected
            if not self.is_connected:
                self._connect()
                if not self.is_connected:
                    time.sleep(config.CAMERA_RECONNECT_DELAY)
                    continue
            
            # Capture frame
            ret, frame = self.cap.read()
            
            if ret:
                self.frame = frame
                self.last_frame_time = datetime.now()
                self.reconnect_attempts = 0
            else:
                print(f"[WARNING] {self.camera_id} frame capture failed")
                self.is_connected = False
                if self.cap:
                    self.cap.release()
    
    def _connect(self):
        """Attempt to connect to camera."""
        if self.reconnect_attempts >= config.CAMERA_RECONNECT_ATTEMPTS:
            print(f"[ERROR] {self.camera_id} max reconnection attempts reached")
            return
        
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            
            if self.cap.isOpened():
                # Test read
                ret, _ = self.cap.read()
                if ret:
                    self.is_connected = True
                    self.reconnect_attempts = 0
                    print(f"[CAMERA] {self.camera_id} connected successfully")
                else:
                    self.cap.release()
                    self.reconnect_attempts += 1
            else:
                self.reconnect_attempts += 1
                
        except Exception as e:
            print(f"[ERROR] {self.camera_id} connection failed: {e}")
            self.reconnect_attempts += 1
    
    def get_frame(self):
        """
        Get latest frame from camera.
        
        Returns:
            numpy.ndarray or None: Latest frame
        """
        return self.frame
    
    def is_alive(self):
        """Check if camera stream is alive and producing frames."""
        if not self.is_connected:
            return False
        
        if self.last_frame_time is None:
            return False
        
        # Check if we've received a frame recently (within last 5 seconds)
        time_diff = (datetime.now() - self.last_frame_time).total_seconds()
        return time_diff < 5.0


class CameraManager:
    """Manages multiple camera streams."""
    
    def __init__(self):
        self.cameras = {}
        self.active_camera_ids = []
    
    def add_camera(self, camera_id, camera_index):
        """
        Add a camera to the manager.
        
        Args:
            camera_id: Logical identifier (e.g., "CAM-ENTRANCE")
            camera_index: Physical index (int) or RTSP URL (str)
        """
        if camera_id in self.cameras:
            print(f"[WARNING] Camera {camera_id} already exists")
            return False
        
        camera = CameraStream(camera_id, camera_index)
        self.cameras[camera_id] = camera
        self.active_camera_ids.append(camera_id)
        
        print(f"[MANAGER] Added camera: {camera_id} (index: {camera_index})")
        return True
    
    def remove_camera(self, camera_id):
        """Remove a camera from the manager."""
        if camera_id not in self.cameras:
            print(f"[WARNING] Camera {camera_id} not found")
            return False
        
        camera = self.cameras[camera_id]
        camera.stop()
        del self.cameras[camera_id]
        self.active_camera_ids.remove(camera_id)
        
        print(f"[MANAGER] Removed camera: {camera_id}")
        return True
    
    def start_all(self):
        """Start all camera streams."""
        for camera_id, camera in self.cameras.items():
            camera.start()
        
        print(f"[MANAGER] Started {len(self.cameras)} cameras")
    
    def stop_all(self):
        """Stop all camera streams."""
        for camera in self.cameras.values():
            camera.stop()
        
        print("[MANAGER] All cameras stopped")
    
    def get_frame(self, camera_id):
        """
        Get latest frame from a specific camera.
        
        Args:
            camera_id: Camera identifier
        
        Returns:
            Frame or None
        """
        if camera_id not in self.cameras:
            return None
        
        return self.cameras[camera_id].get_frame()
    
    def get_all_frames(self):
        """
        Get latest frames from all cameras.
        
        Returns:
            dict: {camera_id: frame}
        """
        frames = {}
        for camera_id in self.active_camera_ids:
            frame = self.get_frame(camera_id)
            if frame is not None:
                frames[camera_id] = frame
        
        return frames
    
    def get_camera_status(self):
        """
        Get status of all cameras.
        
        Returns:
            dict: {camera_id: status_dict}
        """
        status = {}
        for camera_id, camera in self.cameras.items():
            status[camera_id] = {
                "is_alive": camera.is_alive(),
                "is_connected": camera.is_connected,
                "last_frame_time": camera.last_frame_time,
                "reconnect_attempts": camera.reconnect_attempts
            }
        
        return status
    
    @staticmethod
    def detect_available_cameras(max_test=10):
        """
        Detect available camera indexes.
        
        Args:
            max_test: Maximum index to test
        
        Returns:
            list: Available camera indexes
        """
        available = []
        
        for i in range(max_test):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    available.append(i)
                cap.release()
        
        return available
    
    def auto_detect_and_add_cameras(self):
        """Automatically detect and add available cameras."""
        available = self.detect_available_cameras()
        
        if not available:
            print("[MANAGER] No cameras detected")
            return False
        
        for idx in available[:config.MAX_CAMERAS]:
            camera_id = f"CAM-{idx:02d}"
            self.add_camera(camera_id, idx)
        
        print(f"[MANAGER] Auto-detected {len(available)} cameras")
        return True


# ==================== TESTING ====================

def test_camera_manager():
    """Test camera manager functionality."""
    print("[TEST] Camera Manager Test")
    
    manager = CameraManager()
    
    # Detect cameras
    available = manager.detect_available_cameras()
    print(f"[TEST] Available cameras: {available}")
    
    if available:
        # Add first camera
        manager.add_camera("TEST-CAM", available[0])
        manager.start_all()
        
        # Capture a few frames
        time.sleep(2)
        
        for i in range(5):
            frame = manager.get_frame("TEST-CAM")
            if frame is not None:
                print(f"[TEST] Frame {i}: {frame.shape}")
            time.sleep(0.5)
        
        manager.stop_all()
    
    print("[TEST] Test complete")


if __name__ == "__main__":
    test_camera_manager()