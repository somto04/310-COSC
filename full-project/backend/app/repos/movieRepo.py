from pathlib import Path
import json, os
from typing import List, Dict, Any
from fastapi import HTTPException

#loadAll function to read movie data from a JSON file
def loadAll() -> list[dict]:
    DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "movies.json"
    if not DATA_PATH.exists():
        return[]
    with DATA_PATH.open("r", encoding="utf-8") as f:
         return json.load(f)
     
#saveAll function to write movie data to a JSON file
def loadAll(items: list[dict]) -> None:
    DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "movies.json"
    tmp = DATA_PATH.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_PATH)
    
def saveAll(items: List[Dict[str, Any]]) -> None:
    DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "movies.json"
    tmp = DATA_PATH.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_PATH)
    
def deleteMovie(movieId: str) -> None:
    movies = loadAll()
    newMovies = [it for it in movies if it.get("id") != movieId]
    if len(newMovies) == len(movies):
        raise HTTPException(status_code=404, detail=f"Movie '{movieId}' not found")
    saveAll(newMovies)
    
def searchMovie(query: str) -> List[Dict[str, Any]]:
    movies = loadAll()
    results = []
    query_lower = query.lower()
    for it in movies:
        if (query_lower in it.get("movieName", "").lower() or
            query_lower in it.get("genre", "").lower() or
            any(query_lower in actor.lower() for actor in it.get("actors", []))):
            results.append(it)
    return results
