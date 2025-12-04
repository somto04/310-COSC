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

      // Revert UI
      setLikedReviewIds((prev) =>
        isLiked ? [...prev, reviewId] : prev.filter((id) => id !== reviewId)
      );

      alert("Error updating like.");
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

  // --- FAVORITES SYSTEM ---
  const [isFavorite, setIsFavorite] = useState(false);

  const checkFavoriteStatus = async () => {
    const token = localStorage.getItem("token");
    const userId = localStorage.getItem("userId");

    if (!movieId || !token || !userId) return;

    try {
      const res = await fetch(`${API}/favorites/`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) return;

      const data = await res.json();
      const favIds = data.map((m: any) => m.id);

      setIsFavorite(favIds.includes(Number(movieId)));
    } catch (err) {
      console.error("Failed to load favorites", err);
    }
  };

  const addToFavorites = async () => {
    const token = localStorage.getItem("token");
    if (!token || !movie) return;

    try {
      await fetch(`${API}/favorites/${movie.id}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` }
      });
      setIsFavorite(true);
    } catch (err) {
      console.error("Failed to add to favorites", err);
    }
  };

  const removeFromFavorites = async () => {
    const token = localStorage.getItem("token");
    if (!token || !movie) return;

    try {
      await fetch(`${API}/favorites/${movie.id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` }
      });
      setIsFavorite(false);
    } catch (err) {
      console.error("Failed to remove from favorites", err);
    }
  };

  // Load everything
  useEffect(() => {
    if (!movieId) return;

    const fetchData = async () => {
      setLoading(true);
      try {
        const res = await fetch(`${API}/movies/${movieId}`);
        if (!res.ok) throw new Error("Failed to fetch movie");
        const data: Movie = await res.json();
        setMovie(data);

        const tmdbRes = await fetch(`${API}/tmdb/details/${movieId}`);
        if (tmdbRes.ok) setTmdb(await tmdbRes.json());

        fetchLikedReviews();
        checkFavoriteStatus();
        checkWatchlistStatus();
        fetchReviews(1);
      } catch (err) {
        console.error(err);
        setError("Error loading movie details");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [movieId]);

  const fetchReviews = async (page: number) => {
    try {
      const res = await fetch(
        `${API}/reviews/search?query=${movieId}&page=${page}&limit=10`
      );
      if (!res.ok) throw new Error("Failed to fetch reviews");

      const data: Review[] = await res.json();

      if (page === 1) setReviews(data);
      else setReviews((prev) => [...prev, ...data]);

      setHasMoreReviews(data.length === 10);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (reviewsPage !== 1) fetchReviews(reviewsPage);
  }, [reviewsPage]);

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

      if (!res.ok) throw new Error("Failed to post review");

      const newReview = await res.json();
      setReviews((prev) => [newReview, ...prev]);

      setNewTitle("");
      setNewBody("");
    } catch (err) {
      console.error(err);
      setError("Failed to post review");
    } finally {
      setPosting(false);
    }
  };

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

      if (!res.ok) throw new Error("Failed to flag review");

      setReviews((prev) =>
        prev.map((r) =>
          r.id === reviewId ? { ...r, flagged: true } : r
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

      <button
        onClick={isFavorite ? removeFromFavorites : addToFavorites}
        style={{
          marginTop: "1rem",
          padding: "0.6rem 1rem",
          fontWeight: "bold",
          border: "1px solid black",
          backgroundColor: isFavorite ? "red" : "black",
          color: "white",
          cursor: "pointer",
          borderRadius: "4px",
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

      {/* ---- Reviews UI ---- */}
      <section style={{ marginTop: "2rem" }}>
        <h2>Reviews</h2>

        {reviews.map((r) => (
          <div key={r.id} style={{ border: "1px solid #ccc", padding: "1rem", marginBottom: "1rem" }}>
            <strong>{r.reviewTitle}</strong>
            <p>{r.reviewBody}</p>

            {/* Like button */}
            <button onClick={() => handleToggleLike(r.id)}>
              {likedReviewIds.includes(r.id) ? "❤️ Unlike" : "🤍 Like"}
            </button>

            {/* Flag button */}
            <button
              onClick={() => handleFlagReview(r.id)}
              disabled={r.flagged}
            >
              {r.flagged ? "Flagged" : "Flag Review"}
            </button>
          </div>
        ))}

        {hasMoreReviews && (
          <button onClick={() => setReviewsPage((p) => p + 1)}>
            Load More
          </button>
        )}
      </section>
    </div>
  );
}
