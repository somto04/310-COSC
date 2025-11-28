import { useState, useEffect } from "react";

export default function Profile() {

  const [user, setUser] = useState<{ username: string; email: string } | null>(null);

  const [reviews, setReviews] = useState([
    { id: 1, movie: "Inception", username: "nolanloverboy68", content: "Loved it, Nolan is goated as always." },
    { id: 2, movie: "Avengers Endgame", username: "marvelh8r4eva", content: "Marvel movies can suck my a***." },
  ]);

  const [favorites, setFavorites] = useState([
    { id: 10, title: "Interstellar" },
    { id: 11, title: "The Dark Knight" },
  ]);

  const [showForm, setShowForm] = useState(false);
  const [editUsername, setEditUsername] = useState("");
  const [editEmail, setEditEmail] = useState("");

  // --------------------------
  // LOAD REAL USER FROM BACKEND
  // --------------------------
  useEffect(() => {
    const userId = localStorage.getItem("userId");
    const token = localStorage.getItem("token");
    if (!userId || !token) return;

    fetch(`http://localhost:8000/users/userProfile/${userId}`, {
      headers: {
        "Authorization": `Bearer ${token}`,   // <-- THIS WAS MISSING
      },
    })
      .then((res) => res.json())
      .then((data) => {
        console.log("LOADED USER:", data);
        setUser({
          username: data.user.username,
          email: data.user.email,
        });
        setEditUsername(data.user.username);
        setEditEmail(data.user.email);
      })
      .catch((err) => console.error("Error loading user:", err));
  }, []);

  return (
    <div style={{ padding: "2rem", maxWidth: "700px", margin: "0 auto" }}>
      <h1 style={{ marginBottom: "1rem" }}>Profile</h1>

      {/* USER INFO */}
      {user ? (
        <section style={{ marginBottom: "2rem" }}>
          <h2>User Info</h2>
          <p><strong>Username:</strong> {user.username}</p>
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
      {showForm && (
        <form
          style={{
            marginTop: "1rem",
            display: "flex",
            flexDirection: "column",
            gap: "0.5rem",
          }}
          onSubmit={(e) => {
            e.preventDefault();
            setUser({ username: editUsername, email: editEmail });
            setShowForm(false);
          }}
        >
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
        <h2>Liked Reviews</h2>

        {reviews.length === 0 ? (
          <p>You haven't liked any reviews yet.</p>
        ) : (
          <ul style={{ paddingLeft: "1rem" }}>
            {reviews.map((r) => (
              <li key={r.id} style={{ marginBottom: "1rem" }}>
                <strong>{r.movie}</strong>
                <p>{r.username} : {r.content}</p>

                <button
                  onClick={() => {
                    setReviews(reviews.filter((rev) => rev.id !== r.id));
                  }}
                  style={{
                    padding: "0.3rem 0.8rem",
                    border: "1px solid black",
                    background: "black",
                    color: "white",
                    cursor: "pointer",
                    marginTop: "0.3rem",
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
        <h2>Favorite Movies</h2>

        {favorites.length === 0 ? (
          <p>No favorites yet.</p>
        ) : (
          <ul style={{ paddingLeft: "1rem" }}>
            {favorites.map((f) => (
              <li key={f.id} style={{ marginBottom: "0.5rem" }}>
                {f.title}

                <button
                  onClick={() =>
                    setFavorites(favorites.filter((mov) => mov.id !== f.id))
                  }
                  style={{
                    marginLeft: "1rem",
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
