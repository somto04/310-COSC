from fastapi import APIRouter, Depends, HTTPException
from ..services.reviewService import (
    deleteReview,
    getReviewById,
    ReviewNotFoundError,
    unflagReview,
    getFlaggedReviews,
)
from ..utilities.penalties import incrementPenaltyForUser
from ..schemas.user import CurrentUser
from .authRoute import requireAdmin
from ..schemas.admin import AdminFlagResponse, PaginatedFlaggedReviewsResponse
from ..services.adminService import grantAdmin, revokeAdmin, AdminActionError
from app.services.userService import UserNotFoundError

router = APIRouter(prefix="/admin", tags=["admin"])


# ---------------------------
# Accept flag and delete review
# ---------------------------


@router.post("/reviews/{reviewId}/acceptFlag", response_model=AdminFlagResponse)
def acceptReviewFlag(reviewId: int, currentAdmin: CurrentUser = Depends(requireAdmin)):
    """Accept a review flag, delete the review, and penalize the user."""
    try:
        review = getReviewById(reviewId)
    except ReviewNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    if not review.flagged:
        raise HTTPException(
            status_code=400, detail="Cannot accept flag. Review is not flagged."
        )

    updatedUser = incrementPenaltyForUser(review.userId)
    deleteReview(reviewId)

    return AdminFlagResponse(
        message="Review flag accepted. Review deleted and user penalized.",
        userId=updatedUser.id,
        penaltyCount=updatedUser.penalties,
        isBanned=updatedUser.isBanned,
    )


# ---------------------------
# Reject flag
# ---------------------------


@router.post("/reviews/{reviewId}/rejectFlag", response_model=AdminFlagResponse)
def rejectReviewFlag(reviewId: int, currentAdmin: CurrentUser = Depends(requireAdmin)):
    """Reject a review flag and unflag the review."""
    try:
        review = getReviewById(reviewId)
    except ReviewNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    if not review.flagged:
        raise HTTPException(
            status_code=400,
            detail="Cannot reject flag. Review is not flagged.",
        )

    updatedReview = unflagReview(reviewId)

    return AdminFlagResponse(
        message="Flag rejected. Review unflagged (no penalty applied).",
        userId=updatedReview.userId,
        penaltyCount=0,
        isBanned=False,
    )


# ---------------------------
# Paginated flagged review reports
# ---------------------------


@router.get("/reports/reviews", response_model=PaginatedFlaggedReviewsResponse)
def getFlaggedReviewReports(
    page: int = 1,
    pageSize: int = 20,
    currentAdmin: CurrentUser = Depends(requireAdmin),
):
    flaggedReviewList = getFlaggedReviews()

    startIndex = (page - 1) * pageSize
    endIndex = startIndex + pageSize
    paginatedReviews = flaggedReviewList[startIndex:endIndex]

    return PaginatedFlaggedReviewsResponse(
        page=page,
        pageSize=pageSize,
        totalFlagged=len(flaggedReviewList),
        pageCount=(len(flaggedReviewList) + pageSize - 1) // pageSize,
        reviews=paginatedReviews,
    )


@router.put("/{userId}/grantAdmin")
def grantAdminPrivileges(
    userId: int, currentAdmin: CurrentUser = Depends(requireAdmin)
):
    """Grant admin privileges to a user."""
    try:
        updatedUser = grantAdmin(userId, currentAdmin)
    except AdminActionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {
        "message": "Admin privileges granted.",
        "userId": updatedUser.id,
        "role": updatedUser.role,
    }


@router.put("/{userId}/revokeAdmin")
def revokeAdminPrivileges(
    userId: int, currentAdmin: CurrentUser = Depends(requireAdmin)
):
    """Revoke admin privileges from a user."""
    try:
        updatedUser = revokeAdmin(userId, currentAdmin)
    except AdminActionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {
        "message": "Admin privileges revoked.",
        "userId": updatedUser.id,
        "role": updatedUser.role,
    }
