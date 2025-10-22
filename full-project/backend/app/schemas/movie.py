# ...existing code...
from pydantic import BaseModel, Field, root_validator
from typing import List, Optional

class Movie(BaseModel):
    id: str
    title: str
    yearReleased: int
    actors: List[str] = Field(default_factory=list)
    genre: str
    duration: int  # minutes

    @root_validator(pre=True)
    def accept_legacy_keys(cls, values):
        # id: accept movieId or coerce numeric id -> str
        if "movieId" in values and "id" not in values:
            values["id"] = str(values.pop("movieId"))
        if "id" in values:
            values["id"] = str(values["id"])

        # title alias
        if "movieName" in values and "title" not in values:
            values["title"] = values.pop("movieName")

        # actors alias (mainStars)
        if "mainStars" in values and "actors" not in values:
            values["actors"] = values.pop("mainStars")

        # genre: take first movieGenres item or join if needed
        if "movieGenres" in values and "genre" not in values:
            mg = values.pop("movieGenres")
            if isinstance(mg, list) and mg:
                values["genre"] = mg[0]
            else:
                values["genre"] = str(mg or "")

        # datePublished -> yearReleased (extract year)
        if "datePublished" in values and "yearReleased" not in values:
            dp = values.get("datePublished")
            try:
                values["yearReleased"] = int(str(dp).split("-")[0])
            except Exception:
                # fallback if yearReleased present or unknown
                values["yearReleased"] = int(values.get("yearReleased") or 0)

        # support alias length -> duration
        if "length" in values and "duration" not in values:
            values["duration"] = values.pop("length")

        # ensure minimal defaults so validation succeeds
        values.setdefault("actors", values.get("actors", []))
        values.setdefault("genre", values.get("genre", ""))
        values.setdefault("duration", int(values.get("duration") or 0))
        values.setdefault("yearReleased", int(values.get("yearReleased") or 0))

        return values

class MovieCreate(BaseModel):
    title: str
    yearReleased: int
    actors: List[str] = Field(default_factory=list)
    genre: str
    duration: int

    @root_validator(pre=True)
    def accept_legacy_create_keys(cls, values):
        if "movieName" in values and "title" not in values:
            values["title"] = values.pop("movieName")
        if "length" in values and "duration" not in values:
            values["duration"] = values.pop("length")
        if "mainStars" in values and "actors" not in values:
            values["actors"] = values.pop("mainStars")
        if "movieGenres" in values and "genre" not in values:
            mg = values.pop("movieGenres")
            values["genre"] = mg[0] if isinstance(mg, list) and mg else str(mg or "")
        if "datePublished" in values and "yearReleased" not in values:
            dp = values.get("datePublished")
            try:
                values["yearReleased"] = int(str(dp).split("-")[0])
            except Exception:
                values["yearReleased"] = int(values.get("yearReleased") or 0)
        return values

class MovieUpdate(BaseModel):
    title: Optional[str] = None
    yearReleased: Optional[int] = None
    actors: Optional[List[str]] = None
    genre: Optional[str] = None
    duration: Optional[int] = None
# ...existing code...