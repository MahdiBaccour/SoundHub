
from pymongo import MongoClient
from pathlib import Path
import pandas as pd

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

# 3. Retrieve ratings from MongoDB
ratings = list(db.ratings.find({}, {"_id": 0}))

# 4. Convert documents into rows
rows = []

for rating in ratings:
    row = {
        "rating_id": rating.get("rating_id"),
        "user_id": rating.get("user_id"),
        "song_id": rating.get("song_id"),
        "rating": rating.get("rating")
    }

    rows.append(row)

# 5. Create DataFrame
df = pd.DataFrame(rows)

# 6. Export CSV
output_path = EXPORT_DIR / "ratings.csv"

df.to_csv(
    output_path,
    index=False,
    encoding="utf-8"
)

print("Ratings export completed!")
print("Total exported ratings:", len(df))
print("Output:", output_path)

client.close()
