import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom"; // Added for navigation

const API = import.meta.env.VITE_API_URL;


export default function Homepage() {
    type Movie = {
        id: number;
        tmdbId?: number;
        title: string;
        poster?: string | null;
        overview?: string;
        rating?: number;
    };

    const navigate = useNavigate(); // Initialize navigate

    const [movies, setMovies] = useState<Movie[]>([]);
    const [searchTerm, setSearchTerm] = useState("");
    const [loading, setLoading] = useState(false);

    // Filter state
    const [filterGenre, setFilterGenre] = useState("");
    const [filterYear, setFilterYear] = useState("");
    const [filterDirector, setFilterDirector] = useState("");
    const [filterStar, setFilterStar] = useState("");

    // Available options from API
    const [genres, setGenres] = useState<string[]>([]);
    const [decades, setDecades] = useState<number[]>([]);
    const [directors, setDirectors] = useState<string[]>([]);
    const [stars, setStars] = useState<string[]>([]);

    const fetchMoviesWithPosters = async (moviesList: any[]) => {
        const moviesWithPosters = await Promise.all(
            moviesList.map(async (movie: any) => {
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
        return moviesWithPosters;
    };
  
    // Fetch initial movies
    useEffect(() => {
        setLoading(true);
        fetch(`${API}/movies/`)
            .then((res) => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                return res.json();
            })
            .then(async (moviesList) => {
                const moviesWithPosters = await fetchMoviesWithPosters(moviesList);
                setMovies(moviesWithPosters);
                setLoading(false);
            })
            .catch((err) => {
                console.error("Error fetching movies:", err);
                setLoading(false);
            });
    }, []);
    
    // Fetch metadata for filters
    useEffect(() => {
        fetch(`${API}/movies/meta`)
            .then(res => {
                if (!res.ok) {
                    throw new Error(`HTTP ${res.status}: ${res.statusText}`);
                }
                const contentType = res.headers.get('content-type');
                if (!contentType || !contentType.includes('application/json')) {
                    throw new Error('Expected JSON but got: ' + contentType);
                }
                return res.json();
            })
            .then(data => {
                setGenres(data.genres || []);
                setDecades(data.decades || []);
                setDirectors(data.directors || []);
                setStars(data.stars || []);
            })
            .catch(err => {
                console.error("Error fetching metadata:", err);
                console.error("Make sure your backend is running and the endpoint is correct");
            });
    }, []);

    // Fetch filtered movies
    useEffect(() => {
        const fetchFilteredMovies = async () => {
            try {
                const params = new URLSearchParams();

                if (searchTerm) params.append("query", searchTerm);
                if (filterGenre) params.append("genre", filterGenre);
                if (filterYear) params.append("year", filterYear);
                if (filterDirector) params.append("director", filterDirector);
                if (filterStar) params.append("star", filterStar);

                const url = `${API}/movies/filter?${params.toString()}`;
                const res = await fetch(url);

                if (res.status === 404) {
                    setMovies([]);
                    return;
                }

                if (!res.ok) {
                    throw new Error(`HTTP ${res.status}`);
                }
                
                const data = await res.json();
                if (!Array.isArray(data)) {
                    setMovies([]);
                    return;
                }
                const moviesWithPosters = await fetchMoviesWithPosters(data);
                setMovies(moviesWithPosters);
            }
            catch (err) {
                console.error("Error fetching filtered movies:", err);
            }
        };
        
        fetchFilteredMovies();
    }, [searchTerm, filterDirector, filterStar, filterGenre, filterYear]);

    return (
        <div style={{ padding: "2rem", margin: "0 auto", maxWidth: "1200px" }}>
            <h1 style={{ marginBottom: "1rem" }}>Movies</h1>

            <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}>
                <input
                    type="text"
                    placeholder="Search movies..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    style={{
                        padding: "0.5rem",
                        flex: "1",
                        fontSize: "1rem",
                        height: "50px",
                    }}
                />
      
                <select 
                    value={filterGenre} 
                    onChange={(e) => setFilterGenre(e.target.value)}
                    style={{ padding: "0.5rem", fontSize: "1rem", height: "50px", minWidth: "120px" }}
                >
                    <option value="">All Genres</option>
                    {genres.map((g) => (
                        <option key={g} value={g}>
                            {g}
                        </option>
                    ))}
                </select>

                <select
                    value={filterYear}
                    onChange={(e) => setFilterYear(e.target.value)}
                    style={{ padding: "0.5rem", fontSize: "1rem", height: "50px", minWidth: "100px" }}
                >
                    <option value="">All Decades</option>
                    {decades.map((decade) => (
                        <option key={decade} value={decade}>
                            {decade}s
                        </option>
                    ))}
                </select>

                <select
                    value={filterDirector}
                    onChange={(e) => setFilterDirector(e.target.value)}
                    style={{ padding: "0.5rem", fontSize: "1rem", height: "50px", minWidth: "120px" }}
                >
                    <option value="">All Directors</option>
                    {directors.map((d) => (
                        <option key={d} value={d}>
                            {d}
                        </option>
                    ))}
                </select>      
      
                <select
                    value={filterStar}
                    onChange={(e) => setFilterStar(e.target.value)}
                    style={{ padding: "0.5rem", fontSize: "1rem", height: "50px", minWidth: "120px" }}
                >
                    <option value="">All Stars</option>
                    {stars.map((s) => (
                        <option key={s} value={s}>
                            {s}
                        </option>
                    ))}
                </select>
            </div>

            <section style={{ marginTop: "2rem" }}>
                {loading ? (
                    <p>Loading movies...</p>
                ) : movies.length === 0 ? (
                    <p>No movies found. Try adjusting your filters.</p>
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
                                onClick={() => navigate(`/movies/${movie.id}`)} // Navigate to MovieDetails
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
