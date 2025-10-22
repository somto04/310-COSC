import os, json, pandas as pd

# Folder that holds your movie subfolders
DATA_DIR = os.path.dirname(__file__)
movies, reviews, users = [], [], []
user_ids = {}
movie_id = 1
review_id = 1
user_id = 1

print("Looking in:", os.path.abspath(DATA_DIR))
if not os.path.exists(DATA_DIR):
    print("That folder doesn't exist!")
else:
    print("Folder found, contains:", os.listdir(DATA_DIR))

# loop through subfolders
for folder in os.listdir(DATA_DIR):
    path = os.path.join(DATA_DIR, folder)
    meta_path = os.path.join(path, "metadata.json")
    reviews_path = os.path.join(path, "movieReviews.csv")

    # skip files like import_data.py or movies.json
    if not os.path.isdir(path):
        continue

    print(f"Checking folder: {folder}")
    print("  metadata.json exists:", os.path.exists(meta_path))
    print("  movieReviews.csv exists:", os.path.exists(reviews_path))

    if not os.path.exists(meta_path):
        continue

    #read metadata
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    movies.append({
        "id": movie_id,
        "title": meta.get("title"),
        "movieIMDbRating": meta.get("movieIMDbRating"),
        "movieGenres": meta.get("movieGenres"),
        "directors": meta.get("directors"),
        "mainStars": meta.get("mainStars"),
        "description": meta.get("description"),
        "datePublished": meta.get("datePublished"),
        "duration": meta.get("duration")
    })

    #read reviews
    if os.path.exists(reviews_path):
        df = pd.read_csv(reviews_path)
        for _, row in df.iterrows():
            username = str(row.get("User", "Unknown")).strip()
            if username not in user_ids:
                user_ids[username] = user_id
                users.append({"id": user_id, "username": username})
                user_id += 1

            reviews.append({
                "id": review_id,
                "movie_id": movie_id,
                "user_id": user_ids[username],
                "review_title": row.get("Review Title"),
                "review_text": row.get("Review"),
                "rating": row.get("User's Rating out of 10"),
                "date_posted": row.get("Date of Review")
            })
            review_id += 1

    movie_id += 1

#save all three JSON files i think lolsss
#save directly into the same folder as this script
output_dir = DATA_DIR
with open(os.path.join(output_dir, "movies.json"), "w", encoding="utf-8") as f:
    json.dump(movies, f, indent=2)
with open(os.path.join(output_dir, "reviews.json"), "w", encoding="utf-8") as f:
    json.dump(reviews, f, indent=2)
with open(os.path.join(output_dir, "users.json"), "w", encoding="utf-8") as f:
    json.dump(users, f, indent=2)

print(f"Movies processed: {len(movies)}")
print(f"Reviews processed: {len(reviews)}")
print(f"Users processed: {len(users)}")
print("Exported JSON files: movies.json, reviews.json, users.json")
