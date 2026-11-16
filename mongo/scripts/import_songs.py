
import csv
from pathlib import Path
from pymongo import MongoClient, UpdateOne

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = PROJECT_ROOT / "imports" / "dataset_soundhub.csv"

# MongoDB connection
client = MongoClient(
    "mongodb://admin:soundhub123@localhost:27017/?authSource=admin"
)

db = client["soundhub"]
songs_collection = db["songs"]

songs = {}

print("Reading Spotify dataset...")

with open(CSV_PATH, "r", encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        track_id = row["track_id"].strip()

        if not track_id:
            continue

        genre = row["track_genre"].strip()
        title = row["track_name"].strip() or None
        album = row["album_name"].strip() or None

        artists = [
            artist.strip()
            for artist in row["artists"].split(";")
            if artist.strip()
        ]

        # Handle a song that we have already encountered
        if track_id in songs:
            song = songs[track_id]

            if genre and genre not in song["genres"]:
                song["genres"].append(genre)

            # Recover metadata if a later row contains it
            if not song["title"] and title:
                song["title"] = title

            if not song["album"] and album:
                song["album"] = album

            if not song["artist_names"] and artists:
                song["artist_names"] = artists

            continue

        # Build a new song document
        song = {
            "song_id": track_id,
            "title": title,
            "artist_names": artists,
            "album": album,
            "popularity": int(row["popularity"]),
            "duration_ms": int(row["duration_ms"]),
            "explicit": row["explicit"].lower() == "true",
            "genres": [genre] if genre else [],
            "audio_features": {
                "danceability": float(row["danceability"]),
                "energy": float(row["energy"]),
                "key": int(row["key"]),
                "loudness": float(row["loudness"]),
                "mode": int(row["mode"]),
                "speechiness": float(row["speechiness"]),
                "acousticness": float(row["acousticness"]),
                "instrumentalness": float(row["instrumentalness"]),
                "liveness": float(row["liveness"]),
                "valence": float(row["valence"]),
                "tempo": float(row["tempo"]),
                "time_signature": int(row["time_signature"])
            }
        }

        songs[track_id] = song

print(f"Found {len(songs)} unique songs.")

# Prepare MongoDB operations
operations = [
    UpdateOne(
        {"song_id": song["song_id"]},
        {"$set": song},
        upsert=True
    )
    for song in songs.values()
]

# Import in batches
BATCH_SIZE = 1000

for i in range(0, len(operations), BATCH_SIZE):
    batch = operations[i:i + BATCH_SIZE]

    songs_collection.bulk_write(batch, ordered=False)

    print(
        f"Imported {min(i + BATCH_SIZE, len(operations))}"
        f" / {len(operations)}"
    )

print("\nImport completed!")
print("Total songs in MongoDB:", songs_collection.count_documents({}))

client.close()
