"""
mongo_setup.py
MongoDB Atlas setup helper for Austin Animal Shelter Big Data Project
Run this FIRST before the notebook to verify your connection.
"""

from pymongo import MongoClient
import os, sys

# ── PASTE YOUR ATLAS URI HERE ─────────────────────────────────────────────────
# Get it from: MongoDB Atlas → Your Cluster → Connect → Drivers → Python
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://siripi:Chandu143@bigdata.rtntt9l.mongodb.net/?appName=bigdata"
)

def test_connection():
    print("🔌 Testing MongoDB Atlas connection...")
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=8000)
        client.admin.command("ping")
        print("✅ Connected to MongoDB Atlas!")

        db = client["austin_animal_shelter"]
        print(f"📦 Database: {db.name}")

        # List existing collections
        cols = db.list_collection_names()
        print(f"📋 Existing collections: {cols if cols else '(empty — ready for ingestion)'}")
        client.close()
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n📝 TROUBLESHOOTING:")
        print("  1. Replace <USERNAME>, <PASSWORD>, <CLUSTER> in MONGO_URI above")
        print("  2. In Atlas → Network Access → Add your current IP (or 0.0.0.0/0 for dev)")
        print("  3. In Atlas → Database Access → ensure user has readWrite role")
        return False

def drop_all_collections():
    """Use with caution — resets the entire database."""
    client = MongoClient(MONGO_URI)
    db = client["austin_animal_shelter"]
    for col in db.list_collection_names():
        db[col].drop()
        print(f"🗑  Dropped: {col}")
    client.close()
    print("✅ All collections dropped. Ready for fresh ingestion.")

if __name__ == "__main__":
    ok = test_connection()
    sys.exit(0 if ok else 1)
