import json
from pathlib import Path

DATA_FILE = Path(__file__).parent / "reviews.json"


with open(DATA_FILE, "r", encoding="utf-8") as f:
    reviews = json.load(f)

normalized = []
for r in reviews:
    normalized.append({
        "id": str(r.get("id")),
        "movieId": int(r.get("movieId") or r.get("movie_id") or 0),
        "userId": int(r.get("userId") or r.get("user_id") or 0),
        "reviewTitle": r.get("reviewTitle") or r.get("review_title") or "",
        "reviewBody": r.get("reviewBody") or r.get("review_text") or "",
        "rating": str(r.get("rating") or "").strip(),
        "datePosted": r.get("datePosted") or r.get("date_posted") or "",
    })

with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(normalized, f, indent=2, ensure_ascii=False)

print(f"Normalized {len(normalized)} reviews to camelCase.")
