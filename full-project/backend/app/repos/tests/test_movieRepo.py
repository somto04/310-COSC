import json
import app.repos.movieRepo as movieRepo

def test_movieLoadUsesTmp(tmp_path, monkeypatch):
    testFile = tmp_path / "movies.json"

    data = [
        {
            "id": 1,
            "title": "Spirited Away",
            "movieIMDbRating": 8.6,
            "movieGenres": ["Animation", "Fantasy", "Adventure"],
            "directors": ["Hayao Miyazaki"],
            "mainStars": ["Rumi Hiiragi", "Miyu Irino", "Mari Natsuki"],
            "description": "A young girl enters a world of spirits and must save her parents.",
            "datePublished": "2001-07-20",
            "duration": 125,
            "yearReleased": 2001
        },
        {
            "id": 2,
            "title": "Your Name",
            "movieIMDbRating": 8.4,
            "movieGenres": ["Animation", "Drama", "Fantasy"],
            "directors": ["Makoto Shinkai"],
            "mainStars": ["Ryunosuke Kamiki", "Mone Kamishiraishi"],
            "description": "Two teenagers mysteriously swap bodies and connect across time.",
            "datePublished": "2016-08-26",
            "duration": 112,
            "yearReleased": 2016
        }
    ]

    testFile.write_text(json.dumps(data))

    # Patch the constant the functions read
    monkeypatch.setattr(movieRepo, "MOVIE_DATA_FILE", testFile, raising=False)

    items = movieRepo.loadMovies()
    assert len(items) == 2
    assert items[0]["id"] == 1
    assert items[0]["title"] == "Spirited Away"
    assert items[1]["movieIMDbRating"] == 8.4
    assert items[1]["id"] == 2
    assert items[1]["title"] == "Your Name"
    assert items[1]["directors"] == ["Makoto Shinkai"]


def test_movieSaveAndVerifyContents(tmp_path, monkeypatch):
    testFile = tmp_path / "movies.json"
    monkeypatch.setattr(movieRepo, "MOVIE_DATA_FILE", testFile, raising=False)

    data = [
        {
            "id": 1,
            "title": "Kizumonogatari I: Tekketsu-hen",
            "movieIMDbRating": 7.8,
            "movieGenres": ["Animation", "Action", "Supernatural"],
            "directors": ["Tatsuya Oishi"],
            "mainStars": ["Hiroshi Kamiya", "Maaya Sakamoto", "Yui Horie"],
            "description": "A high schooler encounters a powerful vampire and becomes her unwilling servant.",
            "datePublished": "2016-01-08",
            "duration": 64,
            "yearReleased": 2016
        },
        {
            "id": 2,
            "title": "Kizumonogatari III: Reiketsu-hen",
            "movieIMDbRating": 8.2,
            "movieGenres": ["Animation", "Drama", "Supernatural"],
            "directors": ["Tatsuya Oishi"],
            "mainStars": ["Hiroshi Kamiya", "Maaya Sakamoto", "Yui Horie"],
            "description": "The conclusion to Koyomi's bloody tale of redemption and loss.",
            "datePublished": "2017-01-06",
            "duration": 83,
            "yearReleased": 2017
        }
    ]

    movieRepo.saveMovies(data)

    assert testFile.exists(), "movies.json should have been created"
    contents = json.loads(testFile.read_text())

    assert contents == data
    assert len(contents) == 2
    assert contents[0]["title"].startswith("Kizumonogatari")
    assert all("description" in m for m in contents)