import json
import os

# Automatically find the path for reviews.json
base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, "reviews.json")

print(f"Looking for: {file_path}")

with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Handle both list or single-object JSON files
if isinstance(data, dict):
    data = [data]

for review in data:
    try:
        # Convert string IDs and rating to int if possible
        review["id"] = int(review["id"])
        review["movieId"] = int(review["movieId"])
        review["userId"] = int(review["userId"])
        if isinstance(review.get("rating"), str) and review["rating"].isdigit():
            review["rating"] = int(review["rating"])
    except Exception as e:
        print(f"⚠️ Skipped one due to error: {e}\n{review}")

# Save back to the same file (pretty formatted)
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("All IDs and ratings successfully converted to integers.")
