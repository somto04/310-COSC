import json, os

path = os.path.join(os.path.dirname(__file__), "replies.json")

with open(path, "r", encoding="utf-8") as f:
    replies = json.load(f)

cleaned = []
nextId = 1

for r in replies:
    try:
        # try to force ID to int (if already numeric)
        r["id"] = int(r["id"])
    except Exception:
        # assign a new int ID if UUID
        r["id"] = nextId
        nextId += 1

    # convert other fields to int where possible
    try:
        r["reviewId"] = int(r["reviewId"])
    except Exception:
        pass
    try:
        r["userId"] = int(r["userId"])
    except Exception:
        pass

    cleaned.append(r)

with open(path, "w", encoding="utf-8") as f:
    json.dump(cleaned, f, indent=2)

print(f" Cleaned {len(cleaned)} replies and converted IDs to integers.")
