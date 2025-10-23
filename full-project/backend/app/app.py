from fastapi import FastAPI
from app.routers import movieRoute, reviewRoute, userRoute
from app.auth import router as authRouter


app = FastAPI(title = "SpoilerAlert API")

app.include_router(movieRoute.router)
app.include_router(reviewRoute.router)
app.include_router(userRoute.router)
app.include_router(authRouter)

@app.get("/")
def root():
    return {"message": "Hello from SpoilerAlert!"}
