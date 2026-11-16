
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

# 3. Retrieve actual songs from MongoDB
songs = list(db.songs.find({}, {"_id": 0}))

rows = []

# 4. Transform each MongoDB document into a CSV row
for song in songs:

    row = {
        "song_id": song.get("song_id"),
        "title": song.get("title"),
        "artist_names": json.dumps(song.get("artist_names", [])),
        "album": song.get("album"),
        "popularity": song.get("popularity"),
        "duration_ms": song.get("duration_ms"),
        "explicit": song.get("explicit"),
        "genres": json.dumps(song.get("genres", []))
    }

    # Flatten nested audio_features
    audio_features = song.get("audio_features", {})

    for feature, value in audio_features.items():
        row[feature] = value

    rows.append(row)

# 5. Convert rows into a DataFrame
df = pd.DataFrame(rows)

# 6. Export to CSV
output_path = EXPORT_DIR / "songs.csv"

df.to_csv(
    output_path,
    index=False,
    encoding="utf-8"
)

print("Songs export completed!")
print("Total exported songs:", len(df))
print("Number of CSV columns:", len(df.columns))
print("Output:", output_path)

client.close()
