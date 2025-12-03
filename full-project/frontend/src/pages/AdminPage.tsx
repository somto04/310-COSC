// src/pages/AdminDashboard.tsx
import { useState } from "react";
import ReviewsAdmin from "../components/admin/ReviewsAdmin";
// import UsersAdmin from "../components/admin/UsersAdmin";
// import MoviesAdmin from "../components/admin/MoviesAdmin";

type AdminSection = "reviews" | "users" | "movies";

export default function AdminDashboard() {
  const [section, setSection] = useState<AdminSection>("reviews");

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Admin Dashboard</h1>

      <div style={{ marginBottom: "1rem", display: "flex", gap: "0.5rem" }}>
        <button onClick={() => setSection("reviews")}>Reviews</button>
        <button onClick={() => setSection("users")}>Users</button>
        <button onClick={() => setSection("movies")}>Movies</button>
      </div>

      {section === "reviews" && <ReviewsAdmin />}
      {/* {section === "users" && <UsersAdmin />} */}
      {/* {section === "movies" && <MoviesAdmin />} */}
    </div>
  );
}
