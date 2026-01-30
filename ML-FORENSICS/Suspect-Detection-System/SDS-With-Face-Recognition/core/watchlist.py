"""
Watchlist Management Module
Manages suspect database with legal status and risk levels
"""

import os
import pandas as pd
import pickle
import numpy as np
from datetime import datetime
import hashlib
import cv2
from insightface.app import FaceAnalysis
import config

class WatchlistManager:
    """Manages watchlist database and embeddings."""
    
    REQUIRED_COLUMNS = [
        "PersonID",
        "CaseID", 
        "FullName",
        "RiskLevel",
        "LegalStatus",
        "AuthorizedAgency",
        "DateAdded",
        "AddedBy",
        "Notes",
        "LastDetected"
    ]
    
    def __init__(self):
        self.csv_file = config.WATCHLIST_CSV
        self.embeddings_file = config.EMBEDDINGS_FILE
        self.face_analyzer = None
        self._initialize_csv()
    
    def _initialize_csv(self):
        """Create watchlist CSV with proper headers if it doesn't exist."""
        if not os.path.exists(self.csv_file):
            df = pd.DataFrame(columns=self.REQUIRED_COLUMNS)
            df.to_csv(self.csv_file, index=False, encoding='utf-8')
            print(f"[INIT] Created new watchlist: {self.csv_file}")
        else:
            # Validate existing CSV
            try:
                df = pd.read_csv(self.csv_file, encoding='utf-8')
                missing_cols = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
                if missing_cols:
                    print(f"[WARNING] Missing columns: {missing_cols}. Reinitializing.")
                    for col in missing_cols:
                        df[col] = ""
                    df.to_csv(self.csv_file, index=False, encoding='utf-8')
            except Exception as e:
                print(f"[ERROR] CSV validation failed: {e}")
    
    def _init_face_analyzer(self):
        """Lazy initialization of face analyzer."""
        if self.face_analyzer is None:
            print("[INIT] Loading InsightFace model...")
            self.face_analyzer = FaceAnalysis(name=config.FACE_DETECTION_MODEL)
            ctx_id = 0 if config.GPU_ENABLED else -1
            self.face_analyzer.prepare(ctx_id=ctx_id)
            print("[INIT] Face analyzer ready.")
    
    def add_person(self, person_id, case_id, full_name, risk_level, legal_status, 
                   authorized_agency, added_by, notes=""):
        """
        Add a new person to the watchlist.
        
        Args:
            person_id: Unique identifier for the person
            case_id: Associated case number
            full_name: Full name of the person
            risk_level: CRITICAL, HIGH, MEDIUM, LOW, REVIEW
            legal_status: WANTED, POI, MISSING, WITNESS, UNDER_INVESTIGATION
            authorized_agency: Agency authorized to access this record
            added_by: Officer/investigator who added the record
            notes: Additional context
        """
        # Validation
        if risk_level.upper() not in config.RISK_LEVELS:
            raise ValueError(f"Invalid risk level: {risk_level}")
        
        if legal_status.upper() not in config.LEGAL_STATUS_TYPES:
            raise ValueError(f"Invalid legal status: {legal_status}")
        
        if not config.is_authorized_agency(authorized_agency):
            raise ValueError(f"Unauthorized agency: {authorized_agency}")
        
        df = pd.read_csv(self.csv_file, encoding='utf-8')
        
        # Check for duplicates
        if person_id in df["PersonID"].values:
            print(f"[WARNING] Person {person_id} already exists in watchlist.")
            return False
        
        new_row = {
            "PersonID": person_id,
            "CaseID": case_id,
            "FullName": full_name,
            "RiskLevel": risk_level.upper(),
            "LegalStatus": legal_status.upper(),
            "AuthorizedAgency": authorized_agency,
            "DateAdded": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "AddedBy": added_by,
            "Notes": notes,
            "LastDetected": ""
        }
        
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(self.csv_file, index=False, encoding='utf-8')
        
        print(f"[WATCHLIST] Added: {person_id} - {full_name} ({legal_status}, {risk_level})")
        self._log_audit("ADD_PERSON", person_id, added_by)
        return True
    
    def remove_person(self, person_id, removed_by, reason):
        """Remove a person from the watchlist (with audit trail)."""
        df = pd.read_csv(self.csv_file, encoding='utf-8')
        
        if person_id not in df["PersonID"].values:
            print(f"[WARNING] Person {person_id} not found in watchlist.")
            return False
        
        df = df[df["PersonID"] != person_id]
        df.to_csv(self.csv_file, index=False, encoding='utf-8')
        
        print(f"[WATCHLIST] Removed: {person_id}")
        self._log_audit("REMOVE_PERSON", person_id, removed_by, reason)
        return True
    
    def update_last_detected(self, person_id):
        """Update the last detected timestamp for a person."""
        df = pd.read_csv(self.csv_file, encoding='utf-8')
        
        if person_id in df["PersonID"].values:
            df.loc[df["PersonID"] == person_id, "LastDetected"] = \
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df.to_csv(self.csv_file, index=False, encoding='utf-8')
    
    def get_person_info(self, person_id):
        """Retrieve full information for a person."""
        df = pd.read_csv(self.csv_file, encoding='utf-8')
        person = df[df["PersonID"] == person_id]
        
        if person.empty:
            return None
        
        return person.iloc[0].to_dict()
    
    def get_all_persons(self):
        """Get all persons in the watchlist."""
        df = pd.read_csv(self.csv_file, encoding='utf-8')
        return df.to_dict('records')
    
    def extract_embeddings_from_images(self, person_id, image_dir):
        """
        Extract face embeddings from a directory of images for a person.
        
        Args:
            person_id: Person identifier
            image_dir: Directory containing images of the person
        
        Returns:
            List of embeddings
        """
        self._init_face_analyzer()
        
        embeddings = []
        processed_count = 0
        
        if not os.path.exists(image_dir):
            print(f"[ERROR] Directory not found: {image_dir}")
            return embeddings
        
        image_files = [f for f in os.listdir(image_dir) 
                      if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        for img_file in image_files:
            img_path = os.path.join(image_dir, img_file)
            
            try:
                img = cv2.imread(img_path)
                if img is None:
                    print(f"[WARNING] Could not read: {img_path}")
                    continue
                
                faces = self.face_analyzer.get(img)
                
                if len(faces) == 0:
                    print(f"[WARNING] No face detected in: {img_file}")
                    continue
                
                if len(faces) > 1:
                    print(f"[WARNING] Multiple faces in: {img_file}. Using largest.")
                
                # Use the face with largest bounding box
                largest_face = max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
                embeddings.append(largest_face.embedding)
                processed_count += 1
                
                print(f"[EMBEDDING] Processed: {img_file}")
                
            except Exception as e:
                print(f"[ERROR] Failed to process {img_file}: {e}")
        
        print(f"[EMBEDDING] Extracted {processed_count} embeddings for {person_id}")
        return embeddings
    
    def build_embeddings_database(self, images_base_dir):
        """
        Build embeddings database from organized image directory.
        
        Expected structure:
        images_base_dir/
            person_id_1/
                normal/
                    image1.jpg
                    image2.jpg
                masked/
                    image1.jpg
                    image2.jpg
            person_id_2/
                normal/
                    image1.jpg
                masked/
                    image1.jpg
        
        Returns:
            Dictionary with embeddings and metadata
        """
        self._init_face_analyzer()
        
        all_embeddings = []
        all_person_ids = []
        person_embedding_counts = {}
        
        if not os.path.exists(images_base_dir):
            print(f"[ERROR] Images directory not found: {images_base_dir}")
            return None
        
        # Get list of persons from watchlist
        df = pd.read_csv(self.csv_file, encoding='utf-8')
        
        for person_dir in os.listdir(images_base_dir):
            person_path = os.path.join(images_base_dir, person_dir)
            
            if not os.path.isdir(person_path):
                continue
            
            person_id = person_dir
            
            # Verify person exists in watchlist
            if person_id not in df["PersonID"].values:
                print(f"[WARNING] {person_id} not in watchlist. Skipping.")
                continue
            
            # Check for normal and masked subdirectories
            normal_dir = os.path.join(person_path, "normal")
            masked_dir = os.path.join(person_path, "masked")
            
            # Process normal images
            if os.path.exists(normal_dir):
                embeddings = self.extract_embeddings_from_images(person_id, normal_dir)
                if embeddings:
                    all_embeddings.extend(embeddings)
                    all_person_ids.extend([person_id] * len(embeddings))
                    person_embedding_counts[person_id] = person_embedding_counts.get(person_id, 0) + len(embeddings)
            
            # Process masked images
            if os.path.exists(masked_dir):
                embeddings = self.extract_embeddings_from_images(person_id, masked_dir)
                if embeddings:
                    all_embeddings.extend(embeddings)
                    all_person_ids.extend([person_id] * len(embeddings))
                    person_embedding_counts[person_id] = person_embedding_counts.get(person_id, 0) + len(embeddings)
            
            # If no subdirectories, process images directly in person folder (backward compatibility)
            if not os.path.exists(normal_dir) and not os.path.exists(masked_dir):
                embeddings = self.extract_embeddings_from_images(person_id, person_path)
                if embeddings:
                    all_embeddings.extend(embeddings)
                    all_person_ids.extend([person_id] * len(embeddings))
                    person_embedding_counts[person_id] = len(embeddings)
        
        if not all_embeddings:
            print("[ERROR] No embeddings extracted.")
            return None
        
        # Save embeddings
        embeddings_data = {
            "embeddings": np.array(all_embeddings),
            "person_ids": all_person_ids,
            "person_counts": person_embedding_counts,
            "model": config.FACE_DETECTION_MODEL,
            "created_at": datetime.now().isoformat(),
            "total_embeddings": len(all_embeddings),
            "total_persons": len(person_embedding_counts)
        }
        
        with open(self.embeddings_file, "wb") as f:
            pickle.dump(embeddings_data, f)
        
        print(f"[SUCCESS] Embeddings database created:")
        print(f"  - Total embeddings: {len(all_embeddings)}")
        print(f"  - Total persons: {len(person_embedding_counts)}")
        for person_id, count in person_embedding_counts.items():
            print(f"    • {person_id}: {count} embeddings")
        print(f"  - Saved to: {self.embeddings_file}")
        
        self._log_audit("BUILD_EMBEDDINGS", "SYSTEM", "SYSTEM", 
                       f"Built database with {len(all_embeddings)} embeddings")
        
        return embeddings_data
    
    def load_embeddings(self):
        """Load embeddings database."""
        if not os.path.exists(self.embeddings_file):
            print(f"[ERROR] Embeddings file not found: {self.embeddings_file}")
            return None
        
        try:
            with open(self.embeddings_file, "rb") as f:
                data = pickle.load(f)
            
            print(f"[LOADED] Embeddings database:")
            print(f"  - Total embeddings: {data['total_embeddings']}")
            print(f"  - Total persons: {data['total_persons']}")
            print(f"  - Created: {data['created_at']}")
            
            return data
        except Exception as e:
            print(f"[ERROR] Failed to load embeddings: {e}")
            return None
    
    def _log_audit(self, action, person_id, performed_by, details=""):
        """Log audit trail for watchlist operations."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "person_id": person_id,
            "performed_by": performed_by,
            "details": details
        }
        
        with open(config.AUDIT_LOG, "a") as f:
            f.write(f"{log_entry}\n")


# ==================== STANDALONE UTILITIES ====================

def create_sample_watchlist():
    """Create a sample watchlist for testing (DEMO ONLY)."""
    manager = WatchlistManager()
    
    sample_persons = [
        {
            "person_id": "POI-2025-001",
            "case_id": "CASE-2025-001", 
            "full_name": "John Doe",
            "risk_level": "HIGH",
            "legal_status": "WANTED",
            "authorized_agency": "LAW_ENFORCEMENT",
            "added_by": "Officer Smith",
            "notes": "Suspected involvement in robbery case"
        },
        {
            "person_id": "POI-2025-002",
            "case_id": "CASE-2025-002",
            "full_name": "Jane Smith", 
            "risk_level": "MEDIUM",
            "legal_status": "POI",
            "authorized_agency": "FORENSIC_INVESTIGATOR",
            "added_by": "Detective Johnson",
            "notes": "Person of interest in fraud investigation"
        }
    ]
    
    for person in sample_persons:
        manager.add_person(**person)
    
    print("[DEMO] Sample watchlist created.")


if __name__ == "__main__":
    # Demo usage
    create_sample_watchlist()