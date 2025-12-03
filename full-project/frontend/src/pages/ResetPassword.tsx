import { useState } from "react";
import { useNavigate } from "react-router-dom";

const API = import.meta.env.VITE_API_URL;

export default function ResetPassword() {
  const [username, setUsername] = useState("");
  const [resetToken, setResetToken] = useState<string | null>(null);
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    // Step 1: NO TOKEN YET → generate token
    if (!resetToken) {
      const formData = new FormData();
      formData.append("username", username);

      try {
        const res = await fetch(`${API}/generate-reset-token`, {
          method: "POST",
          body: formData,
        });

        const data = await res.json();

        if (!res.ok) {
          setError(data.detail || "Could not generate reset token");
          return;
        }

        setResetToken(data.token); // browser stores the token safely in state!
        setMessage("Token generated. Enter your new password.");
        setError("");
      } catch (err) {
        setError("Network error");
      }

      return;
    }

    // Step 2: TOKEN EXISTS → allow password reset
    if (newPassword !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    const formData = new FormData();
    formData.append("token", resetToken);
    formData.append("newPassword", newPassword);

    try {
      const res = await fetch(`${API}/reset-password`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || "Failed to reset password");
        return;
      }

      setMessage("Password reset successful!");
      setTimeout(() => navigate("/login"), 1500);
    } catch (err) {
      setError("Network error");
    }
  }

  return (
    <div style={{ padding: "2rem", maxWidth: "400px", margin: "0 auto" }}>
      <h1>Reset Password</h1>

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        {/* Username field (only before token is generated) */}
        {!resetToken && (
          <input
            type="text"
            placeholder="Enter your username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        )}

        {/* New password fields (only after token is generated) */}
        {resetToken && (
          <>
            <input
              type="password"
              placeholder="New password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
            />
            <input
              type="password"
              placeholder="Confirm password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
            />
          </>
        )}

        <button type="submit">
          {!resetToken ? "Generate Token" : "Reset Password"}
        </button>
      </form>

      {error && <p style={{ color: "red" }}>{error}</p>}
      {message && <p style={{ color: "green" }}>{message}</p>}
    </div>
  );
}
