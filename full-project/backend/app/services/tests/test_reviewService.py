import pytest
import uuid
from fastapi import HTTPException
from unittest.mock import patch, MagicMock
from app.services import reviewService
from app.schemas.review import Review, ReviewCreate, ReviewUpdate


@pytest.fixture
def fake_reviews():
    return [
        {
            "id": "1",
            "movieId": 10,
            "userId": 40846,
            "reviewTitle": "Good movie",
            "reviewBody": "Excellent really made me love Thor, answered a bunch of questions and tied things together. A must see.",
            "rating": "10",
            "datePosted": "8 April 2018",
            "flagged": False,
        },
        {
            "id": "2",
            "movieId": 11,
            "userId": 40847,
            "reviewTitle": "Fun, entertaining and more than worth a watch",
            "reviewBody": "Sometimes you watch a film and you remember why you love the movies so much.",
            "rating": "8",
            "datePosted": "10 April 2018",
            "flagged": False,
        },
    ]


@pytest.fixture
def fake_movies():
    return [
        {"id": "10", "title": "Avengers"},
        {"id": "11", "title": "Batman"},
    ]


# --------------------------------------------------------------------
# search
# --------------------------------------------------------------------
@patch("app.services.reviewService.loadAll")
@patch("app.services.reviewService.movieRepo.loadAll")
def test_search_by_movie_id(mock_movie_load, mock_review_load, fake_reviews, fake_movies):
    mock_review_load.return_value = fake_reviews
    mock_movie_load.return_value = fake_movies

    result = reviewService.searchReviews("10")

    assert len(result) == 1
    assert result[0].reviewTitle == "Good movie"


@patch("app.services.reviewService.loadAll")
@patch("app.services.reviewService.movieRepo.loadAll")
def test_search_by_movie_title(mock_movie_load, mock_review_load, fake_reviews, fake_movies):
    mock_review_load.return_value = fake_reviews
    mock_movie_load.return_value = fake_movies

    result = reviewService.searchReviews("batman")
    assert len(result) == 1
    assert result[0].reviewTitle == "Fun, entertaining and more than worth a watch"


# --------------------------------------------------------------------
# list
# --------------------------------------------------------------------
@patch("app.services.reviewService.loadAll")
def test_list_reviews(mock_load, fake_reviews):
    mock_load.return_value = fake_reviews
    result = reviewService.listReviews()
    assert len(result) == 2
    assert all(isinstance(r, Review) for r in result)


# --------------------------------------------------------------------
# create
# --------------------------------------------------------------------
@patch("app.services.reviewService.saveAll")
@patch("app.services.reviewService.loadAll")
def test_create_review(mock_load, mock_save, fake_reviews):
    mock_load.return_value = fake_reviews

    payload = ReviewCreate(
        movieId=12,
        userId=50001,
        reviewTitle="New Review",
        rating="9",
        reviewBody="Loved it",
        flagged=False,
    )

    new_review = reviewService.createReview(payload)

    assert new_review.movieId == 12
    assert new_review.reviewTitle == "New Review"
    mock_save.assert_called_once()


# --------------------------------------------------------------------
# get
# --------------------------------------------------------------------
@patch("app.services.reviewService.loadAll")
def test_get_review_by_id_found(mock_load, fake_reviews):
    mock_load.return_value = fake_reviews
    review = reviewService.getReviewById("1")
    assert review.reviewTitle == "Good movie"


@patch("app.services.reviewService.loadAll")
def test_get_review_by_id_not_found(mock_load):
    mock_load.return_value = []
    with pytest.raises(HTTPException) as exc:
        reviewService.getReviewById("999")
    assert exc.value.status_code == 404


# --------------------------------------------------------------------
# update
# --------------------------------------------------------------------
@patch("app.services.reviewService.saveAll")
@patch("app.services.reviewService.loadAll")
def test_update_review(mock_load, mock_save, fake_reviews):
    mock_load.return_value = fake_reviews
    payload = ReviewUpdate(
        movieId=10,
        userId=40846,
        reviewTitle="Updated title",
        rating="10",
        reviewBody="Amazing",
        flagged=True,
    )
    updated = reviewService.updateReview("1", payload)
    assert updated.reviewTitle == "Updated title"
    mock_save.assert_called_once()


@patch("app.services.reviewService.saveAll")
@patch("app.services.reviewService.loadAll")
def test_update_review_not_found(mock_load, mock_save):
    mock_load.return_value = []
    payload = ReviewUpdate(
        movieId=10,
        userId=40000,
        reviewTitle="Hi",
        rating="10",
        reviewBody="Test",
        flagged=False,
    )
    with pytest.raises(HTTPException):
        reviewService.updateReview("nope", payload)


# --------------------------------------------------------------------
# delete
# --------------------------------------------------------------------
@patch("app.services.reviewService.saveAll")
@patch("app.services.reviewService.loadAll")
def test_delete_review_success(mock_load, mock_save, fake_reviews):
    mock_load.return_value = fake_reviews
    reviewService.deleteReview("1")
    mock_save.assert_called_once()


@patch("app.services.reviewService.saveAll")
@patch("app.services.reviewService.loadAll")
def test_delete_review_not_found(mock_load, mock_save, fake_reviews):
    mock_load.return_value = fake_reviews
    with pytest.raises(HTTPException) as exc:
        reviewService.deleteReview("999")
    assert exc.value.status_code == 404
