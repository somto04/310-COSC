import { useState } from "react";

const API = import.meta.env.VITE_API_URL;

export default function TestPage() {
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string>("");

  // auth + pagination inputs
  const [token, setToken] = useState<string>("");
  const [page, setPage] = useState<string>("1");
  const [count, setCount] = useState<string>("10");

  async function hit(endpoint: string, method = "GET", body?: any) {
    setError("");
    setResult("");

    try {
      const headers: HeadersInit = {
        "Content-Type": "application/json",
      };

      if (token.trim()) {
        headers["Authorization"] = `Bearer ${token.trim()}`;
      }

      const res = await fetch(`${API}${endpoint}`, {
        method,
        headers,
        body: body ? JSON.stringify(body) : undefined,
      });

      const data = await res.json().catch(() => null);
      setResult({ status: res.status, data });
    } catch (e: any) {
      setError(e.message || "uhh it exploded");
    }
  }

  function buildUsersQuery() {
    const params = new URLSearchParams();
    if (page) params.set("page", page);
    if (count) params.set("count", count);
    const qs = params.toString();
    return `/users${qs ? `?${qs}` : ""}`;
  }

  return (
    <div
      style={{
        padding: "20px",
        color: "#ddd",
        background: "#222",
        minHeight: "100vh",
        fontFamily: "system-ui, sans-serif",
      }}
    >
      <h1>Test Page</h1>

      {/* basic endpoints */}
      <div style={{ display: "flex", gap: "12px", marginBottom: "16px" }}>
        <button onClick={() => hit("/movies")}>GET /movies</button>
        <button
          onClick={() =>
            hit("/movies", "POST", {
              title: "Test Movie",
              movieGenres: ["Action"],
              directors: ["Me"],
              mainStars: ["You"],
              duration: 120,
            })
          }
        >
          POST /movies
        </button>
        <button onClick={() => hit("/reviews")}>GET /reviews</button>
      </div>

      {/* auth + users tester */}
      <div
        style={{
          marginTop: "24px",
          padding: "16px",
          borderRadius: "8px",
          background: "#111",
        }}
      >
        <h2>Auth & Users tester</h2>

        <div style={{ marginBottom: "12px" }}>
          <label style={{ display: "block", marginBottom: "4px" }}>
            JWT Token (paste from /login)
          </label>
          <input
            type="text"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            style={{
              width: "100%",
              padding: "8px",
              borderRadius: "4px",
              border: "1px solid #555",
              background: "#222",
              color: "#eee",
            }}
          />
        </div>

        <div
          style={{
            display: "flex",
            gap: "12px",
            marginBottom: "12px",
          }}
        >
          <div>
            <label style={{ display: "block", marginBottom: "4px" }}>page</label>
            <input
              type="number"
              min={1}
              value={page}
              onChange={(e) => setPage(e.target.value)}
              style={{
                padding: "6px 8px",
                borderRadius: "4px",
                border: "1px solid #555",
                background: "#222",
                color: "#eee",
                width: "80px",
              }}
            />
          </div>
          <div>
            <label style={{ display: "block", marginBottom: "4px" }}>count</label>
            <input
              type="number"
              min={1}
              value={count}
              onChange={(e) => setCount(e.target.value)}
              style={{
                padding: "6px 8px",
                borderRadius: "4px",
                border: "1px solid #555",
                background: "#222",
                color: "#eee",
                width: "80px",
              }}
            />
          </div>
        </div>

        <button onClick={() => hit(buildUsersQuery())}>
          GET /users?page={page}&count={count}
        </button>
      </div>

      {/* output */}
      <div style={{ marginTop: "24px" }}>
        <h3>Result</h3>
        <pre
          style={{
            background: "#111",
            padding: "12px",
            borderRadius: "8px",
            maxHeight: "400px",
            overflow: "auto",
          }}
        >
          {JSON.stringify(result, null, 2)}
        </pre>

        {error && (
          <div style={{ color: "tomato", marginTop: "8px" }}>
            <strong>Error:</strong> {error}
          </div>
        )}
      </div>
    </div>
  );
}
