import pytest
from fastapi import HTTPException
from unittest.mock import patch, MagicMock
from app.services import reviewService
from ...schemas.movie import Movie
from app.schemas.review import Review, ReviewCreate, ReviewUpdate
from app.services.reviewService import ReviewNotFoundError
from ...repos import reviewRepo

@pytest.fixture
def fakeReviews():
    """ provides mock reviews data for testing that follows our review schema"""
    return [
        Review(
            id= 1,
            movieId= 10,
            userId= 40846,
            reviewTitle= "Good movie",
            reviewBody= "Excellent really made me love Thor, answered a bunch of questions and tied things together. A must see.",
            rating= 10,
            datePosted= "8 April 2018",
            flagged= True
        ),
        Review(
            id= 2,
            movieId= 11,
            userId= 40847,
            reviewTitle= "Fun, entertaining and more than worth a watch",
            reviewBody= "Sometimes you watch a film and you remember why you love the movies so much.",
            rating= 8,
            datePosted= "10 April 2018",
            flagged= False
        ),
        Review(
            id= 3,
            movieId= 10,
            userId= 40848,
            reviewTitle= "Not my type of movie",
            reviewBody= "I found this movie quite boring and predictable.",
            rating= 5,
            datePosted= "12 April 2018",
            flagged= True
        ),
    ]

@pytest.fixture
def fakeMovies():
    """this fixture provides mock movies data for testing"""
    return [
        Movie(id=10, title="Avengers", movieGenres =["Action"], duration= 143),
        Movie(id=11, title="Batman", movieGenres =["Action"], duration=126),
    ]

# patching the loadReviews and saveReviews methods to avoid actual file I/O during tests
@patch("app.services.reviewService.loadReviews")
@patch("app.services.reviewService.movieRepo.loadMovies")
def test_searchByMovieId(mockMovieLoad, mockReviewLoad, fakeReviews, fakeMovies):
    """this test checks searching reviews by movie ID """
    reviewRepo._REVIEW_CACHE = None
    reviewRepo._NEXT_REVIEW_ID = None

    mockReviewLoad.return_value = fakeReviews
    mockMovieLoad.return_value = fakeMovies

    result = reviewService.searchReviews("10")

    assert len(result) == 2
    assert result[0].reviewTitle == "Good movie"

@patch("app.services.reviewService.loadReviews")
@patch("app.services.reviewService.movieRepo.loadMovies")
def test_searchByMovieTitle(mockMovieLoad, mockReviewLoad, fakeReviews, fakeMovies):
    """this test checks searching reviews by movie title """
    mockReviewLoad.return_value = fakeReviews
    mockMovieLoad.return_value = fakeMovies

    result = reviewService.searchReviews("batman")
    assert len(result) == 1
    assert result[0].reviewTitle == "Fun, entertaining and more than worth a watch"

@patch("app.services.reviewService.loadReviews")
def test_listReviews(mockLoad, fakeReviews):
    """this test checks that all reviews are listed correctly"""
    mockLoad.return_value = fakeReviews
    result = reviewService.listReviews()
    assert len(result) == 3
    assert all(isinstance(review, Review) for review in result)

@patch("app.services.reviewService.getNextReviewId")
@patch("app.services.reviewService.loadReviews")
@patch("app.services.reviewService.saveReviews")
def test_createReview(mockSave, mockLoad, mockNextId, fakeReviews):

    """this test checks creating a new review according to our review schema"""
    mockLoad.return_value = fakeReviews
    mockNextId.return_value = 100

    payload = ReviewCreate(
        reviewTitle="New Review",
        reviewBody="Loved it!!!!!!!!!!!",
        rating=9,
    )

    newReview = reviewService.createReview(12, 50001, payload)

    assert newReview.movieId == 12
    assert newReview.reviewTitle == "New Review"
    assert newReview.id == 100
    mockSave.assert_called_once()



@patch("app.services.reviewService.loadReviews")
def test_getReviewByIdFound(mockLoad, fakeReviews):
    """this test checks getting a review by its ID"""
    mockLoad.return_value = fakeReviews
    review = reviewService.getReviewById(1)
    assert review.reviewTitle == "Good movie"

@patch("app.services.reviewService.loadReviews")
def test_getReviewByIdNotFound(mockLoad):
    """this test checks handling when a review ID is not found and throws a 404 error"""
    mockLoad.return_value = []
    with pytest.raises(ReviewNotFoundError) as exc:
        reviewService.getReviewById(999)

@patch("app.services.reviewService.saveReviews")
@patch("app.services.reviewService.loadReviews")
def test_updateReview(mockLoad, mockSave, fakeReviews):
    """this test checks updating an existing review"""
    mockLoad.return_value = fakeReviews

    payload = ReviewUpdate(
        reviewTitle="Updated title",
        reviewBody="Amazing!!!!!!!!!!!",
        rating=10,
    )

    updated = reviewService.updateReview(1, payload)

    assert updated.reviewTitle == "Updated title"
    mockSave.assert_called_once()


# this test checks handling when trying to update a non-existent review and throws a 404 error
@patch("app.services.reviewService.saveReviews")
@patch("app.services.reviewService.loadReviews")
def test_updateReviewNotFound(mockLoad, mockSave):
    mockLoad.return_value = []

    payload = ReviewUpdate(
        reviewTitle="Hi everyone",
        reviewBody="Testing review update!!!!!!!!!!!",
        rating=10,
    )

    with pytest.raises(ReviewNotFoundError):
        reviewService.updateReview(999, payload)


# this test checks deleting a review successfully
@patch("app.services.reviewService.saveReviews")
@patch("app.services.reviewService.loadReviews")
def test_deleteReviewSuccess(mockLoad, mockSave, fakeReviews):
    mockLoad.return_value = fakeReviews
    reviewService.deleteReview(1)
    mockSave.assert_called_once()

# this test checks handling when trying to delete a non-existent review and throws a 404 error
@patch("app.services.reviewService.saveReviews")
@patch("app.services.reviewService.loadReviews")
def test_deleteReviewNotFound(mockLoad, mockSave, fakeReviews):
    mockLoad.return_value = fakeReviews
    with pytest.raises(ReviewNotFoundError) as exc:
        reviewService.deleteReview(999)


@patch("app.services.reviewService.saveReviews")
@patch("app.services.reviewService.loadReviews")
def test_flagReviewSuccess(mockLoad, mockSave, fakeReviews):
    mockLoad.return_value = fakeReviews

    updated = reviewService.flagReview(2)

    assert updated.id == 2
    assert updated.flagged is True
    mockSave.assert_called_once()


@patch("app.services.reviewService.saveReviews")
@patch("app.services.reviewService.loadReviews")
def test_flagReviewNotFound(mockLoad, mockSave):
    mockLoad.return_value = []

    with pytest.raises(ReviewNotFoundError):
        reviewService.flagReview(999)

    mockSave.assert_not_called()

@patch("app.services.reviewService.loadReviews")
def test_getFlaggedReviews(mockLoad, fakeReviews):
    """this test checks retrieving all flagged reviews"""
    mockLoad.return_value = fakeReviews
    flagged = reviewService.getFlaggedReviews()

    assert len(flagged) == 2
    assert all(review.flagged is True for review in flagged)
