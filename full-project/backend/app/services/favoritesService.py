# services/favoriteService.py
from fastapi import HTTPException
from ..repos.favoritesRepo import loadFavorites, saveFavorites
from ..repos.movieRepo import loadMovies
from ..schemas.favorites import Favorite

def addFavorite(userId: int, movieId: int):
    """Add a movie to user's favorites."""
    favorites = loadFavorites()
    movies = loadMovies()

    if not any(movie.id == movieId for movie in movies):
        raise HTTPException(status_code=404, detail="Movie not found")

    # prevent duplicate
    if any(favorite.userId == userId and favorite.movieId == movieId for favorite in favorites):
        return {"message": "Already favorited"}

    favorites.append(Favorite(userId=userId, movieId=movieId))
    saveFavorites(favorites)
    return {"message": "Added to favorites"}

def removeFavorite(userId: int, movieId: int):
    """
    Remove a movie from user's favorites.
    """
    favorites = loadFavorites()

    newList = [
        favorite for favorite in favorites
        if not (favorite.userId == userId and favorite.movieId == movieId)
    ]

    saveFavorites(newList)
    return {"message": "Removed from favorites"}

def listFavorites(userId: int):
    """List all favorite movies for a user."""
    favorites = loadFavorites()
    movies = loadMovies()

    favMovieIds = [favorite.movieId for favorite in favorites if favorite.userId == userId]

    return [movie for movie in movies if movie.id in favMovieIds]
