from fastapi import FastAPI
from app.routers import movieRoute, reviewRoute, userRoute


app = FastAPI(title = "SpoilerAlert API")

app.include_router(movieRoute.router)
app.include_router(reviewRoute.router)
app.include_router(userRoute.router)

@app.get("/")
def root():
    return {"message": "Hello from SpoilerAlert!"}
