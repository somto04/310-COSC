import { useEffect, useState } from "react";

interface Movie {
    id: number;
    title: string;
    posterPath: string;
}

export default function Homepage() {
    const[movies, setMovies] = useState<Movie[]>([]);

    useEffect(() => {
        fetch("http://localhost:8000/movies")
        .then((response) => response.json())
        .then((data) => setMovies(data));
    }, []);

    return (
        <div>
           <h1>Movies</h1> 
           <ul>
            {movies.map((movie) => (
            <li key={movie.id}>{movie.title}</li>
            ))}
           </ul>
        </div>
    )
}