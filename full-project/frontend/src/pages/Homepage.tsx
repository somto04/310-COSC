import { useEffect, useState } from "react";

export default function Homepage() {
    type Movie = {
        id: number;
        tmdbId: number;
        title: string;
        poster?: string | null;
        overview: string;
        rating: number;
    };
    
    const[movies, setMovies] = useState<Movie[]>([]);

    useEffect(() => {
    fetch("http://localhost:8000/movies/")

      .then((res) => res.json())
      .then(async (moviesList) => {
            console.log("MOVIES FROM BACKEND:", moviesList);
        const moviesWithPosters = await Promise.all(
          moviesList.map(async (movie: any) => {
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
      .catch((err) => console.error("Error loading movies:", err));
  }, []);
 return (
    <div style={{ padding: "2rem", maxWidth: "700px", margin: "0 auto" }}>
      <h1 style={{ marginBottom: "1rem" }}>Movies</h1>

      {/* MOVIES */}
      <section style={{ marginTop: "2rem" }}>

        {movies.length === 0 ? (
          <p>No movies yet.</p>
        ) : (
          <ul style={{ paddingLeft: "1rem" }}>
            {movies.map((movie) => (
              <li
                key={movie.id}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "1rem",
                  marginBottom: "1rem",
                }}
              >
                {movie.poster && (
                  <img
                    src={movie.poster}
                    alt={movie.title}
                    style={{
                      width: "60px",
                      height: "90px",
                      objectFit: "cover",
                      border: "1px solid black",
                    }}
                  />
                )}

                <span>{movie.title}</span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}