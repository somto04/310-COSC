from typing import List
from fastapi import HTTPException
from ..schemas.review import Review, ReviewUpdate, ReviewCreate
from ..repos.reviewRepo import loadReviews, saveReviews, getNextReviewId
from ..repos import movieRepo

def searchReviews(query: str) -> List[Review]:
    """ Searches reviews by movie title (case-insensitive) or by movie ID 
    
    Returns:
        Reviews that match the search
    """
    strippedQuery = (query or "").strip().lower()
    if not strippedQuery:
        return []

    reviews = loadReviews()
    movies = movieRepo.loadAll()

    # If query is a number, treat as movie ID
    if strippedQuery.isdigit():
        movie_id = int(strippedQuery)
        return [review for review in reviews if review.movieId == movie_id]

    matching_movie_ids = [
        movie["id"] for movie in movies
        if strippedQuery in movie.get("title", "").lower()
    ]

    return [review for review in reviews if review.movieId in matching_movie_ids]


def listReviews() -> List[Review]:
    """ Lists all reviews currently stored """
    return loadReviews()

def createReview(payload: ReviewCreate) -> Review:
    """ 
    Creates a new review and saves it according to our review schema 

    Returns: 
        New review
    
    Raises: 
        HTTPException: id collision error if theres a duplicate
    """
    reviews = loadReviews()

    newReview = Review(
        id=getNextReviewId(), 
        movieId=payload.movieId, 
        userId=payload.userId,
        reviewTitle=payload.reviewTitle.strip(), 
        rating=payload.rating if isinstance(payload.rating, int) else int(payload.rating),
        reviewBody=payload.reviewBody.strip(),
        flagged=payload.flagged or False,
    )
    
    reviews.append(newReview)
    saveReviews(reviews)
    return newReview

def getReviewById(reviewId: int) -> Review:
    """ 
    Retrieves a review by its ID

    Returns: 
        The review
    
    Raises: 
        HTTPException: review not found
    """
    reviews = loadReviews()

    for review in reviews:
        if review.id == reviewId:
            return review
    raise HTTPException(status_code=404, detail=f"Review '{reviewId}' not found")

def updateReview(reviewId: int, payload: ReviewUpdate) -> Review:
    """ 
    Updates an existing review identified by its ID

    Returns: 
        The updated review
    
    Raises: 
        HTTPException: review not found
    """  
    reviews = loadReviews()
    for idx, it in enumerate(reviews):
        if it.id == reviewId:
            updateData = payload.model_dump(exclude_unset=True)
            
            updatedDict = it.model_dump()
            updatedDict.update(updateData)
            
            if 'reviewTitle' in updateData and updatedDict['reviewTitle']:
                updatedDict['reviewTitle'] = updatedDict['reviewTitle'].strip()

            if 'reviewBody' in updateData and updatedDict['reviewBody']:
                updatedDict['reviewBody'] = updatedDict['reviewBody'].strip()

            if 'rating' in updateData and updatedDict['rating']:
                updatedDict['rating'] = int(updatedDict['rating'])
            
            updated = Review(**updatedDict)
            reviews[idx] = updated
            saveReviews(reviews)
            return updated
        
    raise HTTPException(status_code=404, detail=f"Review '{reviewId}' not found")

def deleteReview(reviewId: int) -> None:
    """ 
    Deletes a review by its ID

    Raises: 
        HTTPException: review not found
    """  
    reviews = loadReviews()
    newReviews = [review for review in reviews if review.id != reviewId]

    if len(newReviews) == len(reviews):
        raise HTTPException(status_code=404, detail=f"Review '{reviewId}' not found")
    
    saveReviews(newReviews)
