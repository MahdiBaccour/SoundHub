
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
users_collection = db["users"]

users = {}

print("Reading user data...")

with open(CSV_PATH, "r", encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        user_id = row["user_id"].strip()

        if not user_id:
            continue

        # Keep only one document per user
        if user_id in users:
            continue

        favorite_genres = [
            genre.strip()
            for genre in row["favorite_genres"].split(";")
            if genre.strip()
        ]

        user = {
            "user_id": user_id,
            "username": row["username"].strip(),
            "email": row["email"].strip(),
            "country": row["country"].strip(),
            "favorite_genres": favorite_genres
        }

        users[user_id] = user

print(f"Found {len(users)} unique users.")

# Prepare MongoDB operations
operations = [
    UpdateOne(
        {"user_id": user["user_id"]},
        {"$set": user},
        upsert=True
    )
    for user in users.values()
]

# Import in batches
BATCH_SIZE = 1000

for i in range(0, len(operations), BATCH_SIZE):
    batch = operations[i:i + BATCH_SIZE]

    users_collection.bulk_write(batch, ordered=False)

    print(
        f"Imported {min(i + BATCH_SIZE, len(operations))}"
        f" / {len(operations)}"
    )

print("\nUsers import completed!")
print("Total users in MongoDB:", users_collection.count_documents({}))

client.close()
