# services/favoriteService.py
from fastapi import HTTPException
from ..repos.favoritesRepo import loadFavorites, saveFavorites
from ..repos.movieRepo import loadMovies
from ..schemas.favorites import Favorite

class FavoriteError(Exception):
    """Base class for favorite-related errors."""
    pass

class MovieNotFoundError(FavoriteError):
    """Raised when the movie does not exist."""
    pass

class FavoriteAlreadyExistsError(FavoriteError):
    """Raised when adding a duplicate favorite."""
    pass

class FavoriteNotFoundError(FavoriteError):
    """Raised when removing a favorite that doesn't exist."""
    pass

def addFavorite(userId: int, movieId: int):
    """Add a movie to user's favorites."""
    favorites = loadFavorites()
    movies = loadMovies()

    if not any(movie.id == movieId for movie in movies):
        raise MovieNotFoundError(f"Movie '{movieId}' not found")

    # prevent duplicate
    if any(favorite.userId == userId and favorite.movieId == movieId for favorite in favorites):
        raise FavoriteAlreadyExistsError(f"Movie '{movieId}' already in favorites")

    favorites.append(Favorite(userId=userId, movieId=movieId))
    saveFavorites(favorites)
    return {"message": "Added to favorites"}

def removeFavorite(userId: int, movieId: int):
    """
    Remove a movie from user's favorites.
    """
    favorites = loadFavorites()
    
    if not any(f.userId == userId and f.movieId == movieId for f in favorites):
        raise FavoriteNotFoundError(f"Favorite '{movieId}' not found for current user")
    
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
