
from pymongo import MongoClient
from pathlib import Path
import pandas as pd
import json

# 1. Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPORT_DIR = PROJECT_ROOT / "exports"
EXPORT_DIR.mkdir(exist_ok=True)

# 2. Connect to MongoDB
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")

client = MongoClient(
    f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin"
)

db = client["soundhub"]

# 3. Retrieve users from MongoDB
users = list(db.users.find({}, {"_id": 0}))

rows = []

# 4. Prepare users for CSV
for user in users:
    row = {
        "user_id": user.get("user_id"),
        "username": user.get("username"),
        "email": user.get("email"),
        "country": user.get("country"),
        "favorite_genres": json.dumps(
            user.get("favorite_genres", [])
        )
    }

    rows.append(row)

# 5. Create DataFrame
df = pd.DataFrame(rows)

# 6. Export CSV
output_path = EXPORT_DIR / "users.csv"

df.to_csv(
    output_path,
    index=False,
    encoding="utf-8"
)

print("Users export completed!")
print("Total exported users:", len(df))
print("Output:", output_path)

client.close()
