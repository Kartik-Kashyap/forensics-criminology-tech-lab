"""
Utility: Post-Incident Video Analyzer
Trace suspect movement through recorded video footage
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from core.watchlist import WatchlistManager
from core.recognition import FaceRecognitionEngine
from core.alerts import PostIncidentTracer, DetectionLogger
import numpy as np


def analyze_video():
    """Interactive video analysis for suspect tracing."""
    print("\n" + "="*60)
    print("  POST-INCIDENT VIDEO ANALYSIS")
    print("="*60 + "\n")
    
    # Initialize components
    print("Initializing system components...")
    
    watchlist_manager = WatchlistManager()
    embeddings_data = watchlist_manager.load_embeddings()
    
    if embeddings_data is None:
        print("\n[ERROR] No embeddings database found.")
        print("Please run: python utils/build_embeddings.py")
        return
    
    recognition_engine = FaceRecognitionEngine(embeddings_data)
    detection_logger = DetectionLogger()
    tracer = PostIncidentTracer(recognition_engine, detection_logger)
    
    print("[OK] System ready\n")
    
    # Get video file
    video_path = input("Enter path to video file: ").strip()
    
    if not os.path.exists(video_path):
        print(f"\n[ERROR] Video file not found: {video_path}")
        return
    
    # List available persons in watchlist
    persons = watchlist_manager.get_all_persons()
    
    if not persons:
        print("\n[ERROR] No persons in watchlist.")
        return
    
    print(f"\nWatchlist ({len(persons)} persons):")
    for i, person in enumerate(persons, 1):
        print(f"  {i}. {person['PersonID']} - {person['FullName']} ({person['LegalStatus']})")
    
    # Select person
    while True:
        try:
            choice = int(input("\nSelect person to trace (number): "))
            if 1 <= choice <= len(persons):
                person_id = persons[choice - 1]['PersonID']
                person_name = persons[choice - 1]['FullName']
                break
        except ValueError:
            pass
        print("Invalid choice. Try again.")
    
    # Output path (optional)
    save_output = input("\nSave annotated video? (yes/no): ").strip().lower()
    output_path = None
    
    if save_output == 'yes':
        output_filename = f"trace_{person_id}_{os.path.basename(video_path)}"
        output_path = os.path.join(config.EVIDENCE_DIR, output_filename)
        print(f"Output will be saved to: {output_path}")
    
    # Confirm
    print("\n" + "-"*60)
    print(f"Video: {video_path}")
    print(f"Target: {person_id} ({person_name})")
    print(f"Confidence Threshold: {config.TRACE_CONFIDENCE_THRESHOLD}")
    if output_path:
        print(f"Output: {output_path}")
    print("-"*60)
    
    confirm = input("\nStart analysis? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        print("\n" + "="*60)
        print("ANALYSIS IN PROGRESS...")
        print("="*60 + "\n")
        
        try:
            detections = tracer.trace_suspect_in_video(
                video_path, 
                person_id, 
                output_path
            )
            
            print("\n" + "="*60)
            print("[OK] ANALYSIS COMPLETE")
            print("="*60)
            print(f"Total detections: {len(detections)}")
            
            if detections:
                print("\nDetection timeline:")
                for i, detection in enumerate(detections[:10], 1):  # Show first 10
                    timestamp = detection['video_timestamp']
                    confidence = detection['confidence']
                    frame_num = detection['frame_number']
                    print(f"  {i}. Frame {frame_num} | {timestamp:.1f}s | Confidence: {confidence:.2f}")
                
                if len(detections) > 10:
                    print(f"  ... and {len(detections) - 10} more")
                
                print(f"\nDetailed report saved to: {config.SUSPECT_TRACES_DIR}")
            else:
                print("\nNo detections found.")
                print("Try:")
                print("  - Lower confidence threshold in config.py")
                print("  - Verify person images quality")
                print("  - Check video quality")
            
        except Exception as e:
            print(f"\n[ERROR] Analysis error: {e}")
    else:
        print("\nCancelled.")


if __name__ == "__main__":
    analyze_video()