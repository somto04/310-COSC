from fastapi import APIRouter, status, Depends, HTTPException, Form
from app.routers.auth import getCurrentUser  # small fix to remove ".py" in import

router = APIRouter()

@router.get("/adminDashboard")
def getAdminDashboard(currentUser=Depends(getCurrentUser)):
    if currentUser["role"] == "admin":
        return {"message": "Welcome to the admin dashboard"}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )


@router.post("/logout")
def logout(currentUser=Depends(getCurrentUser)):
    """
    Logs the current user out by clearing or invalidating their token/session.
    """
    # In a real app, you might remove or blacklist the token here
    return {
        "message": f"User '{currentUser['username']}' has been logged out successfully."
    }
