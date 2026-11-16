
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
ratings_collection = db["ratings"]

ratings = {}

print("Reading ratings data...")

with open(CSV_PATH, "r", encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        rating_id = row["rating_id"].strip()

        if not rating_id:
            continue

        rating = {
            "rating_id": rating_id,
            "user_id": row["user_id"].strip(),
            "song_id": row["track_id"].strip(),
            "rating": int(row["rating"])
        }

        ratings[rating_id] = rating

print(f"Found {len(ratings)} unique ratings.")

# Prepare MongoDB operations
operations = [
    UpdateOne(
        {"rating_id": rating["rating_id"]},
        {"$set": rating},
        upsert=True
    )
    for rating in ratings.values()
]

# Import in batches
BATCH_SIZE = 1000

for i in range(0, len(operations), BATCH_SIZE):
    batch = operations[i:i + BATCH_SIZE]

    ratings_collection.bulk_write(batch, ordered=False)

    print(
        f"Imported {min(i + BATCH_SIZE, len(operations))}"
        f" / {len(operations)}"
    )

print("\nRatings import completed!")
print("Total ratings in MongoDB:", ratings_collection.count_documents({}))

client.close()
