"""Qdrant Collection Setup Script.

This script connects to a Qdrant instance and ensures that the necessary 
collections ('astro_profiles' and 'astro_sessions') exist.

It is designed to be run as a one-time setup task or as part of a deployment
process to prepare the Qdrant database for the Astrologer MCP application.

Environment Variables:
    QDRANT_URL: The URL of the Qdrant instance.
    QDRANT_API_KEY: The API key for authenticating with the Qdrant instance.
"""

import os
import sys
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models

# --- Configuration ---

# Load environment variables from .env file
load_dotenv()

QDRANT_URL = os.environ.get("QDRANT_URL")
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY")

# Define the collections that should exist
REQUIRED_COLLECTIONS = {
    "astro_profiles": models.VectorParams(size=5, distance=models.Distance.COSINE),
    "astro_sessions": models.VectorParams(size=5, distance=models.Distance.COSINE),
}

# --- Main Execution ---

def main():
    """Connects to Qdrant and creates missing collections."""
    
    print("--- Starting Qdrant Collection Setup ---")

    # --- Validate Configuration ---
    if not QDRANT_URL or not QDRANT_API_KEY:
        print("[ERROR] QDRANT_URL and QDRANT_API_KEY must be set in your environment.")
        sys.exit(1)

    # --- Initialize Qdrant Client ---
    try:
        qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        print(f"Successfully connected to Qdrant at: {QDRANT_URL}")
    except Exception as e:
        print(f"[ERROR] Failed to connect to Qdrant: {e}")
        sys.exit(1)

    # --- Ensure Collections Exist ---
    try:
        existing_collections_response = qdrant_client.get_collections()
        existing_collection_names = {
            collection.name for collection in existing_collections_response.collections
        }
        print(f"Found existing collections: {existing_collection_names or 'None'}")
    except Exception as e:
        print(f"[ERROR] Could not retrieve existing collections: {e}")
        sys.exit(1)

    print("\nProcessing required collections...")
    for name, vector_params in REQUIRED_COLLECTIONS.items():
        if name in existing_collection_names:
            print(f"[OK] Collection '{name}' already exists. Skipping.")
        else:
            try:
                qdrant_client.recreate_collection(
                    collection_name=name,
                    vectors_config=vector_params,
                )
                print(f"[OK] Collection '{name}' created successfully.")
            except Exception as e:
                print(f"[ERROR] Failed to create collection '{name}': {e}")

    # --- Final Verification ---
    try:
        final_collections_response = qdrant_client.get_collections()
        final_collection_names = {
            collection.name for collection in final_collections_response.collections
        }
        print("\n--- Verification Complete ---")
        print("Current collections in Qdrant:")
        for name in sorted(final_collection_names):
            print(f"  - {name}")
    except Exception as e:
        print(f"\n[ERROR] Failed to list final collections: {e}")

if __name__ == "__main__":
    main()