import json

path = "app/data/reviews.json"

with open(path, "r", encoding="utf-8") as f:
    reviews = json.load(f)

cleaned = []
nextId = 1

for r in reviews:
    # Skip any invalid entries where rating is not a digit
    ratingStr = str(r.get("rating", "")).strip()
    if not ratingStr.isdigit():
        continue

    # Fix or replace bad IDs
    try:
        r["id"] = int(r["id"])
    except Exception:
        r["id"] = nextId
        nextId += 1

    # Force all numeric fields to int
    r["movieId"] = int(r["movieId"])
    r["userId"] = int(r["userId"])
    r["rating"] = int(r["rating"])
    cleaned.append(r)

with open(path, "w", encoding="utf-8") as f:
    json.dump(cleaned, f, indent=2)

print(f"Cleaned {len(cleaned)} valid reviews saved to {path}")
