import { useState, useEffect } from "react";

export default function Profile() {

  type FavoriteMovie = {
  id: number;
  title: string;
  poster?: string | null; // optional
  };

  type LikedReviewFull = {
  id: number;
  movieId: number;
  movieTitle: string;
  username: string;
  reviewTitle: string;
  reviewBody: string;
  rating?: number;
  datePosted?: string;
  flagged?: boolean;
  poster?: string | null;
};



  const [favorites, setFavorites] = useState<FavoriteMovie[]>([]);
  const [user, setUser] = useState<{ username: string; email: string } | null>(null);

const [reviews, setReviews] = useState<LikedReviewFull[]>([]);




  const [showForm, setShowForm] = useState(false);
  const [editUsername, setEditUsername] = useState("");
  const [editEmail, setEditEmail] = useState("");


  //load logged in user info
  useEffect(() => {
    const userId = localStorage.getItem("userId");
    const token = localStorage.getItem("token");
    if (!userId || !token) return;

    fetch(`http://localhost:8000/users/userProfile/${userId}`, {
      headers: {
        "Authorization": `Bearer ${token}`,  
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

  
//load logged in user's favorites posters from TMDB
useEffect(() => {
  const token = localStorage.getItem("token");
  if (!token) return;

  fetch("http://localhost:8000/favorites/", {
    headers: {
      "Authorization": `Bearer ${token}`,
    },
  })
    .then((res) => res.json())
    .then(async (movies) => {
      const moviesWithPosters = await Promise.all(
        movies.map(async (movie: any) => {
          const tmdbRes = await fetch(`http://localhost:8000/tmdb/details/${movie.id}`);
          const tmdbData = await tmdbRes.json();
          console.log("TMDB DATA for:", movie.title, tmdbData);

          const posterPath = tmdbData.poster || null;

          return {
            id: movie.id,
            title: movie.title,
            poster: posterPath,
          };
        })
      );

      setFavorites(moviesWithPosters);
    })
    .catch((err) => console.error("Error loading favorites:", err));
}, []);


// Load liked reviews from database
useEffect(() => {
  const token = localStorage.getItem("token");
  if (!token) return;

  fetch("http://localhost:8000/likeReview/", {
    headers: {
      "Authorization": `Bearer ${token}`,
    },
  })
    .then((res) => res.json())
    .then((data) => {
      console.log("LIKED REVIEWS:", data);
      setReviews(data);
    })
    .catch((err) => console.error("Error loading liked reviews:", err));
}, []);




  return (
    <div style={{ padding: "2rem", maxWidth: "700px", margin: "0 auto" }}>
      <h1 style={{ marginBottom: "1rem" }}>Profile</h1>
<button
  onClick={() => {
    const token = localStorage.getItem("token");

    // hit backend logout (optional but nice)
    fetch("http://localhost:8000/default/logout", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
      },
    }).catch(() => {});

    // clear stored login info
    localStorage.removeItem("token");
    localStorage.removeItem("userId");

    // redirect to login
    window.location.href = "/temp-login";
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
    <li 
      key={r.id} 
      style={{ 
        marginBottom: "1.5rem",
        display: "flex",
        gap: "1rem",
        alignItems: "flex-start"
      }}
    >
      {/* Poster */}
      {r.poster && (
        <img 
          src={r.poster} 
          alt={r.movieTitle}
          style={{
            width: "60px",
            height: "90px",
            objectFit: "cover",
            border: "1px solid black"
          }}
        />
      )}

      <div style={{ flex: 1 }}>
        {/* Movie Title */}
        <p style={{ fontWeight: "bold", fontSize: "1rem" }}>
          {r.movieTitle}
        </p>

        {/* Review Title */}
        <p style={{ fontStyle: "italic", margin: "0.2rem 0" }}>
          "{r.reviewTitle}"
        </p>

        {/* Reviewer Username */}
        <p style={{ margin: "0.2rem 0" }}>
          <strong>User: {r.username}</strong>
        </p>

        {/* Review Body */}
        <p style={{ margin: "0.2rem 0" }}>
          {r.reviewBody}
        </p>

        {/* Remove Button */}
        <button
          onClick={() => {
            const token = localStorage.getItem("token");

            fetch(`http://localhost:8000/likeReview/${r.id}`, {
              method: "DELETE",
              headers: {
                "Authorization": `Bearer ${token}`,
              },
            })
              .then(() => {
                setReviews(reviews.filter((rev) => rev.id !== r.id));
              })
              .catch((err) => console.error("Error unliking review:", err));
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
      </div>
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
  <li 
    key={f.id} 
    style={{ 
      display: "flex", 
      alignItems: "center", 
      gap: "1rem", 
      marginBottom: "1rem" 
    }}
  >
    {/* Poster */}
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

    {/* Title */}
    <span>{f.title}</span>

    {/* Remove Button */}
    <button
      onClick={() => {
        const token = localStorage.getItem("token");

        fetch(`http://localhost:8000/favorites/${f.id}`, {
          method: "DELETE",
          headers: {
            "Authorization": `Bearer ${token}`,
          },
        })
          .then(() => {
            setFavorites(favorites.filter((mov) => mov.id !== f.id));
          })
          .catch((err) => console.error("Error removing favorite:", err));
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
