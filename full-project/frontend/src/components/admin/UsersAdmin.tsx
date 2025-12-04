// src/pages/admin/UsersAdmin.tsx  (same folder level as ReviewsAdmin)

import { useEffect, useState } from "react";
import { authGet, authPut } from "../../api/adminApi";

type UserRow = {
  id: number;
  username: string;
  isAdmin?: boolean;
};

export default function UsersAdmin() {
    const [page, setPage] = useState(1);
    const [pageSize] = useState(10);

    const [users, setUsers] = useState<UserRow[]>([]);
    const [hasNextPage, setHasNextPage] = useState(false);

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [msg, setMsg] = useState<string | null>(null);

    // for “are you sure?” double-click
    const [confirmAction, setConfirmAction] = useState<{
        userId: number;
        action: "grant" | "revoke";
    } | null>(null);

    const [pageInput, setPageInput] = useState("");

    const handlePageJump = () => {
    const num = Number(pageInput);
    if (!num || num < 1) return;
    loadPage(num);
    };


  async function loadPage(p: number) {
    try {
      setLoading(true);
      setError(null);
      setMsg(null);
      setConfirmAction(null);

      const query = `?page=${p}&limit=${pageSize}`;
      const result = await authGet(`/users${query}`);

      if (!Array.isArray(result)) {
        throw new Error("Unexpected users response");
      }

      setUsers(result);
      setPage(p);
      setHasNextPage(result.length === pageSize);
    } catch (err: any) {
      setError(err.message ?? "Failed to load users");
    } finally {
      setLoading(false);
    }
  }

  async function doGrant(user: UserRow) {
    try {
      setMsg(null);
      const res = await authPut(`/admin/${user.id}/grantAdmin`);
      setMsg(res.message ?? `Granted admin to ${user.username}`);

      setUsers((prev) =>
        prev.map((u) =>
          u.id === user.id ? { ...u, isAdmin: true } : u
        )
      );
    } catch (err: any) {
      setError(err.message ?? "Failed to grant admin");
    }
  }

  async function doRevoke(user: UserRow) {
    try {
      setMsg(null);
      const res = await authPut(`/admin/${user.id}/revokeAdmin`);
      setMsg(res.message ?? `Revoked admin from ${user.username}`);

      setUsers((prev) =>
        prev.map((u) =>
          u.id === user.id ? { ...u, isAdmin: false } : u
        )
      );
    } catch (err: any) {
      setError(err.message ?? "Failed to revoke admin");
    }
  }

  function handleGrantClick(user: UserRow) {
    if (
      confirmAction &&
      confirmAction.userId === user.id &&
      confirmAction.action === "grant"
    ) {
      setConfirmAction(null);
      void doGrant(user);
    } else {
      setConfirmAction({ userId: user.id, action: "grant" });
    }
  }

  function handleRevokeClick(user: UserRow) {
    if (
      confirmAction &&
      confirmAction.userId === user.id &&
      confirmAction.action === "revoke"
    ) {
      setConfirmAction(null);
      void doRevoke(user);
    } else {
      setConfirmAction({ userId: user.id, action: "revoke" });
    }
  }

  useEffect(() => {
    loadPage(1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const renderPagination = () => (
  <div
    style={{
      display: "flex",
      gap: "0.75rem",
      alignItems: "center",
      margin: "1rem 0",
    }}
  >
    <span>Page {page}</span>

    <input
      type="number"
      min="1"
      placeholder="Go to page"
      value={pageInput}
      onChange={(e) => setPageInput(e.target.value)}
      aria-label="Page number"
      style={{
        width: "80px",
        padding: "0.3rem",
        background: "#111",
        color: "#eee",
        border: "1px solid #444",
        borderRadius: "4px",
      }}
    />

    <button
      onClick={handlePageJump}
        style={{ padding: "0.3rem 0.8rem", cursor: "pointer" }}
      aria-label="Navigate to page"
    >
      Go
    </button>

    <button
        disabled={page <= 1}
        aria-label={page <= 1 ? "Already on the first page" : "Go to previous page"}
        onClick={() => loadPage(page - 1)}
        style={{ padding: "0.3rem 0.8rem" }}
    >
        Prev
    </button>

    <button
        disabled={!hasNextPage}
        aria-label={
            !hasNextPage ? "No more pages after this" : "Go to next page"
        }
        onClick={() => loadPage(page + 1)}
        style={{ padding: "0.3rem 0.8rem" }}
    >
        Next
    </button>

  </div>
);

  if (loading && users.length === 0) {
    return (
      <p style={{ color: "#eee", padding: "2rem" }}>
        Loading users...
      </p>
    );
  }

  return (
    <div style={{ padding: "2rem", color: "#eee" }}>
      <h2 style={{ marginBottom: "0.5rem" }}>User Privileges</h2>

      {error && <p style={{ color: "tomato" }}>{error}</p>}
      {msg && <p style={{ color: "lightgreen" }}>{msg}</p>}

      {/* top pagination */}
      {renderPagination()}

      {users.length > 0 ? (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {users.map((u) => {
            const isAdmin = !!u.isAdmin;

            const isConfirmGrant =
              confirmAction &&
              confirmAction.userId === u.id &&
              confirmAction.action === "grant";

            const isConfirmRevoke =
              confirmAction &&
              confirmAction.userId === u.id &&
              confirmAction.action === "revoke";

            return (
              <li
                key={u.id}
                style={{
                  marginBottom: "0.75rem",
                  padding: "0.75rem 1rem",
                  borderRadius: "8px",
                  background: "#222",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <div>
                  <p style={{ margin: 0 }}>
                    <strong>ID:</strong> {u.id}
                  </p>
                  <p style={{ margin: 0 }}>
                    <strong>Username:</strong> {u.username}
                    {isAdmin && (
                      <span
                        style={{
                          marginLeft: "0.5rem",
                          fontSize: "0.85rem",
                          background: "#444",
                          padding: "0.1rem 0.4rem",
                          borderRadius: "999px",
                        }}
                      >
                        admin
                      </span>
                    )}
                  </p>
                </div>

                <div
                  style={{
                    display: "flex",
                    gap: "0.5rem",
                    minWidth: "220px",
                    justifyContent: "flex-end",
                  }}
                >
                  {!isAdmin && (
                    <button
                      onClick={() => handleGrantClick(u)}
                      style={{
                        padding: "0.3rem 0.8rem",
                        cursor: "pointer",
                      }}
                    >
                      {isConfirmGrant ? "Sure? Click again" : "Grant admin"}
                    </button>
                  )}

                  {isAdmin && (
                    <button
                      onClick={() => handleRevokeClick(u)}
                      style={{
                        padding: "0.3rem 0.8rem",
                        cursor: "pointer",
                      }}
                    >
                      {isConfirmRevoke
                        ? "Sure? Click again"
                        : "Revoke admin"}
                    </button>
                  )}
                </div>
              </li>
            );
          })}
        </ul>
      ) : (
        <p>No users on this page.</p>
      )}

      {/* bottom pagination */}
      {renderPagination()}
    </div>
  );
}
