import { useEffect, useState } from "react";
const API = import.meta.env.VITE_API_URL;

export default function WatchlistPage() {
  type Movie = {
    id: number;
    tmdbId?: number;
    title: string;
    poster?: string | null;
    overview?: string;
    rating?: number;
  };

  const [movies, setMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(false);

  // Fetch initial watchlist
  const token = localStorage.getItem("token");
  useEffect(() => {
      setLoading(true);
      fetch(`${API}/users/watchlist`, {
        headers: {
        Authorization: `Bearer ${token}`},
        credentials: "include",
    })          
    .then((res) => {
              if (!res.ok) throw new Error(`HTTP ${res.status}`);
              return res.json();
          })
          .then(async (response) => {
            const watchlist = response.watchlist || [];
            const watchlistWithPosters = await fetchWatchlistWithPosters(watchlist);
              setMovies(watchlistWithPosters);
              setLoading(false);
          })
          .catch((err) => {
              console.error("Error fetching movies:", err);
              setLoading(false);
          });
  }, []);
  
  const fetchWatchlistWithPosters = async (watchlist: any[]) => {
    const watchlistWithPosters = await Promise.all(
      watchlist.map(async (movie: any) => {
        try {
            const tmdbRes = await fetch(
              `${API}/tmdb/details/${movie.id}`
            );
            const tmdbData = await tmdbRes.json();
            return {
                id: movie.id,
                title: movie.title,
                poster: tmdbData.poster || null,
            };
          } catch (err) {
            console.error(`Error fetching poster for ${movie.title}:`, err);
            return {
                id: movie.id,
                title: movie.title,
                poster: null,
              };
            }
          })
      );
      return watchlistWithPosters;
  };

  return (
    <div style={{ padding: "2rem", margin: "0 auto", maxWidth: "1200px" }}>
      <h1 style={{ marginBottom: "1rem" }}>Watchlist</h1>

        <section style={{ marginTop: "2rem" }}>
            {loading ? (
                <p>Loading movies...</p>
            ) : movies.length === 0 ? (
                <p>No movies found. Try adding a movie to your watchlist.</p>
            ) : (
                <ul style={{ listStyle: "none", padding: 0 }}>
                    {movies.map((movie) => (
                        <li
                            key={movie.id}
                            style={{
                                display: "flex",
                                alignItems: "center",
                                gap: "1rem",
                                marginBottom: "1rem",
                                cursor: "pointer",
                                padding: "0.5rem",
                                border: "1px solid #ddd",
                                borderRadius: "4px",
                                transition: "background-color 0.2s",
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "#f5f5f5"}
                            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "transparent"}
                        >
                            {movie.poster ? (
                                <img
                                    src={movie.poster}
                                    alt={movie.title}
                                    style={{
                                        width: "60px",
                                        height: "90px",
                                        objectFit: "cover",
                                        border: "1px solid #ccc",
                                        borderRadius: "4px",
                                    }}
                                />
                            ) : (
                                <div style={{
                                    width: "60px",
                                    height: "90px",
                                    backgroundColor: "#e0e0e0",
                                    display: "flex",
                                    alignItems: "center",
                                    justifyContent: "center",
                                    border: "1px solid #ccc",
                                    borderRadius: "4px",
                                    fontSize: "0.7rem",
                                    color: "#666",
                                    textAlign: "center",
                                    padding: "0.25rem",
                                }}>
                                    No Image
                                </div>
                            )}
                            <span style={{ fontSize: "1.1rem" }}>{movie.title}</span>
                        </li>
                    ))}
                </ul>
            )}
        </section>
    </div>
  );
}
