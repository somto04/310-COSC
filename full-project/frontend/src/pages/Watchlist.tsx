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
  useEffect(() => {
      setLoading(true);
      fetch(`${API}/users/watchlist`)
          .then((res) => {
              if (!res.ok) throw new Error(`HTTP ${res.status}`);
              return res.json();
          })
          .then(async (watchlist) => {
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
    <div style={{ padding: "2rem" }}>
      <h1>Watchlist</h1>
    </div>
  );
}
