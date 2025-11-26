import json
import app.repos.reviewRepo as reviewRepo
from ...schemas.review import Review

def test_reviewLoadUsesTmp(tmp_path, monkeypatch):
    testFile = tmp_path / "reviews.json"

    data = [
        Review(
            id= 1,
            movieId= 101,
            userId= 7,
            reviewTitle= "A Tale Worth a Thousand Berries",
            reviewBody= "By the seas! This film had more heart than a feast at Baratie. Zoro nearly cried, well, almost.",
            rating= 9,
            datePosted= "2025-01-12",
            flagged= False
        ),
        Review(
            id= 2,
            movieId= 102,
            userId= 3,
            reviewTitle= "Not Even the Grand Line Could Save It",
            reviewBody= "Nami said it was a treasure, but the pacing dragged worse than Usopp’s tall tales. Needed more spirit!",
            rating= 6,
            datePosted= "2025-03-22",
            flagged= True
        )
    ]

    testFile.write_text(
    json.dumps([review.model_dump() for review in data], ensure_ascii=False),encoding="utf-8")   
    monkeypatch.setattr("app.repos.reviewRepo.REVIEW_DATA_PATH", testFile)


    reviews = reviewRepo.loadReviews()
    assert len(reviews) == 2
    assert reviews[0].id == 1
    assert reviews[0].reviewTitle == "A Tale Worth a Thousand Berries"
    assert reviews[1].userId == 3
    assert reviews[1].flagged is True

def test_reviewSaveAndVerifyContents(tmp_path, monkeypatch):
    testFile = tmp_path / "reviews.json"
    monkeypatch.setattr("app.repos.reviewRepo.REVIEW_DATA_PATH", testFile)

    data = [
    Review(
        id= 1,
        movieId= 101,
        userId= 7,
        reviewTitle= "A Tale Worth a Thousand Berries",
        reviewBody= "By the seas! This film had more heart than a feast at Baratie. Zoro nearly cried—well, almost.",
        rating= 9,
        datePosted= "2025-01-12",
        flagged= False
    ),
    Review(
        id= 2,
        movieId= 102,
        userId= 3,
        reviewTitle= "Not Even the Grand Line Could Save It",
        reviewBody= "Nami said it was a treasure, but the pacing dragged worse than Usopp’s tall tales. Needed more spirit!",
        rating= 6,
        datePosted= "2025-03-22",
        flagged= True
    ),
    Review(
        id= 3,
        movieId= 103,
        userId= 10,
        reviewTitle= "Sanji’s Culinary Masterpiece",
        reviewBody= "Cooked to perfection! Every scene sizzled like meat on the grill. I’d trade a barrel of cola for another viewing.",
        rating= 8,
        datePosted= "2025-05-04",
        flagged= False
    ),
    Review(
        id= 4,
        movieId= 104,
        userId= 2,
        reviewTitle= "A Devil Fruit Disaster",
        reviewBody= "Plot twist hit harder than Luffy’s Gatling, but the ending sank faster than a Marine ship in a storm.",
        rating= 5,
        datePosted= "2025-07-16",
        flagged= False
    )
]

    reviewRepo.saveReviews(data)

    assert testFile.exists(), "users.json should have been created"
    contents = json.loads(testFile.read_text(encoding="utf-8"))
    expected = [review.model_dump() for review in data]
    assert contents == expected
    assert len(contents) == 4
    assert contents[2]["reviewTitle"] == "Sanji’s Culinary Masterpiece"
    assert contents[3]["rating"] == 5
    assert contents[3]["reviewBody"].startswith("Plot twist hit harder than Luffy’s Gatling")
    assert contents[1]["flagged"] is True
    assert contents[0]["userId"] == 7
    assert contents[2]["movieId"] == 103
    assert contents[1]["datePosted"] == "2025-03-22"