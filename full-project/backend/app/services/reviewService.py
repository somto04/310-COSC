import uuid
from typing import List
from fastapi import HTTPException
from ..schemas.review import Review, ReviewUpdate, ReviewCreate
from ..repos.reviewRepo import loadAll, saveAll

def listReviews() -> List[Review]:
    """
    MODIFIES: None
    EFFECTS:  Returns a list of Review objects. 
              Raises HTTPException if loading fails.

    The code below does the same as: 
        result = []
        for review in loadAll():
            result.append(Review(**review))
        return result

    loadAll() returns a list of dicts, each dict representing a review.

    doing **review unpacks the dict into keyword arguments 
    for the Review constructor, which is then appended to the result list.
    """
    return [Review(**review) for review in loadAll()]

def createReview(payload: ReviewCreate) -> Review:
    """
    REQUIRES: payload is a valid ReviewCreate object
    MODIFIES: reviews.json file to add new review
    EFFECTS:  Creates a new Review object from the payload, assigns it a unique ID,
              saves it to the reviews.json file, and returns the created Review object.
              Raises HTTPException on ID conflict.
    """
    # Load existing reviews (as list of dicts)
    reviews = loadAll()
    # Generate a new unique ID for the review using uuid4
    newId = str(uuid.uuid4())

    # if any existing review has the same ID, raise conflict error
    if any(review.get("id") == newId for review in reviews):
        raise HTTPException(status_code=409, detail="ID collision; retry.")
    
    # Create the new Review object using the provided payload
    # Strip whitespace from string fields with .strip()
    # id is generated above (since client wouldn't provide it)
    newReview = Review(id = newId, 
                        movieId = payload.movieId, 
                        userId = payload.userId,
                        reviewTitle = payload.reviewTitle.strip(), 
                        reviewBody = payload.reviewBody.strip(),
                        rating = payload.rating.strip(),
                        flagged = payload.flagged)
    
    # Append the new review (as dict) to the list and save
    reviews.append(newReview.dict())
    saveAll(reviews)
    return newReview

def getReviewById(reviewId: str) -> Review:
    """
    MODIFIES: None
    EFFECTS:  Retrieves a Review object by its ID. 
              Raises HTTPException if the review is not found.
    """

    # Load all reviews (as list of dicts)
    reviews = loadAll()

    # go through each review dict and if the ID matches, 
    # unpack it into a Review object and return it
    for review in reviews:
        if review.get("id") == reviewId:
            return Review(**review)
    raise HTTPException(status_code=404, detail=f"Review '{reviewId}' not found")

def updateReview(reviewId: str, payload: ReviewUpdate) -> Review:
    """
    REQUIRES: payload is a valid ReviewUpdate object
    MODIFIES: reviews.json file to update existing review
    EFFECTS:  Updates an existing Review object identified by reviewId, '
                returns the updated Review object.
    """

    # Load all reviews (as list of dicts)
    reviews = loadAll()

    # for each review and its index, go through the reviews
    # if the ID matches reviewId, create an updated Review object
    for index, review in enumerate(reviews):
        if review.get("id") == reviewId:
            # Only include fields from payload that were actually provided
            updated = payload.dict(exclude_unset=True)

            # Merge existing data in review + updated + reassign the id
            # this way we don't lose any fields not included 
            # in the payload if the client does not provide them
            # guarantee the id remains unchanged
            merged = {**review, **updated, "id": reviewId}
            
            # Create a Review object from the merged data (unpacking the dict)
            updated = Review(**merged)

            # Update the review in the list and save to the json file
            reviews[index] = updated.dict()
            saveAll(reviews)
            return updated
    # If we finish the loop without finding the review, raise 404
    raise HTTPException(status_code=404, detail=f"Review '{reviewId}' not found")

def deleteReview(reviewId: str) -> None:
    """
    MODIFIES: reviews.json file to remove existing review
    EFFECTS:  Deletes the Review object identified by reviewId. 
              Raises HTTPException if the review is not found.
    """

    # Load all reviews (as list of dicts)
    reviews = loadAll()

    # Filter out the review with the matching ID
    newReviews = [review for review in reviews if review.get("id") != reviewId]

    # If no review was removed, raise 404
    if len(newReviews) == len(reviews):
        raise HTTPException(status_code=404, detail=f"Review '{reviewId}' not found")
    
    saveAll(newReviews)