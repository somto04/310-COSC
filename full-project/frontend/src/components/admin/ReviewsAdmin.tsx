import { useEffect, useState } from "react";
import { authGet, authPost } from "../../api/adminApi";

type FlaggedReview = {
  id: number;
  movieId: number;
  userId: number;
  reviewTitle: string;
  reviewBody: string;
};

type FlaggedPage = {
  page: number;
  pageSize: number;
  pageCount: number;
  totalFlagged: number;
  reviews: FlaggedReview[];
};

export default function ReviewsAdmin() {
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [data, setData] = useState<FlaggedPage | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [msg, setMsg] = useState<string | null>(null);

  const [movieTitles, setMovieTitles] = useState<Record<number, string>>({});
  const [usernames, setUsernames] = useState<Record<number, string>>({});

  async function loadPage(p: number) {
    try {
      setLoading(true);
      setError(null);
      setMsg(null);

      const query = `?page=${p}&pageSize=${pageSize}`;
      const result = await authGet(`/admin/reports/reviews${query}`);

      setData(result);
      setPage(result.page);
    } catch (err: any) {
      setError(err.message ?? "Failed to load flagged reviews");
    } finally {
      setLoading(false);
    }
  }

  async function acceptFlag(r: FlaggedReview) {
    try {
      setMsg(null);
      const res = await authPost(`/admin/reviews/${r.id}/acceptFlag`);
      setMsg(res.message ?? "Flag accepted");

      setData((prev) =>
        prev
          ? {
              ...prev,
              reviews: prev.reviews.filter((x) => x.id !== r.id),
              totalFlagged: prev.totalFlagged - 1,
            }
          : prev
      );
    } catch (err: any) {
      setError(err.message ?? "Failed to accept flag");
    }
  }

  async function rejectFlag(r: FlaggedReview) {
    try {
      setMsg(null);
      const res = await authPost(`/admin/reviews/${r.id}/rejectFlag`);
      setMsg(res.message ?? "Flag rejected");

      setData((prev) =>
        prev
          ? {
              ...prev,
              reviews: prev.reviews.filter((x) => x.id !== r.id),
              totalFlagged: prev.totalFlagged - 1,
            }
          : prev
      );
    } catch (err: any) {
      setError(err.message ?? "Failed to reject flag");
    }
  }

  // initial load
  useEffect(() => {
    loadPage(1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // fetch movie titles & usernames for the current page
  useEffect(() => {
    if (!data?.reviews || data.reviews.length === 0) return;

    const missingMovieIds = Array.from(
      new Set(
        data.reviews
          .map((r) => r.movieId)
          .filter((id) => movieTitles[id] === undefined)
      )
    );
    const missingUserIds = Array.from(
      new Set(
        data.reviews
          .map((r) => r.userId)
          .filter((id) => usernames[id] === undefined)
      )
    );

    async function fetchExtras() {
      try {
        // movies
        if (missingMovieIds.length > 0) {
          const movieResults = await Promise.allSettled(
            missingMovieIds.map((id) => authGet(`/movies/${id}`))
          );
          setMovieTitles((prev) => {
            const next = { ...prev };
            movieResults.forEach((movie, idx) => {
              const id = missingMovieIds[idx];
              next[id] = movie.status === "fulfilled" ? movie.value.title ?? `Movie #${id}` : `Movie #${id}`;
            });
            return next;
          });
        }

        // users
        if (missingUserIds.length > 0) {
          const userResults = await Promise.allSettled(
            missingUserIds.map((id) =>
              authGet(`/users/userProfile?userId=${id}`)
            )
          );
          setUsernames((prev) => {
            const next = { ...prev };
            userResults.forEach((result, idx) => {
              const id = missingUserIds[idx];
              if (result.status === "fulfilled") {
                const res = result.value;
                const username =
                  res.user?.username || res.username || `User #${id}`;
                next[id] = username;
              } else {
                next[id] = `User #${id}`;
              }
            });
            return next;
          });
        }
      } catch {
        // if these fail, we just fall back to ids, no need to scream at the user
      }
    }

    fetchExtras();
  }, [data]);

  const renderPagination = () =>
    data && (
      <div
        style={{
          display: "flex",
          gap: "0.75rem",
          alignItems: "center",
          margin: "1rem 0",
        }}
      >
        <span>
          Page {data.page}/{data.pageCount} — Total flagged: {data.totalFlagged}
        </span>

        <button
          disabled={page <= 1}
          onClick={() => loadPage(page - 1)}
          style={{ padding: "0.3rem 0.8rem" }}
        >
          Prev
        </button>

        <button
          disabled={page >= data.pageCount}
          onClick={() => loadPage(page + 1)}
          style={{ padding: "0.3rem 0.8rem" }}
        >
          Next
        </button>
      </div>
    );

  if (loading && !data) {
    return <p style={{ color: "#eee", padding: "2rem" }}>Loading...</p>;
  }

  return (
    <div style={{ padding: "2rem", color: "#eee" }}>
      <h2 style={{ marginBottom: "0.5rem" }}>Flagged Reviews</h2>

      {error && <p style={{ color: "tomato" }}>{error}</p>}
      {msg && <p style={{ color: "lightgreen" }}>{msg}</p>}

      {/* top pagination */}
      {renderPagination()}

      {data && data.reviews && data.reviews.length > 0 ? (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {data.reviews.map((r) => {
            const movieTitle = movieTitles[r.movieId] ?? `Movie #${r.movieId}`;
            const username = usernames[r.userId] ?? `User #${r.userId}`;

            return (
              <li
                key={r.id}
                style={{
                  marginBottom: "1rem",
                  padding: "1rem",
                  borderRadius: "8px",
                  background: "#222",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "flex-start",
                  gap: "1rem",
                }}
              >
                {/* LEFT SIDE */}
                <div style={{ flex: 1 }}>
                  {/* movie + user ABOVE title */}
                  <p
                    style={{
                      margin: 0,
                      marginBottom: "0.25rem",
                      fontSize: "0.9rem",
                      opacity: 0.85,
                    }}
                  >
                    {movieTitle} | {username}
                  </p>

                  {/* actual review title */}
                  <p style={{ margin: 0, fontWeight: 600 }}>
                    {r.reviewTitle}
                  </p>

                  <p
                    style={{
                      marginTop: "0.5rem",
                      whiteSpace: "pre-wrap",
                    }}
                  >
                    {r.reviewBody}
                  </p>
                </div>

                {/* RIGHT SIDE ACTION BUTTONS */}
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "0.4rem",
                    minWidth: "140px",
                  }}
                >
                  <button
                    onClick={() => acceptFlag(r)}
                    style={{
                      padding: "0.3rem 0.8rem",
                      cursor: "pointer",
                    }}
                  >
                    Accept Flag
                  </button>
                  <button
                    onClick={() => rejectFlag(r)}
                    style={{
                      padding: "0.3rem 0.8rem",
                      cursor: "pointer",
                    }}
                  >
                    Reject Flag
                  </button>
                </div>
              </li>
            );
          })}
        </ul>
      ) : (
        <p>No flagged reviews on this page.</p>
      )}

      {/* bottom pagination */}
      {renderPagination()}
    </div>
  );
}
