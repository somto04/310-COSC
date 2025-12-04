import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getToken, getUserId } from "../utils/auth";

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

  // Movie + TMDB
  const [movie, setMovie] = useState<Movie | null>(null);
  const [tmdb, setTmdb] = useState<TMDbMovie | null>(null);

  // Reviews
  const [reviews, setReviews] = useState<Review[]>([]);
  const [reviewsPage, setReviewsPage] = useState(1);
  const [hasMoreReviews, setHasMoreReviews] = useState(false);

  // Form state
  const [newTitle, setNewTitle] = useState("");
  const [newBody, setNewBody] = useState("");
  const [posting, setPosting] = useState(false);

  // UI + Errors
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // LIKE SYSTEM
  const [likedReviewIds, setLikedReviewIds] = useState<number[]>([]);

  // FAVORITES SYSTEM
  const [isFavorite, setIsFavorite] = useState(false);


  // --- FETCH LIKED REVIEWS ---
  const fetchLikedReviews = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) return;

      const res = await fetch(`${API}/likeReview/`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) return;

      const data = await res.json();
      setLikedReviewIds(data.map((item: { id: number }) => item.id));
    } catch {}
  };


  // --- TOGGLE LIKE ---
  const handleToggleLike = async (reviewId: number) => {
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Please log in to like reviews.");
      return;
    }

    const isLiked = likedReviewIds.includes(reviewId);

    // optimistic UI
    setLikedReviewIds(prev =>
      isLiked ? prev.filter(id => id !== reviewId) : [...prev, reviewId]
    );

    try {
      const method = isLiked ? "DELETE" : "POST";
      const res = await fetch(`${API}/likeReview/${reviewId}`, {
        method,
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) throw new Error();
    } catch {
      // revert UI
      setLikedReviewIds(prev =>
        isLiked ? [...prev, reviewId] : prev.filter(id => id !== reviewId)
      );
    }
  };

  // ---  WATCHLIST SYSTEM ---
  const [isInWatchlist, setInWatchlist] = useState(false);

  const checkWatchlistStatus = async () => {
    const token = getToken();

    if (!movieId || !token) return;

    try {
      const res = await fetch(`${API}/users/watchlist`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) return;

      const data = await res.json();
      const watchlistIds = data.watchlist.map((movie: any) => movie.id);

      setInWatchlist(watchlistIds.includes(Number(movieId)));
    } catch (err) {
      console.error("Failed to load watchlist", err);
    }
  };

  const addToWatchlist = async () => {
    const token = getToken;
    if (!token || !movie) return;

    try {
      const res = await fetch(`${API}/users/watchlist/${movie.id}`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        }
      });

      if (!res.ok) {
        console.error("Backend failed to add movie:", res.status);
        return;
      }

      setInWatchlist(true);
    } catch (err) {
      console.error("Failed to add to watchlist", err);
    }
  };


  const removeFromWatchlist = async () => {
    const token = getToken();
    if (!token || !movie) return;

    try {
      await fetch(`${API}/users/watchlist/${movie.id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` }
      });
      setInWatchlist(false);
    } catch (err) {
      console.error("Failed to remove from watchlist", err);
    }
  };

  // --- FAVORITES CHECK ---
  const checkFavoriteStatus = async () => {
    const token = localStorage.getItem("token");
    if (!token || !movieId) return;

    try {
      const res = await fetch(`${API}/favorites/`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) return;

      const data = await res.json();
      const favIds = data.map((m: any) => m.id);
      setIsFavorite(favIds.includes(Number(movieId)));
    } catch {}
  };


  // --- ADD FAVORITE ---
  const addToFavorites = async () => {
    const token = localStorage.getItem("token");
    if (!token || !movie) return;

    try {
      await fetch(`${API}/favorites/${movie.id}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      setIsFavorite(true);
    } catch {}
  };


  // --- REMOVE FAVORITE ---
  const removeFromFavorites = async () => {
    const token = localStorage.getItem("token");
    if (!token || !movie) return;

    try {
      await fetch(`${API}/favorites/${movie.id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      setIsFavorite(false);
    } catch {}
  };


  // --- FETCH MOVIE, TMDB, REVIEWS ---
  useEffect(() => {
    if (!movieId) return;

    const loadData = async () => {
      setLoading(true);
      try {
        const res = await fetch(`${API}/movies/${movieId}`);
        if (!res.ok) throw new Error();
        const data: Movie = await res.json();
        setMovie(data);

        const tmdbRes = await fetch(`${API}/tmdb/details/${movieId}`);
        if (tmdbRes.ok) setTmdb(await tmdbRes.json());

        fetchLikedReviews();
        checkFavoriteStatus();
        checkWatchlistStatus();
        fetchReviews(1);

      } catch {
        setError("Error loading movie");
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [movieId]);


  // --- FETCH REVIEWS ---
  const fetchReviews = async (page: number) => {
    try {
      const res = await fetch(
        `${API}/reviews/search?query=${movieId}&page=${page}&limit=10`
      );

      if (!res.ok) throw new Error();

      const data: Review[] = await res.json();
      if (page === 1) setReviews(data);
      else setReviews(prev => [...prev, ...data]);

      setHasMoreReviews(data.length === 10);
    } catch {}
  };

  useEffect(() => {
    if (reviewsPage !== 1) fetchReviews(reviewsPage);
  }, [reviewsPage]);


  // --- POST REVIEW ---
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle || !newBody) return;

    setPosting(true);
    try {
      const token = localStorage.getItem("token");

      const res = await fetch(`${API}/reviews/${movieId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          reviewTitle: newTitle,
          reviewBody: newBody,
          rating: 5,
        }),
      });

      if (!res.ok) throw new Error();

      const newReview = await res.json();
      setReviews(prev => [newReview, ...prev]);

      setNewTitle("");
      setNewBody("");

    } catch {
      setError("Failed to post review");
    } finally {
      setPosting(false);
    }
  };


  // --- FLAG REVIEW ---
  const handleFlagReview = async (reviewId: number) => {
    try {
      const token = getToken();
      const res = await fetch(`${API}/reviews/${reviewId}/flag`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) throw new Error();

      setReviews(prev =>
        prev.map(r => (r.id === reviewId ? { ...r, flagged: true } : r))
      );

    } catch {
      alert("Failed to flag review");
    }
  };


  // --- RENDER ---
  if (loading) return <p>Loading movie details...</p>;
  if (!movie) return <p>Movie not found.</p>;


  return (
    <div style={{ maxWidth: "800px", margin: "0 auto", padding: "2rem" }}>

      <h1>{movie.title}</h1>

      {/* POSTER + DETAILS */}
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
          <p><strong>Duration:</strong> {tmdb?.runtime || movie.duration} min</p>
          <p><strong>Description:</strong> {tmdb?.overview || movie.description}</p>
        </div>
      </div>

      {/* FAVORITES BUTTON */}
      <button
        onClick={isFavorite ? removeFromFavorites : addToFavorites}
        style={{
          padding: "0.6rem 1rem",
          marginBottom: "1rem",
          fontWeight: "bold",
          border: "1px solid black",
          backgroundColor: isFavorite ? "red" : "black",
          color: "white",
          borderRadius: "4px",
          cursor: "pointer",
        }}
      >
        {isFavorite ? "Remove from Favorites" : "Add to Favorites ⭐"}
      </button>

      <button
        onClick={isInWatchlist ? removeFromWatchlist : addToWatchlist}
        style={{
          marginTop: "1rem",
          padding: "0.6rem 1rem",
          fontWeight: "bold",
          border: "1px solid black",
          backgroundColor: isInWatchlist ? "red" : "black",
          color: "white",
          cursor: "pointer",
          borderRadius: "4px",
        }}
      >
        {isInWatchlist ? "Remove from Watchlist" : "Add to Watchlist ⭐"}
      </button>

      <button
        onClick={isInWatchlist ? removeFromWatchlist : addToWatchlist}
        style={{
          marginTop: "1rem",
          padding: "0.6rem 1rem",
          fontWeight: "bold",
          border: "1px solid black",
          backgroundColor: isInWatchlist ? "red" : "black",
          color: "white",
          cursor: "pointer",
          borderRadius: "4px",
        }}
      >
        {isInWatchlist ? "Remove from Watchlist" : "Add to Watchlist ⭐"}
      </button>


      {/* --- ADD REVIEW --- */}
      <section style={{ marginTop: "2rem" }}>
        <h2>Add a Review</h2>

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


      {/* --- REVIEWS LIST --- */}
      <section style={{ marginTop: "2rem" }}>
        <h2>Reviews</h2>

        {reviews.map((r) => {
          const liked = likedReviewIds.includes(r.id);

          return (
            <div
              key={r.id}
              style={{
                border: "1px solid #ddd",
                padding: "1rem",
                marginBottom: "1rem",
                borderRadius: "4px",
              }}
            >
              <strong>{r.reviewTitle}</strong> <em>({r.datePosted})</em>
              <p>{r.reviewBody}</p>

              {/* LIKE BUTTON */}
              <button
                onClick={() => handleToggleLike(r.id)}
                style={{
                  padding: "0.25rem 0.5rem",
                  marginRight: "0.5rem",
                  backgroundColor: liked ? "#ffdddd" : "#eee",
                  cursor: "pointer",
                }}
              >
                {liked ? "❤️ Liked" : "🤍 Like"}
              </button>

              {/* FLAG BUTTON */}
              <button
                onClick={() => handleFlagReview(r.id)}
                disabled={r.flagged}
                style={{
                  padding: "0.25rem 0.5rem",
                  cursor: r.flagged ? "not-allowed" : "pointer",
                }}
              >
                {r.flagged ? "Flagged" : "Flag Review"}
              </button>
            </div>
          );
        })}

        {hasMoreReviews && (
          <button
            onClick={() => setReviewsPage((p) => p + 1)}
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
