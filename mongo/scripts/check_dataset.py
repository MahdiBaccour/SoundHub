
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = PROJECT_ROOT / "imports" / "dataset_soundhub.csv"

df = pd.read_csv(CSV_PATH)

print("Dataset shape:", df.shape)

print("\nMissing values per column:")
print(df.isnull().sum())

print("\nTotal missing values:")
print(df.isnull().sum().sum())

print("\nDuplicate track IDs:")
print(df["track_id"].duplicated().sum())
print("\nRows with missing values:")
print(df[df.isnull().any(axis=1)])

print("\nUnique track IDs:")
print(df["track_id"].nunique())

print("\nMissing track IDs:")
print(df["track_id"].isnull().sum())