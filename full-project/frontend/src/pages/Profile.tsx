import { useState, useEffect } from "react";
const API = import.meta.env.VITE_API_URL;

export default function Profile() {

  type FavoriteMovie = {
    id: number;
    title: string;
    poster?: string | null;
  };

  type LikedReviewFull = {
    id: number;
    movieId: number;
    movieTitle: string;
    username: string;
    reviewTitle: string;
    poster?: string | null;
  };
  type WatchlistMovie = {
  id: number;
  title: string;
  duration: number;
  poster?: string | null;
};


  const [favorites, setFavorites] = useState<FavoriteMovie[]>([]);
  const [reviews, setReviews] = useState<LikedReviewFull[]>([]);

  const [user, setUser] = useState<{
    username: string;
    email: string;
    firstName: string;
    lastName: string;
    age: number;
    pw: string;
  } | null>(null);

  const [showForm, setShowForm] = useState(false);
  const [editUsername, setEditUsername] = useState("");
  const [editFirstName, setEditFirstName] = useState("");
  const [editLastName, setEditLastName] = useState("");
  const [editEmail, setEditEmail] = useState("");
  const [watchlist, setWatchlist] = useState<WatchlistMovie[]>([]);

  const userId = localStorage.getItem("userId");
  const token = localStorage.getItem("token");

  // LOAD LOGGED-IN USER INFO
useEffect(() => {
  if (!userId || !token) return;

  fetch(`${API}/users/userProfile?userId=${userId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
    .then(res => res.json())
    .then(data => {
      setUser({
        username: data.user.username,
        firstName: data.user.firstName,
        lastName: data.user.lastName,
        email: data.user.email,
        age: data.user.age,
        pw: data.user.pw,
      });

      setEditUsername(data.user.username);
      setEditFirstName(data.user.firstName);
      setEditLastName(data.user.lastName);
      setEditEmail(data.user.email);
    })
    .catch(err => console.error("Error loading user:", err));
}, [token, userId]); 

  // LOAD WATCHLIST
useEffect(() => {
  const token = localStorage.getItem("token");
  if (!token) return;

 fetch(`${API}/users/watchlist`,
 {
    headers: { Authorization: `Bearer ${token}` },
  })
    .then((res) => res.json())
    .then(async (data) => {
      const movies = data.watchlist || [];

      // fetch posters
      const enriched = await Promise.all(
        movies.map(async (movie: any) => {
          const tmdbRes = await fetch(
            `${API}/tmdb/details/${movie.id}`
          );
          const tmdb = await tmdbRes.json();

          return {
            id: movie.id,
            title: movie.title,
            duration: movie.duration || 0,
            poster: tmdb.poster || null,
          };
        })
      );

      setWatchlist(enriched);
    })
    .catch((err) => console.error("Watchlist error:", err));
}, []);


  // LOAD FAVORITE MOVIES W/ POSTERS
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) return;

    fetch(`${API}/favorites/`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then(async (movies) => {
        const moviesWithPosters = await Promise.all(
          movies.map(async (movie: any) => {
            const tmdbRes = await fetch(
              `${API}/tmdb/details/${movie.id}`
            );
            const tmdbData = await tmdbRes.json();

            return {
              id: movie.id,
              title: movie.title,
              poster: tmdbData.poster || null,
            };
          })
        );

        setFavorites(moviesWithPosters);
      })
      .catch((err) => console.error("Error loading favorites:", err));
  }, []);


  // LOAD LIKED REVIEWS
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) return;

fetch(`${API}/likeReview/`,{
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then((data) => {
        setReviews(data);
      })
      .catch((err) => console.error("Error loading liked reviews:", err));
  }, []);



  return (
    <div style={{ padding: "2rem", maxWidth: "700px", margin: "0 auto" }}>
      <h1 style={{ marginBottom: "1rem" }}>Profile</h1>

      {/* LOGOUT BUTTON */}
      <button
        onClick={() => {
          const token = localStorage.getItem("token");
          fetch(`${API}/default/logout`, {

            method: "POST",
            headers: { Authorization: `Bearer ${token}` },
          }).catch(() => {});

          localStorage.removeItem("token");
          localStorage.removeItem("userId");
          window.location.href = "/login";
        }}
        style={{
          padding: "0.5rem 1rem",
          border: "1px solid black",
          background: "red",
          cursor: "pointer",
          marginTop: "1rem",
        }}
      >
        Logout
      </button>

      {/* FORGOT PASSWORD BUTTON */}
      <button
  onClick={() => {
    window.location.href = "/reset-password";
  }}
  style={{
    padding: "0.5rem 1rem",
    border: "1px solid black",
    background: "black",
    color: "white",
    cursor: "pointer",
    marginTop: "1rem",
    marginLeft: "1rem",
  }}
>
  Forgot Password?
</button>


      {/* USER INFO */}
      {user ? (
        <section style={{ marginBottom: "2rem" }}>
          <h2>User Info</h2>
          <p><strong>Username:</strong> {user.username}</p>
          <p><strong>Name:</strong> {user.firstName} {user.lastName}</p>
          <p><strong>Email:</strong> {user.email}</p>
        </section>
      ) : (
        <p>Loading user...</p>
      )}

      {/* UPDATE ACCOUNT BUTTON */}
      <button
        onClick={() => setShowForm(!showForm)}
        style={{
          padding: "0.5rem 1rem",
          border: "1px solid black",
          background: "black",
          color: "white",
          cursor: "pointer",
          marginTop: "1rem",
        }}
      >
        Update Account
      </button>

      {/* UPDATE FORM */}
      {showForm && user && (
        <form
          style={{
            marginTop: "1rem",
            display: "flex",
            flexDirection: "column",
            gap: "0.5rem",
          }}
          onSubmit={(e) => {
            e.preventDefault();

            const token = localStorage.getItem("token");
            const userId = localStorage.getItem("userId");

            fetch(`${API}/users/${userId}`, {
              method: "PUT",
              headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
              },
              body: JSON.stringify({
                username: editUsername,
                firstName: editFirstName,
                lastName: editLastName,
                email: editEmail,
                age: user.age,
                pw: user.pw,
              }),
            })
              .then((res) => res.json())
              .then(() => {
  // After update, reload user profile
  const token = localStorage.getItem("token");
  const userId = localStorage.getItem("userId");

  fetch(`${API}/users/userProfile/${userId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
    .then((res) => res.json())
    .then((data) => {
      setUser({
        username: data.user.username,
        firstName: data.user.firstName,
        lastName: data.user.lastName,
        email: data.user.email,
        age: data.user.age,
        pw: data.user.pw,
      });

      setEditUsername(data.user.username);
      setEditFirstName(data.user.firstName);
      setEditLastName(data.user.lastName);
      setEditEmail(data.user.email);

      setShowForm(false);
    });
})

              .catch((err) => console.error("Update failed:", err));
          }}
        >
          <label>
            First Name:
            <input
              type="text"
              value={editFirstName}
              onChange={(e) => setEditFirstName(e.target.value)}
              style={{ padding: "0.3rem", border: "1px solid black" }}
            />
          </label>

          <label>
            Last Name:
            <input
              type="text"
              value={editLastName}
              onChange={(e) => setEditLastName(e.target.value)}
              style={{ padding: "0.3rem", border: "1px solid black" }}
            />
          </label>

          <label>
            Username:
            <input
              type="text"
              value={editUsername}
              onChange={(e) => setEditUsername(e.target.value)}
              style={{ padding: "0.3rem", border: "1px solid black" }}
            />
          </label>

          <label>
            Email:
            <input
              type="email"
              value={editEmail}
              onChange={(e) => setEditEmail(e.target.value)}
              style={{ padding: "0.3rem", border: "1px solid black" }}
            />
          </label>

          <button
            type="submit"
            style={{
              padding: "0.5rem 1rem",
              border: "1px solid black",
              background: "black",
              color: "white",
              cursor: "pointer",
              marginTop: "0.5rem",
            }}
          >
            Save Changes
          </button>
        </form>
      )}

      {/* LIKED REVIEWS */}
      <section style={{ marginTop: "2rem" }}>
        <h2
  style={{ cursor: "pointer", textDecoration: "underline" }}
  onClick={() => (window.location.href = "/liked-reviews")}
>
  Liked Reviews
</h2>

        {reviews.length === 0 ? (
          <p>You haven't liked any reviews yet.</p>
        ) : (
          <ul style={{ paddingLeft: "1rem" }}>
            {reviews.slice(0, 3).map((r) => (
              <li
                key={r.id}
                style={{
                  marginBottom: "1.5rem",
                  display: "flex",
                  gap: "1rem",
                  alignItems: "flex-start",
                }}
              >
                {r.poster && (
                  <img
                    src={r.poster}
                    alt={r.movieTitle}
                    style={{
                      width: "60px",
                      height: "90px",
                      objectFit: "cover",
                      border: "1px solid black",
                    }}
                  />
                )}

                <div style={{ flex: 1 }}>
                  <p style={{ fontWeight: "bold" }}>{r.movieTitle}</p>

                  <p style={{ fontStyle: "italic", margin: "0.2rem 0" }}>
                    "{r.reviewTitle}"
                  </p>

                  <p style={{ margin: "0.2rem 0" }}>
                    <strong>User: {r.username}</strong>
                  </p>
                </div>

                <button
                  onClick={() => {
                    const token = localStorage.getItem("token");

                    fetch(`${API}/likeReview/${r.id}`, {
                      method: "DELETE",
                      headers: {
                        Authorization: `Bearer ${token}`,
                      },
                    })
                      .then(() => {
                        setReviews(reviews.filter((rev) => rev.id !== r.id));
                      })
                      .catch((err) =>
                        console.error("Error unliking review:", err)
                      );
                  }}
                  style={{
                    padding: "0.3rem 0.8rem",
                    border: "1px solid black",
                    background: "black",
                    color: "white",
                    cursor: "pointer",
                  }}
                >
                  Remove
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      {/* WATCHLIST */}

     <section style={{ marginTop: "2rem" }}>
  <h2
    style={{ cursor: "pointer", textDecoration: "underline" }}
    onClick={() => (window.location.href = "/watchlist")}
  >
    Watchlist
  </h2>

  {watchlist.length === 0 ? (
    <p>No movies in watchlist yet.</p>
  ) : (
    <ul style={{ paddingLeft: "1rem" }}>
      {watchlist.slice(0, 3).map((movie) => (
        <li
          key={movie.id}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "1rem",
            marginBottom: "1rem",
          }}
        >
          {movie.poster && (
            <img
              src={movie.poster}
              alt={movie.title}
              style={{
                width: "60px",
                height: "90px",
                objectFit: "cover",
                border: "1px solid black",
              }}
            />
          )}

          <div style={{ flex: 1 }}>
            <p style={{ margin: 0, fontWeight: "bold" }}>{movie.title}</p>
            <p style={{ margin: 0, color: "#555" }}>
              {movie.duration} minutes
            </p>
          </div>

          <button
            onClick={() => {
              const token = localStorage.getItem("token");
              fetch(`${API}/users/watchlist/${movie.id}`, {
                method: "DELETE",
                headers: { Authorization: `Bearer ${token}` },
              })
                .then(() => {
                  setWatchlist(
                    watchlist.filter((m) => m.id !== movie.id)
                  );
                })
                .catch((err) =>
                  console.error("Error removing from watchlist:", err)
                );
            }}
            style={{
              padding: "0.3rem 0.8rem",
              border: "1px solid black",
              background: "black",
              color: "white",
              cursor: "pointer",
            }}
          >
            Remove
          </button>
        </li>
      ))}
    </ul>
  )}
</section>



      {/* FAVORITE MOVIES */}
      <section style={{ marginTop: "2rem" }}>
        <h2
  style={{ cursor: "pointer", textDecoration: "underline" }}
  onClick={() => (window.location.href = "/favorite-movies")}
>
  Favorite Movies
</h2>


        {favorites.length === 0 ? (
          <p>No favorites yet.</p>
        ) : (
          <ul style={{ paddingLeft: "1rem" }}>
           {favorites.slice(0, 3).map((f) => (
              <li
                key={f.id}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "1rem",
                  marginBottom: "1rem",
                }}
              >
                {f.poster && (
                  <img
                    src={f.poster}
                    alt={f.title}
                    style={{
                      width: "60px",
                      height: "90px",
                      objectFit: "cover",
                      border: "1px solid black",
                    }}
                  />
                )}

                <span>{f.title}</span>

                <button
                  onClick={() => {
                    const token = localStorage.getItem("token");

                    fetch(`${API}/favorites/${f.id}`, {
                      method: "DELETE",
                      headers: { Authorization: `Bearer ${token}` },
                    })
                      .then(() => {
                        setFavorites(favorites.filter((mov) => mov.id !== f.id));
                      })
                      .catch((err) =>
                        console.error("Error removing favorite:", err)
                      );
                  }}
                  style={{
                    marginLeft: "auto",
                    padding: "0.3rem 0.8rem",
                    border: "1px solid black",
                    background: "black",
                    color: "white",
                    cursor: "pointer",
                  }}
                >
                  Remove
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}