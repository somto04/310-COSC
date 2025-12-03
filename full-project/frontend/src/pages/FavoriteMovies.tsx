import { useEffect, useState } from "react";
const API = import.meta.env.VITE_API_URL;

type Recommendation = {
  id: number;
  title: string;
  poster: string | null;
  rating: number;
};

type MovieDetails = {
  id: number;
  title: string;
  poster: string | null;

  // local DB
  duration: number | null;
  year: number | null;
  stars: string[];

  // tmdb
  overview: string | null;
  rating: number | null;

  recommendations: Recommendation[];
};



export default function FavoriteMovies() {
  const [movies, setMovies] = useState<MovieDetails[]>([]);
  const [loading, setLoading] = useState(true);
  const handleRemove = async (movieId: number) => {
  const token = localStorage.getItem("token");


  try {
    await fetch(`${API}/favorites/${movieId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });

    // remove from state instantly
    setMovies((prev) => prev.filter((m) => m.id !== movieId));
  } catch (err) {
    console.error("Error removing favorite:", err);
  }
};

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) return;

    fetch(`${API}/favorites/`,{
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then(async (favorites) => {
        const results = await Promise.all(
          favorites.map(async (fav: any) => {
            // LOCAL DB DETAILS
            const localRes = await fetch(
              `${API}/movies/${fav.id}`
            );
            const localMovie = await localRes.json();

            // TMDB DETAILS
            const tmdbRes = await fetch(
              `${API}/tmdb/details/${fav.id}`
            );
            const tmdb = await tmdbRes.json();

            // TMDB RECOMMENDATIONS
            const recRes = await fetch(
              `${API}/tmdb/recommendations/${fav.id}`
            );
            const recs = await recRes.json();

            return {
              id: fav.id,
              title: fav.title,

              poster: tmdb.poster || fav.poster,

              // LOCAL DB INFO
              duration: localMovie.duration || null,
              year: localMovie.year || null,
              stars: localMovie.mainStars || [],

              // TMDB INFO
              overview: tmdb.overview || null,
              rating: tmdb.rating || null,

              recommendations: recs || [],
            };
          })
        );

        setMovies(results);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error loading favorite movies:", err);
        setLoading(false);
      });
  }, []);

  if (loading) return <p style={{ padding: "2rem" }}>Loading favorites...</p>;
const token = localStorage.getItem("token");

// user not logged in
if (!token) {
  return (
    <p style={{ padding: "2rem" }}>
      You must be logged in to view your favorite movies.
    </p>
  );
}

// user logged in but list empty
if (movies.length === 0) {
  return (
    <p style={{ padding: "2rem" }}>
      You have no favorite movies in your list.
    </p>
  );
}

  return (
    <div style={{ padding: "2rem", maxWidth: "900px", margin: "0 auto" }}>
      <h1>Your Favorite Movies</h1>

      {movies.map((movie) => (
        <div
          key={movie.id}
          style={{
            borderBottom: "1px solid #ccc",
            paddingBottom: "2rem",
            marginBottom: "2rem",
          }}
        >
          <div style={{ display: "flex", gap: "1.5rem" }}>
            {movie.poster && (
              <img
                src={movie.poster}
                alt={movie.title}
                style={{
                  width: "160px",
                  height: "240px",
                  objectFit: "cover",
                  border: "1px solid black",
                }}
              />
            )}

            <div>
             <h2
  style={{
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    margin: 0,
  }}
>
  {movie.title}

  <button
    onClick={() => handleRemove(movie.id)}
    style={{
      padding: "0.3rem 0.8rem",
      border: "1px solid black",
      background: "black",
      color: "white",
      cursor: "pointer",
      fontSize: "0.9rem",
    }}
  >
    Remove
  </button>
</h2>


              {movie.year && (
                <p>
                  <strong>Year:</strong> {movie.year}
                </p>
              )}

              {movie.duration && (
                <p>
                  <strong>Duration:</strong> {movie.duration} min
                </p>
              )}

              {movie.stars.length > 0 && (
                <p>
                  <strong>Stars:</strong> {movie.stars.join(", ")}
                </p>
              )}

              {movie.rating && (
                <p>
                  <strong>Rating:</strong> ⭐ {movie.rating}
                </p>
              )}

              {movie.overview && (
                <p style={{ marginTop: "1rem" }}>
                  <strong>Overview:</strong> {movie.overview}
                </p>
              )}
            </div>
          </div>

          {/* RECOMMENDATIONS */}
          {movie.recommendations.length > 0 && (
            <div style={{ marginTop: "1.5rem" }}>
              <h3>Recommendations</h3>

              <div style={{ display: "flex", gap: "1rem" , flexWrap: "wrap" , justifyContent: "center", textAlign: "center"}}>
                {movie.recommendations.slice(0, 4).map((rec) => (
                  <div key={rec.id} style={{ width: "140px" }}>
                    {rec.poster && (
                      <img
                        src={rec.poster}
                        alt={rec.title}
                        style={{
                          width: "140px",
                          height: "210px",
                          objectFit: "cover",
                          border: "1px solid black",
                        }}
                      />
                    )}
                    <p style={{ marginTop: "0.5rem" }}>{rec.title}</p>
                    <p style={{ fontSize: "0.85rem", color: "#555" }}>
                      ⭐ {rec.rating}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
