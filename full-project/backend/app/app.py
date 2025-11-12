from fastapi import FastAPI
from app.routers import movieRoute, reviewRoute, userRoute, auth, replyRoute, loginRoute
from app.externalAPI import tmdbRouter
# Create FastAPI instance w the name of our project
app = FastAPI(title = "SpoilerAlert API")

# Include routers for different modules
app.include_router(movieRoute.router)
app.include_router(reviewRoute.router)
app.include_router(userRoute.router)
app.include_router(auth.router)
app.include_router(replyRoute.router)
app.include_router(tmdbRouter.router)
app.include_router(loginRoute.router)
# Basic root endpoint to verify API is running
@app.get("/")
def root():
    return {"message": "Hello from SpoilerAlert!"}
