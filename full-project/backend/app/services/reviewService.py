from typing import List
from fastapi import HTTPException
from ..schemas.review import Review, ReviewUpdate, ReviewCreate
from ..repos.reviewRepo import loadAll, saveAll
from ..repos import movieRepo

def searchReviews(query: str) -> List[Review]:
    """ Searches reviews by movie title (case-insensitive) or by movie ID 
    
    Returns:
        Reviews that match the search
    """
    strippedQuery = (query or "").strip().lower()
    if not strippedQuery:
        return []

    reviews = loadAll()
    movies = movieRepo.loadAll()
    matched_reviews = []

    # If query is a number, treat as movie ID
    if strippedQuery.isdigit():
        movie_id = int(strippedQuery)
        for review in reviews:
            if review.movieId == movie_id:
                matched_reviews.append(Review(**review))
        return matched_reviews

    matching_movie_ids = [
        movie["id"] for movie in movies
        if strippedQuery in str(movie.get("title", "")).lower()
    ]

    for review in reviews:
        if review.moveiId in matching_movie_ids:
            matched_reviews.append(Review(**review))

    return matched_reviews

def listReviews() -> List[Review]:
    """ Lists all reviews currently stored """
    return [Review(**it) for it in loadAll()]

def createReview(payload: ReviewCreate) -> Review:
    """ 
    Creates a new review and saves it according to our review schema 

    Returns: 
        New review
    
    Raises: 
        HTTPException: id collision error if theres a duplicate
    """
    reviews = loadAll()

    if reviews:
        newId = max([int(r.get("id", 0)) for review in reviews]) + 1
    else:
        newId = 1

    if any(it.get("id") == newId for it in reviews):
        raise HTTPException(status_code=409, detail="ID collision; retry.")
    
    newReview = Review(
        id=newId, 
        movieId=payload.movieId, 
        userId=payload.userId,
        reviewTitle=payload.reviewTitle.strip(), 
        rating=payload.rating if isinstance(payload.rating, int) else int(payload.rating),
        reviewBody=payload.reviewBody.strip(),
        flagged=payload.flagged or False,
    )
    
    newData = newReview.model_dump()
    newData["flagged"] = payload.flagged or False
    reviews.append(newReview.model_dump())
    saveAll(reviews)
    return newReview

def getReviewById(reviewId: int) -> Review:
    """ 
    Retrieves a review by its ID

    Returns: 
        The review
    
    Raises: 
        HTTPException: review not found
    """
    reviews = loadAll()

    for review in reviews:
        if review.id == reviewId:
            return Review(**review)
    raise HTTPException(status_code=404, detail=f"Review '{reviewId}' not found")

def updateReview(reviewId: int, payload: ReviewUpdate) -> Review:
    """ 
    Updates an existing review identified by its ID

    Returns: 
        The updated review
    
    Raises: 
        HTTPException: review not found
    """  
    reviews = loadAll()
    for idx, it in enumerate(reviews):
        if it.get("id") == reviewId:
            current_review = Review(**it)
            update_data = payload.model_dump(exclude_unset=True)
            
            updated_dict = current_review.model_dump()
            updated_dict.update(update_data)
            
            if 'reviewTitle' in update_data and updated_dict['reviewTitle']:
                updated_dict['reviewTitle'] = updated_dict['reviewTitle'].strip()
            if 'reviewBody' in update_data and updated_dict['reviewBody']:
                updated_dict['reviewBody'] = updated_dict['reviewBody'].strip()
            if 'rating' in update_data and updated_dict['rating']:
                updated_dict['rating'] = int(updated_dict['rating'])
            
            updated = Review(**updated_dict)
            reviews[idx] = updated.model_dump()
            saveAll(reviews)
            return updated
    raise HTTPException(status_code=404, detail=f"Review '{reviewId}' not found")

def deleteReview(reviewId: int) -> None:
    """ 
    Deletes a review by its ID

    Raises: 
        HTTPException: review not found
    """  
    reviews = loadAll()
    newReviews = [review for review in reviews if review.id != reviewId]

    if len(newReviews) == len(reviews):
        raise HTTPException(status_code=404, detail=f"Review '{reviewId}' not found")
    
    saveAll(newReviews)
