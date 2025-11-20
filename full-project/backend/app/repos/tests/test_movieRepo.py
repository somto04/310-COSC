import json
import app.repos.movieRepo as movieRepo
from ..movieRepo import Movie

def test_movie_load_uses_tmp(tmp_path, monkeypatch):
    test_file = tmp_path / "movies.json"

    data = [
        Movie(
            id= 1,
            title= "Spirited Away",
            movieIMDbRating= 8.6,
            movieGenres= ["Animation", "Fantasy", "Adventure"],
            directors= ["Hayao Miyazaki"],
            mainStars= ["Rumi Hiiragi", "Miyu Irino", "Mari Natsuki"],
            description= "A young girl enters a world of spirits and must save her parents.",
            datePublished= "2001-07-20",
            duration= 125,
            yearReleased= 2001
        ),
        Movie(
            id= 2,
            title= "Your Name",
            movieIMDbRating= 8.4,
            movieGenres= ["Animation", "Drama", "Fantasy"],
            directors= ["Makoto Shinkai"],
            mainStars= ["Ryunosuke Kamiki", "Mone Kamishiraishi"],
            description= "Two teenagers mysteriously swap bodies and connect across time.",
            datePublished= "2016-08-26",
            duration= 112,
            yearReleased= 2016
        )
    ]

    test_file.write_text(json.dumps(data))

    # Patch the constant the functions read
    monkeypatch.setattr(movieRepo, "MOVIE_DATA_FILE", test_file, raising=False)

    movies = movieRepo.loadAll()
    assert len(movies) == 2
    assert movies[0]["id"] == 1
    assert movies[0]["title"] == "Spirited Away"
    assert movies[1]["movieIMDbRating"] == 8.4
    assert movies[1]["id"] == 2
    assert movies[1]["title"] == "Your Name"
    assert movies[1]["directors"] == ["Makoto Shinkai"]


def test_movie_save_and_verify_contents(tmp_path, monkeypatch):
    test_file = tmp_path / "movies.json"
    monkeypatch.setattr(movieRepo, "MOVIE_DATA_FILE", test_file, raising=False)

    data = [
        Movie(
            id= 1,
            title= "Kizumonogatari I= Tekketsu-hen",
            movieIMDbRating= 7.8,
            movieGenres= ["Animation", "Action", "Supernatural"],
            directors= ["Tatsuya Oishi"],
            mainStars= ["Hiroshi Kamiya", "Maaya Sakamoto", "Yui Horie"],
            description= "A high schooler encounters a powerful vampire and becomes her unwilling servant.",
            datePublished= "2016-01-08",
            duration= 64,
            yearReleased= 2016
        ),
        Movie(
            id= 2,
            title= "Kizumonogatari III= Reiketsu-hen",
            movieIMDbRating= 8.2,
            movieGenres= ["Animation", "Drama", "Supernatural"],
            directors= ["Tatsuya Oishi"],
            mainStars= ["Hiroshi Kamiya", "Maaya Sakamoto", "Yui Horie"],
            description= "The conclusion to Koyomi's bloody tale of redemption and loss.",
            datePublished= "2017-01-06",
            duration= 83,
            yearReleased= 2017
        )
    ]

    movieRepo.saveAll(data)

    assert test_file.exists(), "movies.json should have been created"
    contents = json.loads(test_file.read_text(encoding="utf-8"))

    assert contents == data
    assert len(contents) == 2
    assert contents[0]["title"].startswith("Kizumonogatari")
    assert all("description" in movie for movie in contents)