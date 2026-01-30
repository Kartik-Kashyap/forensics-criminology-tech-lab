"""
Live Sample Collection Module
Interactive webcam-based photo capture for watchlist persons
Captures both normal and masked/occluded face samples
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import config
from core.watchlist import WatchlistManager


def collect_live_samples(person_id, count=50, delay=0.5):
    """
    Collect live face samples using webcam for a person in the watchlist.
    
    Args:
        person_id: Person identifier from watchlist
        count: Number of photos to capture per mode (default: 50)
        delay: Delay between captures in seconds (default: 0.5)
    """
    
    print("\n" + "="*60)
    print("  LIVE SAMPLE COLLECTION")
    print("="*60 + "\n")
    
    # Verify person exists in watchlist
    manager = WatchlistManager()
    person_info = manager.get_person_info(person_id)
    
    if person_info is None:
        print(f"✗ Person {person_id} not found in watchlist.")
        print("Please add to watchlist first using: python utils/add_person.py")
        return
    
    print(f"Collecting samples for: {person_info['FullName']}")
    print(f"Person ID: {person_id}")
    print(f"Case: {person_info['CaseID']}")
    print(f"Legal Status: {person_info['LegalStatus']}\n")
    
    # Create directories
    images_base = os.path.join(config.DATA_DIR, "images", person_id)
    normal_dir = os.path.join(images_base, "normal")
    masked_dir = os.path.join(images_base, "masked")
    
    os.makedirs(normal_dir, exist_ok=True)
    os.makedirs(masked_dir, exist_ok=True)
    
    print(f"Images will be saved to: {images_base}\n")
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("✗ Cannot access webcam. Please check camera connection.")
        return
    
    # Set camera resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    print("="*60)
    print("  PHASE 1: NORMAL FACE CAPTURE")
    print("="*60)
    print("\nInstructions:")
    print("  • Look directly at the camera")
    print("  • Slowly rotate your head left and right")
    print("  • Move slightly closer and farther")
    print("  • Tilt head up and down slightly")
    print("  • Maintain good lighting on face")
    print("  • Press 'q' to stop early\n")
    
    input("Press ENTER to start NORMAL face capture...")
    
    # ========== NORMAL FACE CAPTURE ==========
    img_id = 0
    frame_count = 0
    capture_interval = int(30 * delay)  # Capture every N frames
    
    while img_id < count:
        ret, frame = cap.read()
        
        if not ret:
            print("[WARNING] Frame not captured. Retrying...")
            continue
        
        frame_count += 1
        
        # Capture at intervals
        if frame_count % capture_interval == 0:
            img_id += 1
            filename = f"{person_id}_normal_{img_id:03d}.jpg"
            filepath = os.path.join(normal_dir, filename)
            cv2.imwrite(filepath, frame)
            print(f"[CAPTURED] Normal face: {img_id}/{count}")
        
        # Display with instructions
        display_frame = frame.copy()
        
        # Progress bar
        bar_width = 400
        bar_height = 20
        bar_x = (display_frame.shape[1] - bar_width) // 2
        bar_y = 30
        
        progress = int((img_id / count) * bar_width)
        
        # Background
        cv2.rectangle(display_frame, (bar_x, bar_y), 
                     (bar_x + bar_width, bar_y + bar_height),
                     (50, 50, 50), -1)
        
        # Progress fill
        cv2.rectangle(display_frame, (bar_x, bar_y),
                     (bar_x + progress, bar_y + bar_height),
                     (0, 255, 0), -1)
        
        # Text
        text = f"NORMAL FACE: {img_id}/{count}"
        cv2.putText(display_frame, text, (bar_x, bar_y - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Instructions
        instructions = [
            "Slowly move your head:",
            "LEFT - RIGHT - UP - DOWN",
            "Press 'q' to stop"
        ]
        
        for i, instruction in enumerate(instructions):
            cv2.putText(display_frame, instruction,
                       (10, display_frame.shape[0] - 80 + (i * 25)),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.imshow("Live Sample Collection", display_frame)
        
        key = cv2.waitKey(1)
        if key == ord('q'):
            print("\n[INFO] User stopped normal face collection.")
            break
    
    print(f"\n✓ Collected {img_id} NORMAL face images.\n")
    
    # ========== MASKED/OCCLUDED FACE CAPTURE ==========
    print("="*60)
    print("  PHASE 2: MASKED/OCCLUDED FACE CAPTURE")
    print("="*60)
    print("\nInstructions:")
    print("  • WEAR A MASK or partial face covering")
    print("  • Again, slowly rotate head in all directions")
    print("  • Try different occlusion levels if possible")
    print("  • Press 'q' to stop early\n")
    
    input("Press ENTER when MASK is on to start capture...")
    
    img_id = 0
    frame_count = 0
    
    while img_id < count:
        ret, frame = cap.read()
        
        if not ret:
            print("[WARNING] Frame not captured. Retrying...")
            continue
        
        frame_count += 1
        
        # Capture at intervals
        if frame_count % capture_interval == 0:
            img_id += 1
            filename = f"{person_id}_masked_{img_id:03d}.jpg"
            filepath = os.path.join(masked_dir, filename)
            cv2.imwrite(filepath, frame)
            print(f"[CAPTURED] Masked face: {img_id}/{count}")
        
        # Display with instructions
        display_frame = frame.copy()
        
        # Progress bar
        progress = int((img_id / count) * bar_width)
        
        # Background
        cv2.rectangle(display_frame, (bar_x, bar_y),
                     (bar_x + bar_width, bar_y + bar_height),
                     (50, 50, 50), -1)
        
        # Progress fill (orange for masked)
        cv2.rectangle(display_frame, (bar_x, bar_y),
                     (bar_x + progress, bar_y + bar_height),
                     (0, 165, 255), -1)
        
        # Text
        text = f"MASKED FACE: {img_id}/{count}"
        cv2.putText(display_frame, text, (bar_x, bar_y - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
        
        # Instructions
        instructions = [
            "Keep mask on!",
            "Rotate head in all directions",
            "Press 'q' to stop"
        ]
        
        for i, instruction in enumerate(instructions):
            cv2.putText(display_frame, instruction,
                       (10, display_frame.shape[0] - 80 + (i * 25)),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.imshow("Live Sample Collection", display_frame)
        
        key = cv2.waitKey(1)
        if key == ord('q'):
            print("\n[INFO] User stopped masked face collection.")
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"\n✓ Collected {img_id} MASKED face images.")
    
    # Summary
    print("\n" + "="*60)
    print("✓ SAMPLE COLLECTION COMPLETE")
    print("="*60)
    print(f"Person ID: {person_id}")
    print(f"Total Images Collected: {img_id * 2}")
    print(f"  - Normal: {os.path.join(normal_dir, '*.jpg')}")
    print(f"  - Masked: {os.path.join(masked_dir, '*.jpg')}")
    print("\nNext step:")
    print("  Run: python utils/build_embeddings.py")
    print("  This will process all images and build the recognition database.\n")


def interactive_sample_collection():
    """Interactive CLI for sample collection."""
    print("\n" + "="*60)
    print("  LIVE SAMPLE COLLECTION - INTERACTIVE MODE")
    print("="*60 + "\n")
    
    # Load watchlist
    manager = WatchlistManager()
    persons = manager.get_all_persons()
    
    if not persons:
        print("✗ No persons in watchlist.")
        print("Please add persons first using: python utils/add_person.py")
        return
    
    print(f"Watchlist ({len(persons)} persons):\n")
    for i, person in enumerate(persons, 1):
        print(f"  {i}. {person['PersonID']} - {person['FullName']}")
        print(f"     Case: {person['CaseID']} | Status: {person['LegalStatus']}")
    
    print()
    
    # Select person
    while True:
        try:
            choice = int(input("Select person to collect samples for (number): "))
            if 1 <= choice <= len(persons):
                person_id = persons[choice - 1]['PersonID']
                break
        except ValueError:
            pass
        print("Invalid choice. Try again.")
    
    # Ask for count
    print()
    count_input = input(f"Number of photos per mode (default: 50): ").strip()
    count = int(count_input) if count_input else 50
    
    # Confirm
    print("\n" + "-"*60)
    print(f"Person: {person_id}")
    print(f"Photos per mode: {count}")
    print(f"Total photos: {count * 2} (normal + masked)")
    print(f"Estimated time: ~{int(count * 0.5 / 60)} minutes")
    print("-"*60 + "\n")
    
    confirm = input("Start sample collection? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        collect_live_samples(person_id, count=count)
    else:
        print("Cancelled.")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Command line mode: python collect_samples.py POI-2025-001
        person_id = sys.argv[1]
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        collect_live_samples(person_id, count)
    else:
        # Interactive mode
        interactive_sample_collection()