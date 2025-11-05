import uuid
from typing import List
from fastapi import HTTPException
from ..schemas.review import Review, ReviewUpdate, ReviewCreate
from ..repos.reviewRepo import loadAll, saveAll
from ..repos import movieRepo

# this function searches reviews by movie title (case-insensitive) or by movie ID
def searchReviews(query: str) -> List[Review]:
    
    q = (query or "").strip().lower()
    if not q:
        return []
    # Load all reviews and movies
    reviews = loadAll()
    movies = movieRepo.loadAll()
    matched_reviews = []

    # If query is a number, treat as movie ID
    if q.isdigit():
        for r in reviews:
            if str(r.get("movieId")) == q:
                matched_reviews.append(Review(**r))
        return matched_reviews

    # Otherwise, search for movie title 
    matching_movie_ids = [
        str(m["id"]) for m in movies
        if q in str(m.get("title", "")).lower()
    ]
    # Now find reviews for these movie IDs
    for r in reviews:
        if str(r.get("movieId")) in matching_movie_ids:
            matched_reviews.append(Review(**r))

    return matched_reviews

#this function lists all reviews currently stored
def listReviews() -> List[Review]:
    return [Review(**it) for it in loadAll()]

#this function creates a new review and saves it according to our review schema
def createReview(payload: ReviewCreate) -> Review:
    reviews = loadAll()
    # Generate a new unique ID for the review using uuid4
    newId = str(uuid.uuid4())
    if any(it.get("id") == newId for it in reviews):
        # if that ID already exists, raise a conflict error
        raise HTTPException(status_code=409, detail="ID collision; retry.")
    newReview = Review(id=newId, 
                   movieId = payload.movieId, 
                   userId= payload.userId,
                   reviewTitle = payload.reviewTitle.strip(), 
                   rating = payload.rating.strip(),
                   reviewBody = payload.reviewBody.strip(),
                   flagged = payload.flagged)
    
    newData = newReview.model_dump()
    newData["flagged"] = payload.flagged or False
    # Append the new review and save all reviews
    reviews.append(newReview.model_dump())
    saveAll(reviews)
    return newReview

#this function retrieves a review by its ID
def getReviewById(reviewId: str) -> Review:
    reviews = loadAll()

    # go through each review dict and if the ID matches, 
    # unpack it into a Review object and return it
    for review in reviews:
        if review.get("id") == reviewId:
            return Review(**review)
    # If no matching review is found, raise 404
    raise HTTPException(status_code=404, detail=f"Review '{reviewId}' not found")

#this function updates an existing review identified by its ID
def updateReview(reviewId: str, payload: ReviewUpdate) -> Review:
    reviews = loadAll()
    #idx enumerate to get both index and item
    for idx, it in enumerate(reviews):
        # if the ID matches, update only the provided fields
        if it.get("id") == reviewId:
            current_review = Review(**it)
            update_data = payload.model_dump(exclude_unset=True)
            
            # Create updated review by merging current data with update data
            updated_dict = current_review.model_dump()
            updated_dict.update(update_data)
            
            # Strip fields if they're provided
            if 'reviewTitle' in update_data and updated_dict['reviewTitle']:
                updated_dict['reviewTitle'] = updated_dict['reviewTitle'].strip()
            if 'reviewBody' in update_data and updated_dict['reviewBody']:
                updated_dict['reviewBody'] = updated_dict['reviewBody'].strip()
            if 'rating' in update_data and updated_dict['rating']:
                updated_dict['rating'] = updated_dict['rating'].strip()
            
            updated = Review(**updated_dict)
            reviews[idx] = updated.model_dump()
            saveAll(reviews)
            return updated
    # If we finish the loop without finding the review, raise 404
    raise HTTPException(status_code=404, detail=f"Review '{reviewId}' not found")

# this function deletes a review by its ID
def deleteReview(reviewId: str) -> None:
    reviews = loadAll()

    # Filter out the review with the matching ID
    newReviews = [review for review in reviews if review.get("id") != reviewId]

    # If no review was removed, raise 404
    if len(newReviews) == len(reviews):
        raise HTTPException(status_code=404, detail=f"Review '{reviewId}' not found")
    
    saveAll(newReviews)
