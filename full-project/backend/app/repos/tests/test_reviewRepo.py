import json
import app.repos.reviewRepo as reviewRepo

def test_review_load_uses_tmp(tmp_path, monkeypatch):
    test_file = tmp_path / "reviews.json"

    data = [
        {
            "id": 1,
            "movieId": 101,
            "userId": 7,
            "reviewTitle": "A Tale Worth a Thousand Berries",
            "reviewBody": "By the seas! This film had more heart than a feast at Baratie. Zoro nearly cried—well, almost.",
            "rating": "9.5",
            "datePosted": "2025-01-12",
            "flagged": False
        },
        {
            "id": 2,
            "movieId": 102,
            "userId": 3,
            "reviewTitle": "Not Even the Grand Line Could Save It",
            "reviewBody": "Nami said it was a treasure, but the pacing dragged worse than Usopp’s tall tales. Needed more spirit!",
            "rating": "6.0",
            "datePosted": "2025-03-22",
            "flagged": True
        }
    ]

    test_file.write_text(json.dumps(data))
    # Patch the constant the functions read
    monkeypatch.setattr(reviewRepo, "REVIEW_DATA_FILE", test_file, raising=False)

    reviews = reviewRepo.loadReviews()
    assert len(reviews) == 2
    assert reviews[0]["id"] == 1
    assert reviews[0]["reviewTitle"] == "A Tale Worth a Thousand Berries"
    assert reviews[1]["userId"] == 3
    assert reviews[1]["flagged"] is True

def test_review_save_and_verify_contents(tmp_path, monkeypatch):
    test_file = tmp_path / "reviews.json"
    monkeypatch.setattr(reviewRepo, "REVIEW_DATA_FILE", test_file, raising=False)

    data = [
    {
        "id": 1,
        "movieId": 101,
        "userId": 7,
        "reviewTitle": "A Tale Worth a Thousand Berries",
        "reviewBody": "By the seas! This film had more heart than a feast at Baratie. Zoro nearly cried—well, almost.",
        "rating": "9.5",
        "datePosted": "2025-01-12",
        "flagged": False
    },
    {
        "id": 2,
        "movieId": 102,
        "userId": 3,
        "reviewTitle": "Not Even the Grand Line Could Save It",
        "reviewBody": "Nami said it was a treasure, but the pacing dragged worse than Usopp’s tall tales. Needed more spirit!",
        "rating": "6.0",
        "datePosted": "2025-03-22",
        "flagged": True
    },
    {
        "id": 3,
        "movieId": 103,
        "userId": 10,
        "reviewTitle": "Sanji’s Culinary Masterpiece",
        "reviewBody": "Cooked to perfection! Every scene sizzled like meat on the grill. I’d trade a barrel of cola for another viewing.",
        "rating": "8.8",
        "datePosted": "2025-05-04",
        "flagged": False
    },
    {
        "id": 4,
        "movieId": 104,
        "userId": 2,
        "reviewTitle": "A Devil Fruit Disaster",
        "reviewBody": "Plot twist hit harder than Luffy’s Gatling, but the ending sank faster than a Marine ship in a storm.",
        "rating": "5.7",
        "datePosted": "2025-07-16",
        "flagged": False
    }
]


    reviewRepo.saveReviews(data)

    assert test_file.exists(), "users.json should have been created"
    contents = json.loads(test_file.read_text())
    assert contents == data
    assert len(contents) == 4
    assert contents[2]["reviewTitle"] == "Sanji’s Culinary Masterpiece"
    assert contents[3]["rating"] == "5.7"
    assert contents[3]["reviewBody"].startswith("Plot twist hit harder than Luffy’s Gatling")
    assert contents[1]["flagged"] is True
    assert contents[0]["userId"] == 7
    assert contents[2]["movieId"] == 103
    assert contents[1]["datePosted"] == "2025-03-22"