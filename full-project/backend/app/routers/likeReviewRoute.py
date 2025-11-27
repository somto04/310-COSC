from fastapi import APIRouter, Depends, HTTPException
from ..services.likeReviewService import (likeReview, unlikeReview, getLikedReviews) #waiting implementation
from ..schemas.user import CurrentUser
from ..routers.authRoute import getCurrentUser