import os, json, pandas as pd

# Folder that holds your movie subfolders
DATA_DIR = os.path.dirname(__file__)
movies, reviews, users = [], [], []
userIds = {}
movieId = 1
reviewId = 1
userId = 1

print("Looking in:", os.path.abspath(DATA_DIR))
if not os.path.exists(DATA_DIR):
    print("That folder doesn't exist!")
else:
    print("Folder found, contains:", os.listdir(DATA_DIR))

# loop through subfolders
for folder in os.listdir(DATA_DIR):
    path = os.path.join(DATA_DIR, folder)
    metaPath = os.path.join(path, "metadata.json")
    reviewsPath = os.path.join(path, "movieReviews.csv")

    # skip files like import_data.py or movies.json
    if not os.path.isdir(path):
        continue

    print(f"Checking folder: {folder}")
    print("  metadata.json exists:", os.path.exists(metaPath))
    print("  movieReviews.csv exists:", os.path.exists(reviewsPath))

    if not os.path.exists(metaPath):
        continue

    #read metadata
    with open(metaPath, "r", encoding="utf-8") as f:
        meta = json.load(f)
    movies.append({
        "id": movieId,
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
    if os.path.exists(reviewsPath):
        df = pd.read_csv(reviewsPath)
        for _, row in df.iterrows():
            username = str(row.get("User", "Unknown")).strip()
            if username not in userIds:
                userIds[username] = userId
                users.append({"id": userId, "username": username})
                userId += 1

            reviews.append({
                "id": reviewId,
                "movie_id": movieId,
                "user_id": userIds[username],
                "review_title": row.get("Review Title"),
                "review_text": row.get("Review"),
                "rating": row.get("User's Rating out of 10"),
                "date_posted": row.get("Date of Review")
            })
            reviewId += 1

    movieId += 1

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
