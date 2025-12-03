import { useEffect, useState } from "react";
import { authDelete, authGet, authPost } from "../../api/adminApi";

type FlaggedReview = {
  id: number;
  reviewId?: number;
  movieId?: number;
  userId?: number;
  content?: string;
  flaggedReason?: string;
};

export default function ReviewsAdmin() {
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [msg, setMsg] = useState<string | null>(null);

  function getReviewId(r: FlaggedReview) {
    return r.reviewId ?? r.id;
  }

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
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function acceptFlag(r: FlaggedReview) {
    setMsg(null);
    try {
      const rid = getReviewId(r);
      const res = await authPost(`/admin/reviews/${rid}/acceptFlag`);
      setMsg(res.message);
      // remove the review locally
      setData((prev: any) => ({
        ...prev,
        reviews: prev.reviews.filter((x: any) => getReviewId(x) !== rid),
      }));
    } catch (err: any) {
      setError(err.message);
    }
  }

  async function rejectFlag(r: FlaggedReview) {
    setMsg(null);
    try {
      const rid = getReviewId(r);
      const res = await authPost(`/admin/reviews/${rid}/rejectFlag`);
      setMsg(res.message);
      setData((prev: any) => ({
        ...prev,
        reviews: prev.reviews.filter((x: any) => getReviewId(x) !== rid),
      }));
    } catch (err: any) {
      setError(err.message);
    }
  }

  useEffect(() => {
    loadPage(page);
  }, []);

async function deleteReview(r: FlaggedReview) {
  setMsg(null);
  try {
    const rid = getReviewId(r);

    await authDelete(`/reviews/${rid}`);  // ← DELETE, not POST

    setMsg(`Review #${rid} deleted.`);

    setData((prev: any) => ({
      ...prev,
      reviews: prev.reviews.filter(
        (x: any) => getReviewId(x) !== rid
      ),
      totalFlagged: prev.totalFlagged - 1,
    }));
  } catch (err: any) {
    setError(err.message);
  }
}

  if (loading && !data) return <p>Loading...</p>;

  return (
    <div>
      <h2>Flagged Reviews</h2>

      {error && <p style={{ color: "red" }}>{error}</p>}
      {msg && <p style={{ color: "green" }}>{msg}</p>}

      {data && (
        <>
          <p>
            Page {data.page}/{data.pageCount} — Total flagged:{" "}
            {data.totalFlagged}
          </p>

          <button disabled={page <= 1} onClick={() => loadPage(page - 1)}>
            Prev
          </button>

          <button
            disabled={page >= data.pageCount}
            onClick={() => loadPage(page + 1)}
          >
            Next
          </button>

          <ul style={{ listStyle: "none", padding: 0 }}>
            {data.reviews.map((r: FlaggedReview) => (
              <li key={getReviewId(r)} style={{ marginBottom: "1rem" }}>
                <p>
                  <strong>Review #{getReviewId(r)}</strong>{" "}
                  (user {r.userId}, movie {r.movieId})
                </p>
                <p>{r.content}</p>
                <p>Reason: {r.flaggedReason}</p>

                <button onClick={() => acceptFlag(r)}>Accept Flag</button>
                <button onClick={() => rejectFlag(r)}>Reject Flag</button>
                <button onClick={() => deleteReview(r)}>Delete Review</button>
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
