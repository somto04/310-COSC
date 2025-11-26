import json
import pytest

import app.repos.reviewRepo as reviewRepo
from app.schemas.review import Review


@pytest.fixture
def reviewDataPath(tmp_path, monkeypatch):
    tempFile = tmp_path / "reviews.json"
    monkeypatch.setattr(reviewRepo, "REVIEW_DATA_PATH", tempFile)
    return tempFile


@pytest.fixture
def sampleReviews():
    return [
        Review(
            id=1,
            movieId=101,
            userId=7,
            reviewTitle="First review title",
            reviewBody="This is the first review body, and it is long enough.",
            rating=8,
            datePosted="2025-01-12",
            flagged=False,
        ),
        Review(
            id=2,
            movieId=202,
            userId=3,
            reviewTitle="Second review title",
            reviewBody="This is the second review body, also long enough.",
            rating=6,
            datePosted="2025-03-22",
            flagged=True,
        ),
    ]

    testFile.write_text(
    json.dumps([review.model_dump() for review in data], ensure_ascii=False),encoding="utf-8")   
    
    monkeypatch.setattr(reviewRepo, "REVIEW_DATA_PATH", testFile)
    monkeypatch.setattr(reviewRepo, "_REVIEW_CACHE", None)
    monkeypatch.setattr(reviewRepo, "_NEXT_REVIEW_ID", None)



def testReviewLoadReadsJsonAndReturnsModels(reviewDataPath, sampleReviews):
    initialJson = [review.model_dump(mode="json") for review in sampleReviews]
    reviewDataPath.write_text(json.dumps(initialJson, ensure_ascii=False), encoding="utf-8")

    loadedReviews = reviewRepo.loadReviews()

    assert len(loadedReviews) == 2
    assert loadedReviews[0].id == 1
    assert loadedReviews[0].movieId == 101
    assert loadedReviews[1].flagged is True

def test_reviewSaveAndVerifyContents(tmp_path, monkeypatch):
    testFile = tmp_path / "reviews.json"
    monkeypatch.setattr(reviewRepo, "REVIEW_DATA_PATH", testFile)
    monkeypatch.setattr(reviewRepo, "_REVIEW_CACHE", None)
    monkeypatch.setattr(reviewRepo, "_NEXT_REVIEW_ID", None)


def testReviewSaveWritesJsonCorrectly(reviewDataPath, sampleReviews):
    reviewRepo.saveReviews(sampleReviews)

    savedJson = json.loads(reviewDataPath.read_text(encoding="utf-8"))
    expectedJson = [review.model_dump(mode="json") for review in sampleReviews]

    assert savedJson == expectedJson
