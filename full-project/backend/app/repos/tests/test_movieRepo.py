from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

import app.repos.movieRepo as movieRepoModule
from app.repos.movieRepo import (
    _getMaxMovieId,
    _loadMovieCache,
    getNextMovieId,
    loadMovies,
    saveMovies,
)
from app.schemas.movie import Movie
from decimal import Decimal
import json
from datetime import date

@pytest.fixture(autouse=True)
def resetMovieRepoState():
    movieRepoModule._MOVIE_CACHE = None
    movieRepoModule._NEXT_MOVIE_ID = None
    yield
    movieRepoModule._MOVIE_CACHE = None
    movieRepoModule._NEXT_MOVIE_ID = None


def testGetMaxMovieIdEmptyListReturnsZero():
    resultValue = _getMaxMovieId([])
    assert resultValue == 0


def testGetMaxMovieIdReturnsMaxIdFromMovies():
    movieList = [
        SimpleNamespace(id=3),
        SimpleNamespace(id=10),
        SimpleNamespace(id=5),
    ]
    resultValue = _getMaxMovieId(movieList)
    assert resultValue == 10


@patch("app.repos.movieRepo._baseLoadAll")
def testLoadMovieCacheInitializesCacheAndNextId(mockBaseLoadAll, monkeypatch):
    movieData = [
        {"id": 10, "title": "A"},
        {"id": 20, "title": "B"},
    ]
    mockBaseLoadAll.return_value = movieData

    class DummyMovie:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    monkeypatch.setattr(movieRepoModule, "Movie", DummyMovie)
    with patch("app.repos.movieRepo._getMaxMovieId", return_value=20):
        resultMovies = _loadMovieCache()

    assert isinstance(resultMovies[0], DummyMovie)
    assert len(resultMovies) == 2
    assert movieRepoModule._MOVIE_CACHE is resultMovies
    assert movieRepoModule._NEXT_MOVIE_ID == 21
    mockBaseLoadAll.assert_called_once_with(movieRepoModule.MOVIE_DATA_PATH)


@patch("app.repos.movieRepo._baseLoadAll")
def testLoadMovieCacheUsesCachedValueOnSecondCall(mockBaseLoadAll, monkeypatch):
    movieData = [{"id": 1}]

    class DummyMovie:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    mockBaseLoadAll.return_value = movieData
    monkeypatch.setattr(movieRepoModule, "Movie", DummyMovie)

    firstResult = _loadMovieCache()
    mockBaseLoadAll.reset_mock()
    secondResult = _loadMovieCache()

    assert firstResult is secondResult
    mockBaseLoadAll.assert_not_called()


def testGetNextMovieIdUsesExistingNextIdWithoutLoading(monkeypatch):
    fakeLoad = MagicMock()
    monkeypatch.setattr(movieRepoModule, "_loadMovieCache", fakeLoad)
    movieRepoModule._NEXT_MOVIE_ID = 10

    firstResult = getNextMovieId()
    secondResult = getNextMovieId()

    assert firstResult == 10
    assert secondResult == 11
    assert movieRepoModule._NEXT_MOVIE_ID == 12
    fakeLoad.assert_not_called()


def testGetNextMovieIdInitializesFromLoadWhenNextIdIsNone(monkeypatch):
    def fakeLoad():
        movieRepoModule._NEXT_MOVIE_ID = 7
        return []

    monkeypatch.setattr(movieRepoModule, "_loadMovieCache", fakeLoad)
    movieRepoModule._NEXT_MOVIE_ID = None

    resultValue = getNextMovieId()
    assert resultValue == 7
    assert movieRepoModule._NEXT_MOVIE_ID == 8


def testLoadMoviesDelegatesToLoadMovieCache(monkeypatch):
    movieList = [SimpleNamespace(id=1)]

    def fakeLoad():
        return movieList

    monkeypatch.setattr(movieRepoModule, "_loadMovieCache", fakeLoad)
    resultMovies = loadMovies()
    assert resultMovies is movieList


@patch("app.repos.movieRepo._baseSaveAll")
def testSaveMoviesUpdatesCacheAndNextIdWhenNone(mockBaseSaveAll):
    movieRepoModule._NEXT_MOVIE_ID = None

    class DummyMovie:
        def __init__(self, movieId, dataDict):
            self.id = movieId
            self.dataDict = dataDict

        def model_dump(self):
            return self.dataDict

    movieList = [
        DummyMovie(1, {"id": 1}),
        DummyMovie(2, {"id": 2}),
    ]

    with patch("app.repos.movieRepo._getMaxMovieId", return_value=5):
        saveMovies(movieList)

    assert movieRepoModule._MOVIE_CACHE is movieList
    assert movieRepoModule._NEXT_MOVIE_ID == 6
    mockBaseSaveAll.assert_called_once_with(
        movieRepoModule.MOVIE_DATA_PATH,
        [{"id": 1}, {"id": 2}],
    )


@patch("app.repos.movieRepo._baseSaveAll")
def testSaveMoviesIncreasesNextIdWhenLessOrEqualToMax(mockBaseSaveAll):
    movieRepoModule._NEXT_MOVIE_ID = 3

    class DummyMovie:
        def __init__(self, movieId, dataDict):
            self.id = movieId
            self.dataDict = dataDict

        def model_dump(self):
            return self.dataDict

    movieList = [DummyMovie(10, {"id": 10})]

    with patch("app.repos.movieRepo._getMaxMovieId", return_value=10):
        saveMovies(movieList)

    assert movieRepoModule._MOVIE_CACHE is movieList
    assert movieRepoModule._NEXT_MOVIE_ID == 11
    mockBaseSaveAll.assert_called_once_with(
        movieRepoModule.MOVIE_DATA_PATH,
        [{"id": 10}],
    )


@patch("app.repos.movieRepo._baseSaveAll")
def testSaveMoviesKeepsNextIdWhenGreaterThanMax(mockBaseSaveAll):
    movieRepoModule._NEXT_MOVIE_ID = 20

    class DummyMovie:
        def __init__(self, movieId, dataDict):
            self.id = movieId
            self.dataDict = dataDict

        def model_dump(self):
            return self.dataDict

    movieList = [DummyMovie(5, {"id": 5})]

    with patch("app.repos.movieRepo._getMaxMovieId", return_value=10):
        saveMovies(movieList)

    assert movieRepoModule._MOVIE_CACHE is movieList
    assert movieRepoModule._NEXT_MOVIE_ID == 20
    mockBaseSaveAll.assert_called_once_with(
        movieRepoModule.MOVIE_DATA_PATH,
        [{"id": 5}],
    )

# INTEGRATION TESTS BELOW

@pytest.fixture
def movieDataPath(tmp_path, monkeypatch):
    tempFilePath = tmp_path / "movies.json"
    initialMovies = [
        {
            "id": 1,
            "title": "First Movie",
            "movieIMDbRating": 7.5,
            "movieGenres": ["Action"],
            "directors": ["Director One"],
            "mainstars": ["Star One"],
            "description": "First movie description",
            "duration": 120,
            "yearReleased": 2010,
        },
        {
            "id": 5,
            "title": "Second Movie",
            "movieIMDbRating": 8.3,
            "movieGenres": ["Drama"],
            "directors": ["Director Two"],
            "mainstars": ["Star Two"],
            "description": "Second movie description",
            "duration": 90,
            "yearReleased": 2015,
        },
    ]
    tempFilePath.write_text(json.dumps(initialMovies))
    monkeypatch.setattr(movieRepoModule, "MOVIE_DATA_PATH", tempFilePath)
    movieRepoModule._MOVIE_CACHE = None
    movieRepoModule._NEXT_MOVIE_ID = None
    return tempFilePath


def testIntegrationLoadMoviesParsesJsonIntoMovieModelsWithFields(movieDataPath):
    movieList = loadMovies()

    assert len(movieList) == 2
    assert isinstance(movieList[0], Movie)
    assert isinstance(movieList[1], Movie)

    firstMovie = movieList[0]
    secondMovie = movieList[1]

    assert firstMovie.id == 1
    assert firstMovie.title == "First Movie"
    assert firstMovie.movieIMDbRating == Decimal("7.5")
    assert firstMovie.movieGenres == ["Action"]
    assert firstMovie.directors == ["Director One"]
    assert firstMovie.mainStars == ["Star One"]
    assert firstMovie.description == "First movie description"
    assert firstMovie.duration == 120
    assert firstMovie.yearReleased == 2010

    assert secondMovie.id == 5
    assert secondMovie.title == "Second Movie"
    assert secondMovie.movieIMDbRating == Decimal("8.3")
    assert secondMovie.movieGenres == ["Drama"]
    assert secondMovie.directors == ["Director Two"]
    assert secondMovie.mainStars == ["Star Two"]
    assert secondMovie.description == "Second movie description"
    assert secondMovie.duration == 90
    assert secondMovie.yearReleased == 2015


def testIntegrationGetNextMovieIdUsesExistingFileData(movieDataPath):
    firstId = getNextMovieId()
    secondId = getNextMovieId()

    assert firstId == 6
    assert secondId == 7


def testIntegrationSaveMoviesPersistsAllFieldsAndAdvancesNextId(movieDataPath):
    movieList = loadMovies()
    newMovieId = getNextMovieId()

    newMovie = Movie(
        id=newMovieId,
        title="Third Movie",
        movieIMDbRating=Decimal("9.0"),
        movieGenres=["Action", "Sci-Fi"],
        directors=["Director Three"],
        mainStars=["Star Three"],
        description="Third movie description",
        duration=130,
        yearReleased=2024,
        datePublished=date(2024, 1, 1),
    )
    movieList.append(newMovie)

    saveMovies(movieList)

    reloadedMovieList = loadMovies()
    assert len(reloadedMovieList) == 3
    reloadedIds = [movieItem.id for movieItem in reloadedMovieList]
    assert newMovieId in reloadedIds

    storedJson = json.loads(movieDataPath.read_text())
    assert len(storedJson) == 3

    storedById = {item["id"]: item for item in storedJson}
    assert newMovieId in storedById

    storedNew = storedById[newMovieId]
    assert storedNew["title"] == "Third Movie"
    assert storedNew["movieIMDbRating"] == 9.0
    assert storedNew["movieGenres"] == ["Action", "Sci-Fi"]
    assert storedNew["directors"] == ["Director Three"]
    assert storedNew["mainStars"] == ["Star Three"]
    assert storedNew["description"] == "Third movie description"
    assert storedNew["duration"] == 130
    assert storedNew["yearReleased"] == 2024

    nextAfterSave = getNextMovieId()
    assert nextAfterSave == newMovieId + 1
