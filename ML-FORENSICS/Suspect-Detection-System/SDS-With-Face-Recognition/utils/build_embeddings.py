"""
Utility: Build Embeddings Database
Processes all watchlist images and creates embeddings
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from core.watchlist import WatchlistManager


def build_embeddings():
    """Build embeddings database from images directory."""
    print("\n" + "="*60)
    print("  BUILD EMBEDDINGS DATABASE")
    print("="*60 + "\n")
    
    manager = WatchlistManager()
    
    # Define images directory
    images_dir = os.path.join(config.DATA_DIR, "images")
    
    print(f"Looking for images in: {images_dir}\n")
    
    if not os.path.exists(images_dir):
        print(f"Creating images directory: {images_dir}")
        os.makedirs(images_dir, exist_ok=True)
        print("\nDirectory created. Please organize images as:")
        print(f"  {images_dir}/")
        print(f"    PersonID_1/")
        print(f"      image1.jpg")
        print(f"      image2.jpg")
        print(f"    PersonID_2/")
        print(f"      image1.jpg")
        print("\nRun this script again after adding images.")
        return
    
    # Check if there are any subdirectories
    person_dirs = [d for d in os.listdir(images_dir) 
                  if os.path.isdir(os.path.join(images_dir, d))]
    
    if not person_dirs:
        print("No person directories found in images directory.")
        print("\nPlease organize images as:")
        print(f"  {images_dir}/")
        print(f"    PersonID_1/")
        print(f"      image1.jpg")
        return
    
    print(f"Found {len(person_dirs)} person directories:")
    for person_dir in person_dirs:
        print(f"  - {person_dir}")
    
    confirm = input("\nBuild embeddings database? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        print("\nBuilding embeddings database...")
        print("This may take a few minutes...\n")
        
        try:
            embeddings_data = manager.build_embeddings_database(images_dir)
            
            if embeddings_data:
                print("\n" + "="*60)
                print("✓ EMBEDDINGS DATABASE BUILT SUCCESSFULLY!")
                print("="*60)
                print(f"Total Embeddings: {embeddings_data['total_embeddings']}")
                print(f"Total Persons: {embeddings_data['total_persons']}")
                print(f"Saved to: {config.EMBEDDINGS_FILE}")
                print("\nYou can now start the detection system!")
            else:
                print("\n✗ Failed to build embeddings database.")
                
        except Exception as e:
            print(f"\n✗ Error: {e}")
    else:
        print("\nCancelled.")


if __name__ == "__main__":
    build_embeddings()