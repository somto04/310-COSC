from fastapi import FastAPI
from app.routers import movieRoute, reviewRoute, userRoute, auth


app = FastAPI(title = "SpoilerAlert API")

app.include_router(movieRoute.router)
app.include_router(reviewRoute.router)
app.include_router(userRoute.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Hello from SpoilerAlert!"}
