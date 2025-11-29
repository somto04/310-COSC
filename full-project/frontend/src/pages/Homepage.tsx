import { useEffect, useState } from "react";

export default function Homepage() {
    type Movie = {
        id: number;
        title: string;
        poster?: string | null;
        overview: string;
        rating: number;
    };
    
    const[movies, setMovies] = useState<Movie[]>([]);

    useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) return;

    fetch("http://localhost:8000/movies/", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then(async (movies) => {
        const moviesWithPosters = await Promise.all(
          movies.map(async (movie: any) => {
            const tmdbRes = await fetch(
              `http://localhost:8000/tmdb/details/${movie.id}`
            );
            const tmdbData = await tmdbRes.json();

            return {
              id: movie.id,
              title: movie.title,
              poster: tmdbData.poster || null,
            };
          })
        );

        setMovies(moviesWithPosters);
      })
      .catch((err) => console.error("Error loading favorites:", err));
  }, []);

   return (
    <div style={{ padding: "1rem" }}>
      <h1>Movies</h1>

      <ul style={{ listStyle: "none", padding: 0 }}>
        {movies.map((movie) => (
          <li
            key={movie.id}
            style={{
              marginBottom: "1.5rem",
              display: "flex",
              alignItems: "flex-start",
              gap: "1rem",
            }}
          >
            {movie.poster && (
              <img
                src={movie.poster}
                alt={movie.title}
                width={120}
                style={{ borderRadius: "5px", border: "1px solid #222" }}
              />
            )}

            <div>
              <h3 style={{ margin: 0 }}>{movie.title}</h3>
              <p style={{ margin: "0.3rem 0" }}>{movie.overview}</p>
              <p><strong>Rating:</strong> {movie.rating}/10</p>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}