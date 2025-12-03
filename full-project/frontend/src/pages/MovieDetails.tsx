//this page will show movie details once the user clicks on a movie from the home page. 
//it will fetch movie details from the backend using the movie ID passed in the URL parameters.
//it will also display the reviews correspoinding to that movie.

import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

const API = import.meta.env.VITE_API_URL;

type Movie = {
  id: number;
  tmdbId?: number;
  title: string;
  movieGenres?: string[];
  directors?: string[];
  mainStars?: string[];
  description?: string;
  datePublished?: string;
  duration?: number;
  yearReleased?: number;
};

type TMDbMovie = {
  poster?: string;
  overview?: string;
  runtime?: number;
};

type Review = {
  id: number;
  movieId: number;
  userId: number;
  reviewTitle: string;
  reviewBody: string;
  rating: number;
  datePosted: string;
  flagged: boolean;
};

export default function MovieDetails() {
  const { movieId } = useParams();
  const [movie, setMovie] = useState<Movie | null>(null);
  const [tmdb, setTmdb] = useState<TMDbMovie | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [visibleReviews, setVisibleReviews] = useState<Review[]>([]);
  const [reviewsToShow, setReviewsToShow] = useState(10); // initially show 10 reviews
  const [loading, setLoading] = useState(true);

  const [newTitle, setNewTitle] = useState("");
  const [newBody, setNewBody] = useState("");
  const [posting, setPosting] = useState(false);
  const [error, setError] = useState("");

  // Fetch movie details from backend
  useEffect(() => {
    if (!movieId) return;

    const fetchData = async () => {
      setLoading(true);
      try {
        // Fetch movie info
        const res = await fetch(`${API}/movies/${movieId}`);
        if (!res.ok) throw new Error("Failed to fetch movie");
        const data: Movie = await res.json();
        setMovie(data);

        // Fetch TMDb info (poster, runtime, overview)
        const tmdbRes = await fetch(`${API}/tmdb/details/${movieId}`);
        if (tmdbRes.ok) {
          const tmdbData: TMDbMovie = await tmdbRes.json();
          setTmdb(tmdbData);
        }

        // Fetch reviews by movieId
        const reviewsRes = await fetch(`${API}/reviews/search?query=${movieId}`);
        if (reviewsRes.ok) {
          const reviewsData: Review[] = await reviewsRes.json();
          setReviews(reviewsData);
        }
      } catch (err) {
        console.error(err);
        setError("Error loading movie details");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [movieId]);

  // Update visibleReviews whenever reviews or reviewsToShow changes
  useEffect(() => {
    setVisibleReviews(reviews.slice(0, reviewsToShow));
  }, [reviews, reviewsToShow]);

  // Post a new review
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle || !newBody) return;

    setPosting(true);
    try {
      const token = localStorage.getItem("token"); // Adjust auth method if needed
      const res = await fetch(`${API}/reviews/${movieId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          reviewTitle: newTitle,
          reviewBody: newBody,
          rating: 5, // default until star selection is added
        }),
      });

      if (!res.ok) throw new Error("Failed to post review");
      const created: Review = await res.json();
      setReviews((prev) => [created, ...prev]);
      setNewTitle("");
      setNewBody("");
    } catch (err) {
      console.error(err);
      setError("Failed to post review");
    } finally {
      setPosting(false);
    }
  };

  if (loading) return <p>Loading movie details...</p>;
  if (!movie) return <p>Movie not found</p>;

  return (
    <div style={{ maxWidth: "800px", margin: "0 auto", padding: "2rem" }}>
      <h1>{movie.title}</h1>
      <div style={{ display: "flex", gap: "1rem", marginBottom: "1rem" }}>
        {tmdb?.poster ? (
          <img
            src={tmdb.poster}
            alt={movie.title}
            style={{ width: "200px", objectFit: "cover" }}
          />
        ) : (
          <div
            style={{
              width: "200px",
              height: "300px",
              backgroundColor: "#ccc",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              color: "#666",
            }}
          >
            No Image
          </div>
        )}

        <div>
          <p><strong>Genres:</strong> {movie.movieGenres?.join(", ") || "N/A"}</p>
          <p><strong>Directors:</strong> {movie.directors?.join(", ") || "N/A"}</p>
          <p><strong>Main Stars:</strong> {movie.mainStars?.join(", ") || "N/A"}</p>
          <p><strong>Year:</strong> {movie.yearReleased || "N/A"}</p>
          <p><strong>Duration:</strong> {tmdb?.runtime || movie.duration || "N/A"} min</p>
          <p><strong>Description:</strong> {tmdb?.overview || movie.description || "N/A"}</p>
        </div>
      </div>

      <section style={{ marginTop: "2rem" }}>
        <h2>Reviews</h2>
        {visibleReviews.length === 0 ? (
          <p>No reviews yet. Be the first to review!</p>
        ) : (
          <ul style={{ listStyle: "none", padding: 0 }}>
            {visibleReviews.map((r) => (
              <li
                key={r.id}
                style={{
                  border: "1px solid #ddd",
                  padding: "0.5rem",
                  marginBottom: "0.5rem",
                  borderRadius: "4px",
                }}
              >
                <strong>{r.reviewTitle}</strong> <em>({r.datePosted})</em>
                <p>{r.reviewBody}</p>
              </li>
            ))}
          </ul>
        )}
        {reviewsToShow < reviews.length && (
          <button
            onClick={() => setReviewsToShow(reviewsToShow + 10)}
            style={{ padding: "0.5rem", marginTop: "1rem", cursor: "pointer" }}
          >
            Load More
          </button>
        )}
      </section>

      <section style={{ marginTop: "2rem" }}>
        <h2>Add a Review</h2>
        {error && <p style={{ color: "red" }}>{error}</p>}
        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
          <input
            type="text"
            placeholder="Review Title"
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            required
            style={{ padding: "0.5rem" }}
          />
          <textarea
            placeholder="Write your review..."
            value={newBody}
            onChange={(e) => setNewBody(e.target.value)}
            required
            rows={4}
            style={{ padding: "0.5rem" }}
          />
          <button
            type="submit"
            disabled={posting}
            style={{ padding: "0.5rem", fontWeight: "bold", cursor: "pointer" }}
          >
            {posting ? "Posting..." : "Submit Review"}
          </button>
        </form>
      </section>
    </div>
  );
}
