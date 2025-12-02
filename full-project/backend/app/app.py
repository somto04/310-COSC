from fastapi import FastAPI
from app.routers import movieRoute, reviewRoute, userRoute, replyRoute, adminRoute, favoritesRoute, authRoute, likeReviewRoute
from app.externalAPI import tmdbRouter
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI instance w the name of our project
app = FastAPI(title = "SpoilerAlert API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/ping")
def ping():
    return {"ping": "pong"}

# Include routers for different modules
app.include_router(movieRoute.router)
app.include_router(reviewRoute.router)
app.include_router(userRoute.router)
app.include_router(favoritesRoute.router)
app.include_router(likeReviewRoute.router)
app.include_router(authRoute.router)
app.include_router(adminRoute.router)
app.include_router(replyRoute.router)
app.include_router(tmdbRouter.router)

# Basic root endpoint to verify API is running
@app.get("/")
def root():
    return {"message": "Hello from SpoilerAlert!"}
