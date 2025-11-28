import { useEffect, useState } from "react";

interface Movie {
  id: number;
  title: string;
  poster: string | null;
  overview: string;
  rating: number;
}

export default function Homepage() {
    const[movies, setMovies] = useState<Movie[]>([]);

    useEffect(() => {
    async function fetchMoviesWithDetails() {
        try {
        const res = await fetch("http://localhost:8000/movies");
        const movies = await res.json();

        const detailedMovies = await Promise.all(
            movies.map(async (movie: any) => {
            try {
                const detailsRes = await fetch(
                `http://localhost:8000/details/name/${encodeURIComponent(movie.title)}`
                );
                if (!detailsRes.ok) return null; 
                const details = await detailsRes.json();
                return details;
            } catch {
                return null;
            }
            })
        );

        setMovies(detailedMovies.filter((movie) => movie !== null) as Movie[]);
        } catch (err) {
        console.error("Failed to fetch movies:", err);
        }
    }

    fetchMoviesWithDetails();
    }, []);


    return (
        <div>
           <h1>Movies</h1> 
           <ul>
            {movies.map((movie) => (
                <li key={movie.id}>
                {movie.poster && (
                    <img src={movie.poster} alt={movie.title} width={150} />
                )}
                <p>{movie.title}</p>
                </li>
            ))}
            </ul>
        </div>
    )
}