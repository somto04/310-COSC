from typing import List, Dict
from fastapi import HTTPException
from ..schemas.movie import Movie, MovieUpdate, MovieCreate
from ..repos.movieRepo import loadAll, saveAll


def listMovies() -> List[Movie]:
    data = loadAll()
    print("Loaded", len(data), "movies")
    return [Movie(**m) for m in data]


def createMovie(payload: MovieCreate) -> Movie:
    movies = loadAll()
    new_movie = payload.model_dump()

    #generate next integer ID
    existing_ids = [m.get("id") for m in movies if isinstance(m.get("id"), int)]
    new_movie["id"] = max(existing_ids, default=0) + 1

    movies.append(new_movie)
    saveAll(movies)
    return Movie(**new_movie)

#this function filters movies based on genre, year, director, and star
def getMovieByFilter(genre: str = None, year: int = None, director: str = None, star: str = None) -> List[Dict]:
    movies = loadAll()
    results = []

    for m in movies:
        #prepare fields for matching by accepting substrings and ignoring case
        genres = [g.lower().strip() for g in m.get("movieGenres", [])]
        directors = [d.lower().strip() for d in m.get("directors", [])]
        stars = [s.lower().strip() for s in m.get("mainStars", [])]
        # extract year from datePublished
        date = str(m.get("datePublished", ""))[:4]  

        #you can combine multiple filters or use only one and still get a result
        #genre check: look for substring match anywhere in the list
        if genre and not any(genre.lower() in g for g in genres):
            continue

        if year and date != str(year):
            continue
        
        if director and not any(director.lower() in d for d in directors):
            continue

        if star and not any(star.lower() in s for s in stars):
            continue
        
        #if all checks passed, add to results
        results.append({
            "id": m.get("id"),
            "title": m.get("title"),
            "movieIMDbRating": m.get("movieIMDbRating"),
            "movieGenres": m.get("movieGenres"),
            "directors": m.get("directors"),
            "mainStars": m.get("mainStars"),
            "description": m.get("description"),
            "datePublished": m.get("datePublished"),
            "duration": m.get("duration"),
        })
    return results


    
def getMovieById(movieId: int) -> Movie:
    for m in loadAll():
        if int(m.get("id")) == int(movieId):   #match ints or str
            return Movie(**m)
    raise HTTPException(status_code=404, detail="Movie not found")


def updateMovie(movieId: int, payload: MovieUpdate) -> Movie:
    movies = loadAll()
    for idx, m in enumerate(movies):
        if int(m.get("id")) == int(movieId):   #compare as ints
            updates = payload.model_dump(exclude_unset=True)
            movies[idx] = {**m, **updates}
            saveAll(movies)
            return Movie(**movies[idx])
    raise HTTPException(status_code=404, detail="Movie not found")


def deleteMovie(movieId: int) -> None:
    movies = loadAll()
    filtered = [m for m in movies if int(m.get("id")) != int(movieId)]
    if len(filtered) == len(movies):
        raise HTTPException(status_code=404, detail="Movie not found")
    saveAll(filtered)

def searchViaFilters(filters: Dict) -> List[Dict]:
    results = []
    for m in loadAll():
        match = True
        for key, value in filters.items():
            if key not in m:
                match = False
                break
            if isinstance(value, str):
                if str(m[key]).lower() != value.lower():
                    match = False
                    break
            elif isinstance(value, (int, float)):
                if m[key] != value:
                    match = False
                    break
            elif isinstance(value, list):
                if not all(item in m[key] for item in value):
                    match = False
                    break
        if match:
            results.append({
                "id": m.get("id"),
                "title": m.get("title"),
                "movieIMDbRating": m.get("movieIMDbRating"),
                "movieGenres": m.get("movieGenres"),
                "directors": m.get("directors"),
                "mainStars": m.get("mainStars"),
                "description": m.get("description"),
                "datePublished": m.get("datePublished"),
                "duration": m.get("duration"),
            })
    return results

def searchMovie(query: str) -> List[Dict]:
    q = (query or "").lower().strip()
    if not q:
        return []

    results = []
    for m in loadAll():
        title = str(m.get("title", "")).lower()
        desc = str(m.get("description", "")).lower()
        genres = " ".join(m.get("movieGenres", []))
        stars = " ".join(m.get("mainStars", []))
        directors = " ".join(m.get("directors", []))

        if any(q in field for field in [title, desc, genres, stars, directors]):
            results.append({
                "id": m.get("id"),
                "title": m.get("title"),
                "movieIMDbRating": m.get("movieIMDbRating"),
                "movieGenres": m.get("movieGenres"),
                "directors": m.get("directors"),
                "mainStars": m.get("mainStars"),
                "description": m.get("description"),
                "datePublished": m.get("datePublished"),
                "duration": m.get("duration"),
            })
    return results
