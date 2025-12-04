//this page will show movie details once the user clicks on a movie from the home page. 
//it will fetch movie details from the backend using the movie ID passed in the URL parameters.
//it will also display the reviews corresponding to that movie.

import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getToken } from "../utils/auth";

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
  const [loading, setLoading] = useState(true);
  const [reviewsPage, setReviewsPage] = useState(1);
  const [hasMoreReviews, setHasMoreReviews] = useState(false);

  const [newTitle, setNewTitle] = useState("");
  const [newBody, setNewBody] = useState("");
  const [posting, setPosting] = useState(false);
  const [error, setError] = useState("");

  // --- LIKE SYSTEM ---
  const [likedReviewIds, setLikedReviewIds] = useState<number[]>([]);

  const fetchLikedReviews = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) return;

      const res = await fetch(`${API}/likeReview/`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) return;

      const data = await res.json();
      const ids = data.map((item: { id: number }) => item.id);
      setLikedReviewIds(ids);
    } catch (err) {
      console.error("Failed to load liked reviews", err);
    }
  };

  const handleToggleLike = async (reviewId: number) => {
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Please log in to like reviews.");
      return;
    }

    const isLiked = likedReviewIds.includes(reviewId);

    // Optimistic UI
    setLikedReviewIds((prev) =>
      isLiked ? prev.filter((id) => id !== reviewId) : [...prev, reviewId]
    );

    try {
      const method = isLiked ? "DELETE" : "POST";

      const res = await fetch(`${API}/likeReview/${reviewId}`, {
        method,
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) throw new Error("Failed to toggle like");
    } catch (err) {
      console.error(err);

      // Revert UI on failure
      setLikedReviewIds((prev) =>
        isLiked ? [...prev, reviewId] : prev.filter((id) => id !== reviewId)
      );

      alert("Error updating like.");
    }
  };
  
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
      } catch (err) {
        console.error(err);
        setError("Error loading movie details");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    
    // Fetch reviews and liked reviews separately
    fetchReviews(1);
    fetchLikedReviews();
  }, [movieId]);

  // Fetch reviews by page
  const fetchReviews = async (page: number) => {
    try {
      const res = await fetch(
        `${API}/reviews/search?query=${movieId}&page=${page}&limit=10`
      );
      if (!res.ok) throw new Error("Failed to fetch reviews");
      const data: Review[] = await res.json();

      if (page === 1) {
        setReviews(data);
      } else {
        setReviews((prev) => [...prev, ...data]);
      }

      setHasMoreReviews(data.length === 10); // if less than 10, no more pages
    } catch (err) {
      console.error(err);
    }
  };

  // Load more reviews when reviewsPage changes (after page 1)
  useEffect(() => {
    if (reviewsPage === 1) return; // first page already fetched
    fetchReviews(reviewsPage);
  }, [reviewsPage]);

  // Post a new review
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle || !newBody) return;

    setPosting(true);
    try {
      const token = getToken();
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

  // Flag a review as inappropriate
  const handleFlagReview = async (reviewId: number) => {
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`${API}/reviews/${reviewId}/flag`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });
      if (!res.ok) throw new Error("Failed to flag review");

      // Update UI
      setReviews((prev) =>
        prev.map((rev) =>
          rev.id === reviewId ? { ...rev, flagged: true } : rev
        )
      );
    } catch (err) {
      console.error(err);
      alert("Failed to flag review");
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
          <p>
            <strong>Genres:</strong> {movie.movieGenres?.join(", ") || "N/A"}
          </p>
          <p>
            <strong>Directors:</strong> {movie.directors?.join(", ") || "N/A"}
          </p>
          <p>
            <strong>Main Stars:</strong> {movie.mainStars?.join(", ") || "N/A"}
          </p>
          <p>
            <strong>Year:</strong> {movie.yearReleased || "N/A"}
          </p>
          <p>
            <strong>Duration:</strong> {tmdb?.runtime || movie.duration || "N/A"}{" "}
            min
          </p>
          <p>
            <strong>Description:</strong> {tmdb?.overview || movie.description || "N/A"}
          </p>
        </div>
      </div>

      <section style={{ marginTop: "2rem" }}>
        <h2>Add a Review</h2>
        {error && <p style={{ color: "red" }}>{error}</p>}
        <form
          onSubmit={handleSubmit}
          style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}
        >
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

      <section style={{ marginTop: "2rem" }}>
        <h2>Reviews</h2>
        {reviews.length === 0 ? (
          <p>No reviews yet. Be the first to review!</p>
        ) : (
          <ul style={{ listStyle: "none", padding: 0 }}>
            {reviews.map((r) => {
              const isLiked = likedReviewIds.includes(r.id);
              
              return (
                <li
                  key={r.id}
                  style={{
                    border: "1px solid #ddd",
                    padding: "0.5rem",
                    marginBottom: "0.5rem",
                    borderRadius: "4px",
                  }}
                >
                  {/* Like button */}
                  <button
                    onClick={() => handleToggleLike(r.id)}
                    style={{
                      padding: "0.25rem 0.5rem",
                      cursor: "pointer",
                      backgroundColor: isLiked ? "#ffcccc" : "#eee",
                      border: "1px solid #aaa",
                      borderRadius: "4px",
                      marginRight: "0.5rem",
                    }}
                  >
                    {isLiked ? "❤️ Liked" : "🤍 Like"}
                  </button>

                  <strong>{r.reviewTitle}</strong> <em>({r.datePosted})</em>
                  <p>{r.reviewBody}</p>
                  <button
                    onClick={() => handleFlagReview(r.id)}
                    disabled={r.flagged}
                    style={{
                      padding: "0.25rem 0.5rem",
                      fontSize: "0.8rem",
                      cursor: r.flagged ? "not-allowed" : "pointer",
                      marginTop: "0.25rem",
                    }}
                  >
                    {r.flagged ? "Flagged" : "Flag Review"}
                  </button>
                </li>
              );
            })}
          </ul>
        )}
        {hasMoreReviews && (
          <button
            onClick={() => setReviewsPage((prev) => prev + 1)}
            style={{
              padding: "0.5rem",
              fontWeight: "bold",
              cursor: "pointer",
              marginTop: "1rem",
            }}
          >
            Load More
          </button>
        )}
      </section>
    </div>
  );
}