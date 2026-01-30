"""
Demo Data Initializer
Creates sample watchlist entries for testing (NO REAL DATA)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from core.watchlist import WatchlistManager


def create_demo_watchlist():
    """Create demo watchlist entries for testing."""
    print("\n" + "="*60)
    print("  DEMO WATCHLIST INITIALIZATION")
    print("="*60 + "\n")
    
    print("WARNING: This creates DEMO/TEST data only!")
    print("For production use, add real entries via: python utils/add_person.py\n")
    
    confirm = input("Create demo watchlist? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("Cancelled.")
        return
    
    manager = WatchlistManager()
    
    demo_persons = [
        {
            "person_id": "DEMO-001",
            "case_id": "CASE-DEMO-001",
            "full_name": "Demo Subject Alpha",
            "risk_level": "HIGH",
            "legal_status": "POI",
            "authorized_agency": "SECURITY_OFFICER",
            "added_by": "System Administrator",
            "notes": "Demo entry for testing purposes"
        },
        {
            "person_id": "DEMO-002",
            "case_id": "CASE-DEMO-002",
            "full_name": "Demo Subject Beta",
            "risk_level": "MEDIUM",
            "legal_status": "UNDER_INVESTIGATION",
            "authorized_agency": "FORENSIC_INVESTIGATOR",
            "added_by": "System Administrator",
            "notes": "Demo entry for testing purposes"
        },
        {
            "person_id": "DEMO-003",
            "case_id": "CASE-DEMO-003",
            "full_name": "Demo Subject Gamma",
            "risk_level": "CRITICAL",
            "legal_status": "WANTED",
            "authorized_agency": "LAW_ENFORCEMENT",
            "added_by": "System Administrator",
            "notes": "Demo entry for testing purposes"
        }
    ]
    
    print("\nAdding demo entries...")
    
    for person in demo_persons:
        try:
            success = manager.add_person(**person)
            if success:
                print(f"✓ Added: {person['person_id']}")
            else:
                print(f"✗ Failed: {person['person_id']} (may already exist)")
        except Exception as e:
            print(f"✗ Error adding {person['person_id']}: {e}")
    
    print("\n" + "="*60)
    print("✓ DEMO WATCHLIST CREATED")
    print("="*60)
    print("\nNote: Demo entries will NOT match any faces without training images.")
    print("To test detection:")
    print("1. Place sample face images in: data/images/DEMO-001/")
    print("2. Run: python utils/build_embeddings.py")
    print("3. Start system: python app.py")
    print("")


if __name__ == "__main__":
    create_demo_watchlist()