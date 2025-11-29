import { useEffect, useState } from "react";

export default function Homepage() {
    type Movie = {
        id: number;
        tmdbId?: number;
        title: string;
        poster?: string | null;
        overview?: string;
        rating?: number;
    };
    
    const [movies, setMovies] = useState<Movie[]>([]);
    const [searchTerm, setSearchTerm] = useState("");
    const [loading, setLoading] = useState(false);

    const fetchMoviesWithPosters = async (moviesList: any[]) => {
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
    return moviesWithPosters;
  };
  
  useEffect(() => {
    setLoading(true);
    fetch("http://localhost:8000/movies/")
    .then((res) => res.json())
    .then(async (moviesList) => {
        const moviesWithPosters = await fetchMoviesWithPosters(moviesList);
        setMovies(moviesWithPosters);
        setLoading(false);
    })
    .catch((err) => {
        console.error(err);
        setLoading(false);
    });
    }, []);
    
    useEffect(() => {
        const fetchSearchResults = async () => {
        if (!searchTerm) {
            const res = await fetch("http://localhost:8000/movies/");
            const data = await res.json();
            const moviesWithPosters = await fetchMoviesWithPosters(data);
            setMovies(moviesWithPosters);
            return;
        }

        try {
            const res = await fetch(
            `http://localhost:8000/movies/search?query=${encodeURIComponent(
                searchTerm
            )}`
        );
        if (res.status === 404) {
            setMovies([]);
            return;
        }
        const data = await res.json();
        const moviesWithPosters = await fetchMoviesWithPosters(data);
        setMovies(moviesWithPosters);
    } 
    catch (err) {
        console.error(err);
    }
};
fetchSearchResults();}, [searchTerm]);

 return (
    <div style={{ padding: "2rem", maxWidth: "700px", margin: "0 auto" }}>
      <h1 style={{ marginBottom: "1rem" }}>Movies</h1>

      {/* SEARCH BOX */}
      <input
        type="text"
        placeholder="Search movies..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        style={{
          padding: "0.5rem",
          width: "100%",
          marginBottom: "1rem",
          fontSize: "1rem",
        }}
      />

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
                  cursor: "pointer",
                }}
                onClick={() => {}}
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