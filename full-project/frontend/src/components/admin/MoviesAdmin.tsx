import { useEffect, useState } from "react";
import { getToken } from "../../utils/auth";

const API = import.meta.env.VITE_API_URL;

type Movie = {
  id: number;
  tmdbId?: number;
  title: string;
  movieIMDbRating?: number | string;
  movieIMDb?: number | string;
  movieGenres?: string[];
  movieGenre?: string[];
  directors?: string[];
  mainstars?: string[];
  mainStars?: string[];
  description?: string;
  datePublished?: string;
  duration?: number;
  yearReleased?: number;
  year?: number;
};

type EditForm = {
  tmdbId: string;
  title: string;
  movieIMDb: string;
  movieGenre: string;   // comma-separated
  directors: string;    // comma-separated
  mainstars: string;    // comma-separated
  description: string;
  datePublished: string;
  duration: string;
  yearReleased: string;
};

export default function MoviesAdmin() {
  const [movies, setMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [msg, setMsg] = useState<string | null>(null);

  const [editingMovie, setEditingMovie] = useState<Movie | null>(null);
  const [editForm, setEditForm] = useState<EditForm | null>(null);

  const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null);

  const token = getToken();

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      const target = e.target as HTMLElement;
      if (
        confirmDeleteId !== null &&
        !target.closest(".delete-btn")
      ) {
        setConfirmDeleteId(null);
      }
    }
    window.addEventListener("click", handleClickOutside);
    return () => window.removeEventListener("click", handleClickOutside);
  }, [confirmDeleteId]);

  useEffect(() => {
    function handleEsc(e: KeyboardEvent) {
      if (e.key === "Escape") {
        setConfirmDeleteId(null);
      }
    }
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, []);

  function authHeaders(extra?: HeadersInit): Headers {
        const headers = new Headers(extra);

        headers.set("Content-Type", "application/json");

        if (token) {
            headers.set("Authorization", `Bearer ${token}`);
        }

        return headers;
    }

  async function loadMovies() {
    try {
      setLoading(true);
      setError(null);
      setMsg(null);

      const res = await fetch(`${API}/movies`, {
        headers: authHeaders({ "Content-Type": "application/json" }),
      });

      if (!res.ok) {
        throw new Error(`Failed to load movies (${res.status})`);
      }

      const data = await res.json();
      setMovies(data);
    } catch (e: any) {
      setError(e.message || "Something died loading movies.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadMovies();
  }, [token]);

  function startEdit(movie: Movie) {
    setMsg(null);
    setError(null);
    setConfirmDeleteId(null);

    const form: EditForm = {
      tmdbId: String(movie.tmdbId ?? ""),
      title: movie.title ?? "",
      movieIMDb: String(
        movie.movieIMDbRating ??
          movie.movieIMDb ??
          ""
      ),
      movieGenre: (movie.movieGenres ??
        movie.movieGenre ??
        []
      ).join(", "),
      directors: (movie.directors ?? []).join(", "),
      mainstars: (movie.mainstars ?? movie.mainStars ?? []).join(", "),
      description: movie.description ?? "",
      datePublished: movie.datePublished ?? "",
      duration: String(movie.duration ?? ""),
      yearReleased: String(movie.yearReleased ?? movie.year ?? ""),
    };

    setEditingMovie(movie);
    setEditForm(form);
  }

  function updateFormField<K extends keyof EditForm>(key: K, value: string) {
    if (!editForm) return;
    setEditForm({ ...editForm, [key]: value });
  }

  async function saveEdit() {
    if (!editingMovie || !editForm) return;

    setLoading(true);
    setError(null);
    setMsg(null);

    const yr = Number(editForm.yearReleased);

    if (!editForm.yearReleased.trim() || Number.isNaN(yr) || yr < 1888) {
        setError("Year Released is required and must be a number ≥ 1888.");
        setLoading(false);
        return;
    }


    const payload = {
        tmdbId: Number(editForm.tmdbId) || 0,
        title: editForm.title,
        movieIMDb: parseFloat(editForm.movieIMDb) || 0,
        movieGenre: editForm.movieGenre
            .split(",")
            .map((s) => s.trim())
            .filter(Boolean),
        directors: editForm.directors
            .split(",")
            .map((s) => s.trim())
            .filter(Boolean),
        mainstars: editForm.mainstars
            .split(",")
            .map((s) => s.trim())
            .filter(Boolean),
        description: editForm.description,
        datePublished: editForm.datePublished,
        duration: Number(editForm.duration) || 0,
        yearReleased: yr,
    };

    try {
      const res = await fetch(`${API}/movies/${editingMovie.id}`, {
        method: "PUT",
        headers: authHeaders(),
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => null);
        throw new Error(body?.detail || `Update failed (${res.status})`);
      }

      setMsg(`Updated movie #${editingMovie.id}.`);
      setEditingMovie(null);
      setEditForm(null);
      await loadMovies();
    } catch (e: any) {
      setError(e.message || "Failed to update movie.");
    } finally {
      setLoading(false);
    }
  }

  async function deleteMovie(id: number) {
    setLoading(true);
    setError(null);
    setMsg(null);

    try {
      const res = await fetch(`${API}/movies/${id}`, {
        method: "DELETE",
        headers: authHeaders(),
      });

      if (!res.ok && res.status !== 204) {
        const body = await res.json().catch(() => null);
        throw new Error(body?.detail || `Delete failed (${res.status})`);
      }

      setMovies((prev) => prev.filter((m) => m.id !== id));
      setMsg(`Deleted movie #${id}.`);
    } catch (e: any) {
      setError(e.message || "Failed to delete movie.");
    } finally {
      setConfirmDeleteId(null);
      setLoading(false);
    }
  }

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Movies Admin</h1>

      {loading && <p>Working on it, relax...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {msg && <p style={{ color: "green" }}>{msg}</p>}

      {/* EDIT WINDOW */}
      {editingMovie && editForm && (
        <div
          style={{
            border: "1px solid #ccc",
            padding: "1rem",
            marginBottom: "1.5rem",
            borderRadius: "4px",
            background: "#2b2b2b",
          }}
        >
          <h2>Edit: {editingMovie.title}</h2>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: "0.75rem",
            }}
          >
            <label>
              TMDB ID
              <input
                type="number"
                value={editForm.tmdbId}
                onChange={(e) => updateFormField("tmdbId", e.target.value)}
                style={{ width: "100%" }}
              />
            </label>

            <label>
              Title
              <input
                type="text"
                value={editForm.title}
                onChange={(e) => updateFormField("title", e.target.value)}
                style={{ width: "100%" }}
              />
            </label>

            <label>
              IMDb Rating
              <input
                type="text"
                value={editForm.movieIMDb}
                onChange={(e) => updateFormField("movieIMDb", e.target.value)}
                style={{ width: "100%" }}
              />
            </label>

            <label>
              Genres (comma separated)
              <input
                type="text"
                value={editForm.movieGenre}
                onChange={(e) => updateFormField("movieGenre", e.target.value)}
                style={{ width: "100%" }}
              />
            </label>

            <label>
              Directors (comma separated)
              <input
                type="text"
                value={editForm.directors}
                onChange={(e) => updateFormField("directors", e.target.value)}
                style={{ width: "100%" }}
              />
            </label>

            <label>
              Main stars (comma separated)
              <input
                type="text"
                value={editForm.mainstars}
                onChange={(e) => updateFormField("mainstars", e.target.value)}
                style={{ width: "100%" }}
              />
            </label>

            <label>
              Date Published (YYYY-MM-DD)
              <input
                type="text"
                value={editForm.datePublished}
                onChange={(e) =>
                  updateFormField("datePublished", e.target.value)
                }
                style={{ width: "100%" }}
              />
            </label>

            <label>
              Duration (minutes)
              <input
                type="number"
                value={editForm.duration}
                onChange={(e) => updateFormField("duration", e.target.value)}
                style={{ width: "100%" }}
              />
            </label>

            <label>
              Year Released
              <input
                type="number"
                value={editForm.yearReleased}
                onChange={(e) =>
                  updateFormField("yearReleased", e.target.value)
                }
                style={{ width: "100%" }}
              />
            </label>

            <label style={{ gridColumn: "1 / -1" }}>
              Description
              <textarea
                value={editForm.description}
                onChange={(e) =>
                  updateFormField("description", e.target.value)
                }
                style={{ width: "100%", minHeight: "80px" }}
              />
            </label>
          </div>

          <div style={{ marginTop: "1rem", display: "flex", gap: "0.5rem" }}>
            <button onClick={saveEdit}>Save</button>
            <button
              onClick={() => {
                setEditingMovie(null);
                setEditForm(null);
              }}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* MOVIE LIST */}
      <table
        style={{
          width: "100%",
          borderCollapse: "collapse",
          marginTop: "1rem",
        }}
      >
        <thead>
          <tr>
            <th style={{ borderBottom: "1px solid #ccc", textAlign: "left" }}>
              ID
            </th>
            <th style={{ borderBottom: "1px solid #ccc", textAlign: "left" }}>
              Title
            </th>
            <th style={{ borderBottom: "1px solid #ccc", textAlign: "left" }}>
              Year
            </th>
            <th style={{ borderBottom: "1px solid #ccc" }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {movies.map((m) => (
            <tr key={m.id}>
              <td style={{ padding: "0.5rem 0.25rem" }}>{m.id}</td>
              <td style={{ padding: "0.5rem 0.25rem" }}>{m.title}</td>
              <td style={{ padding: "0.5rem 0.25rem" }}>
                {m.yearReleased ?? m.year ?? ""}
              </td>
              <td style={{ padding: "0.5rem 0.25rem" }}>
                <button
                  onClick={() => startEdit(m)}
                  style={{ marginRight: "0.5rem" }}
                >
                  Update
                </button>

                <button
                  className="delete-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    confirmDeleteId === m.id
                      ? deleteMovie(m.id)
                      : setConfirmDeleteId(m.id);
                  }}
                  style={{
                    background:
                      confirmDeleteId === m.id ? "tomato" : undefined,
                    color: confirmDeleteId === m.id ? "white" : undefined,
                  }}
                >
                  {confirmDeleteId === m.id ? "Are you sure?" : "Delete"}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {movies.length === 0 && !loading && <p>No movies found.</p>}
    </div>
  );
}
