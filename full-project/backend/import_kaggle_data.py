import os
import json
import pandas as pd
import sqlite3

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = "spoileralert.db"

def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT UNIQUE,
        imdb_rating REAL,
        total_rating_count INTEGER,
        total_user_reviews TEXT,
        total_critic_reviews TEXT,
        metascore TEXT,
        genres TEXT,
        directors TEXT,
        creators TEXT,
        main_stars TEXT,
        description TEXT,
        date_published TEXT,
        duration INTEGER,
        metadata_json TEXT
    );

    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        movie_id INTEGER,
        reviewer TEXT,
        review_title TEXT,
        review_text TEXT,
        user_rating REAL,
        usefulness_vote INTEGER,
        total_votes INTEGER,
        date_posted TEXT,
        FOREIGN KEY(movie_id) REFERENCES movies(id)
    );
    """)
    con.commit()
    return con, cur


def import_movie(folder, cur):
    metadata_path = os.path.join(folder, "metadata.json")
    reviews_path = os.path.join(folder, "movieReviews.csv")

    # Load metadata.json
    with open(metadata_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    title = meta.get("title", os.path.basename(folder))
    imdb_rating = meta.get("movieIMDbRating")
    total_rating_count = meta.get("totalRatingCount")
    total_user_reviews = meta.get("totalUserReviews")
    total_critic_reviews = meta.get("totalCriticReviews")
    metascore = meta.get("metaScore")
    genres = ", ".join(meta.get("movieGenres", []))
    directors = ", ".join(meta.get("directors", []))
    creators = ", ".join(meta.get("creators", []))
    main_stars = ", ".join(meta.get("mainStars", []))
    description = meta.get("description")
    date_published = meta.get("datePublished")
    duration = meta.get("duration")

    # Insert movie if not already present
    cur.execute("""
        INSERT OR IGNORE INTO movies (
            title, imdb_rating, total_rating_count, total_user_reviews,
            total_critic_reviews, metascore, genres, directors, creators,
            main_stars, description, date_published, duration, metadata_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        title, imdb_rating, total_rating_count, total_user_reviews,
        total_critic_reviews, metascore, genres, directors, creators,
        main_stars, description, date_published, duration, json.dumps(meta)
    ))

    cur.execute("SELECT id FROM movies WHERE title = ?", (title,))
    movie_id = cur.fetchone()[0]

    # Import reviews.csv
    if os.path.exists(reviews_path):
        df = pd.read_csv(reviews_path)

        expected_cols = {
            "Date of Review": "date_posted",
            "User": "reviewer",
            "Usefulness Vote": "usefulness_vote",
            "Total Votes": "total_votes",
            "User's Rating out of 10": "user_rating",
            "Review Title": "review_title",
            "Review": "review_text"
        }

        # Clean up missing columns 
        for col in expected_cols.keys():
            if col not in df.columns:
                df[col] = None

        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO reviews (
                    movie_id, reviewer, review_title, review_text,
                    user_rating, usefulness_vote, total_votes, date_posted
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                movie_id,
                row["User"],
                row["Review Title"],
                row["Review"],
                row["User's Rating out of 10"],
                row["Usefulness Vote"],
                row["Total Votes"],
                row["Date of Review"]
            ))

    print(f"✅ Imported {title}")


def main():
    con, cur = init_db()

    print("Looking in:", os.path.abspath(DATA_DIR))
    print("Exists:", os.path.exists(DATA_DIR))
    print("Contents:", os.listdir(DATA_DIR))
    for folder in os.listdir(DATA_DIR):
        movie_path = os.path.join(DATA_DIR, folder)
        if os.path.isdir(movie_path):
            try:
                import_movie(movie_path, cur)
            except Exception as e:
                print(f" Skipped {folder}: {e}")

    con.commit()
    con.close()
    print(f"\n Database saved to {DB_PATH}")


if __name__ == "__main__":
    main()
