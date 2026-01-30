"""
Utility: Add Person to Watchlist
Manages watchlist entries and builds embeddings database
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from core.watchlist import WatchlistManager


def interactive_add_person():
    """Interactive CLI for adding a person to the watchlist."""
    print("\n" + "="*60)
    print("  ADD PERSON TO WATCHLIST")
    print("="*60 + "\n")
    
    manager = WatchlistManager()
    
    # Collect information
    print("Enter person details:\n")
    
    person_id = input("Person ID (e.g., POI-2025-001): ").strip()
    case_id = input("Case ID (e.g., CASE-2025-001): ").strip()
    full_name = input("Full Name: ").strip()
    
    # Risk level
    print("\nRisk Level:")
    for i, level in enumerate(config.RISK_LEVELS.keys(), 1):
        print(f"  {i}. {level}")
    
    while True:
        try:
            risk_choice = int(input("Select (1-5): "))
            if 1 <= risk_choice <= 5:
                risk_level = list(config.RISK_LEVELS.keys())[risk_choice - 1]
                break
        except ValueError:
            pass
        print("Invalid choice. Try again.")
    
    # Legal status
    print("\nLegal Status:")
    for i, status in enumerate(config.LEGAL_STATUS_TYPES, 1):
        print(f"  {i}. {status}")
    
    while True:
        try:
            status_choice = int(input("Select (1-5): "))
            if 1 <= status_choice <= 5:
                legal_status = config.LEGAL_STATUS_TYPES[status_choice - 1]
                break
        except ValueError:
            pass
        print("Invalid choice. Try again.")
    
    # Authorized agency
    print("\nAuthorized Agency:")
    for i, agency in enumerate(config.AUTHORIZED_AGENCIES, 1):
        print(f"  {i}. {agency}")
    
    while True:
        try:
            agency_choice = int(input("Select (1-4): "))
            if 1 <= agency_choice <= 4:
                authorized_agency = config.AUTHORIZED_AGENCIES[agency_choice - 1]
                break
        except ValueError:
            pass
        print("Invalid choice. Try again.")
    
    added_by = input("\nAdded by (officer name): ").strip()
    notes = input("Notes (optional): ").strip()
    
    # Confirm
    print("\n" + "-"*60)
    print("CONFIRM DETAILS:")
    print(f"  Person ID: {person_id}")
    print(f"  Case ID: {case_id}")
    print(f"  Name: {full_name}")
    print(f"  Risk Level: {risk_level}")
    print(f"  Legal Status: {legal_status}")
    print(f"  Agency: {authorized_agency}")
    print(f"  Added by: {added_by}")
    if notes:
        print(f"  Notes: {notes}")
    print("-"*60)
    
    confirm = input("\nAdd this person to watchlist? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        try:
            success = manager.add_person(
                person_id=person_id,
                case_id=case_id,
                full_name=full_name,
                risk_level=risk_level,
                legal_status=legal_status,
                authorized_agency=authorized_agency,
                added_by=added_by,
                notes=notes
            )
            
            if success:
                print("\n✓ Person added to watchlist successfully!")
                
                # Ask about images
                has_images = input("\nDo you have images for this person? (yes/no): ").strip().lower()
                
                if has_images == 'yes':
                    print(f"\nPlace images in: {config.DATA_DIR}/images/{person_id}/")
                    print("Then run: python utils/build_embeddings.py")
                
            else:
                print("\nX Failed to add person to watchlist.")
                
        except Exception as e:
            print(f"\nX Error: {e}")
    else:
        print("\nCancelled.")


if __name__ == "__main__":
    interactive_add_person()