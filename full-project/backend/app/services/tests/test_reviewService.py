import pytest
from fastapi import HTTPException
from unittest.mock import patch, MagicMock
from app.services import reviewService
from ...schemas.movie import Movie
from app.schemas.review import Review, ReviewCreate, ReviewUpdate

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
            flagged= False
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
        )
    ]

@pytest.fixture
def fakeMovies():
    """this fixture provides mock movies data for testing"""
    return [
        {"id":10, "title":"Avengers", "movieGenre" :["Action"], "duration": 143},
        {"id":11, "title":"Batman", "movieGenre" :["Action"], "duration":126},
    ]

# patching the loadReviews and saveReviews methods to avoid actual file I/O during tests
@patch("app.services.reviewService.loadReviews")
@patch("app.services.reviewService.movieRepo.loadAll")
def test_search_by_movie_id(mockMovieLoad, mockReviewLoad, fakeReviews, fakeMovies):
    """this test checks searching reviews by movie ID """
    mockReviewLoad.return_value = fakeReviews
    mockMovieLoad.return_value = fakeMovies

    result = reviewService.searchReviews("10")

    assert len(result) == 1
    assert result[0].reviewTitle == "Good movie"

@patch("app.services.reviewService.loadReviews")
@patch("app.services.reviewService.movieRepo.loadAll")
def test_search_by_movie_title(mockMovieLoad, mockReviewLoad, fakeReviews, fakeMovies):
    """this test checks searching reviews by movie title """
    mockReviewLoad.return_value = fakeReviews
    mockMovieLoad.return_value = fakeMovies

    result = reviewService.searchReviews("batman")
    assert len(result) == 1
    assert result[0].reviewTitle == "Fun, entertaining and more than worth a watch"

@patch("app.services.reviewService.loadReviews")
def test_list_reviews(mockLoad, fakeReviews):
    """this test checks that all reviews are listed correctly"""
    mockLoad.return_value = fakeReviews
    result = reviewService.listReviews()
    assert len(result) == 2
    assert all(isinstance(review, Review) for review in result)

@patch("app.services.reviewService.saveReviews")
@patch("app.services.reviewService.loadReviews")
def test_create_review(mockLoad, mockSave, fakeReviews):
    mockLoad.return_value = fakeReviews

    payload = ReviewCreate(
        reviewTitle="New Review",
        reviewBody="Loved it!!!!!!!!!!!",
        rating=9,
    )

    new_review = reviewService.createReview(12, 50001, payload)

    assert new_review.movieId == 12
    assert new_review.reviewTitle == "New Review"
    mockSave.assert_called_once()



@patch("app.services.reviewService.loadReviews")
def test_get_review_by_id_found(mockLoad, fakeReviews):
    """this test checks getting a review by its ID"""
    mockLoad.return_value = fakeReviews
    review = reviewService.getReviewById(1)
    assert review.reviewTitle == "Good movie"

@patch("app.services.reviewService.loadReviews")
def test_get_review_by_id_not_found(mockLoad):
    """this test checks handling when a review ID is not found and throws a 404 error"""
    mockLoad.return_value = []
    with pytest.raises(HTTPException) as exc:
        reviewService.getReviewById(999)
    assert exc.value.status_code == 404

@patch("app.services.reviewService.saveReviews")
@patch("app.services.reviewService.loadReviews")
def test_update_review(mockLoad, mockSave, fakeReviews):
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
def test_update_review_not_found(mockLoad, mockSave):
    mockLoad.return_value = []

    payload = ReviewUpdate(
        reviewTitle="Hi everyone",
        reviewBody="Testing review update!!!!!!!!!!!",
        rating=10,
    )

    with pytest.raises(HTTPException):
        reviewService.updateReview(999, payload)


# this test checks deleting a review successfully
@patch("app.services.reviewService.saveReviews")
@patch("app.services.reviewService.loadReviews")
def test_delete_review_success(mockLoad, mockSave, fakeReviews):
    mockLoad.return_value = fakeReviews
    reviewService.deleteReview(1)
    mockSave.assert_called_once()

# this test checks handling when trying to delete a non-existent review and throws a 404 error
@patch("app.services.reviewService.saveReviews")
@patch("app.services.reviewService.loadReviews")
def test_delete_review_not_found(mockLoad, mockSave, fakeReviews):
    mockLoad.return_value = fakeReviews
    with pytest.raises(HTTPException) as exc:
        reviewService.deleteReview(999)
    assert exc.value.status_code == 404
