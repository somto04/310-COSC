#creates a mini FastAPI for organizing related movie routes
from fastapi import APIRouter, HTTPException 
# imports the List function from the typing moduel for list creation
from typing import List 
#import models from pydantic (library for data validation and settings management that uses Python's built-in type hints to validate data schemas)
from models import Movie, MovieCreate, MovieUpdate

#create a router instance (container for all movie related routes)
router = APIRouter(
    prefix="/movies",
    tags=["movies"]
)
