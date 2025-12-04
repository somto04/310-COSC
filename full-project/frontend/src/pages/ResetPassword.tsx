import { useState } from "react";
import { useNavigate } from "react-router-dom";

const API = import.meta.env.VITE_API_URL;

export default function ResetPassword() {
  const [username, setUsername] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const navigate = useNavigate();

  const handleReset = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setMessage("");

    if (!username || !newPassword || !confirmPassword) {
      setError("All fields are required");
      return;
    }

    if (newPassword !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    try {
      // 1️⃣ Generate reset token
      const tokenRes = await fetch(`${API}/generate-reset-token`, {
        method: "POST",
        body: new URLSearchParams({ username }),
      });

      if (!tokenRes.ok) {
        const data = await tokenRes.json();
        setError(data.detail || "Failed to generate reset token");
        return;
      }

      const { token } = await tokenRes.json();

      // 2️⃣ Reset password using token
      const resetRes = await fetch(`${API}/reset-password`, {
        method: "POST",
        body: new URLSearchParams({ token, new_password: newPassword }),
      });

      const resetData = await resetRes.json();

      if (!resetRes.ok) {
        setError(resetData.detail || "Failed to reset password");
        return;
      }

      setMessage("Password reset successful!");
      setTimeout(() => navigate("/login"), 1200);

    } catch (err) {
      setError("Network error. Try again.");
    }
  };

  return (
    <div style={{ padding: "2rem", maxWidth: "400px", margin: "0 auto" }}>
      <h1>Reset Password</h1>

      <form
        onSubmit={handleReset}
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "1rem",
          marginTop: "1rem",
        }}
      >
        {/* Username Field*/}
        <input
          type="text"
          placeholder="Enter your username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          style={{ padding: "0.5rem", border: "1px solid black" }}
        />

        {/* NEW PASSWORD */}
        <input
          type="password"
          placeholder="New password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          style={{ padding: "0.5rem", border: "1px solid black" }}
        />

        {/* CONFIRM PASSWORD */}
        <input
          type="password"
          placeholder="Confirm new password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          style={{ padding: "0.5rem", border: "1px solid black" }}
        />

        <button
          type="submit"
          style={{ padding: "0.6rem", border: "1px solid black" }}
        >
          Reset Password
        </button>
      </form>

      {error && <p style={{ color: "red", marginTop: "1rem" }}>{error}</p>}
      {message && <p style={{ color: "green", marginTop: "1rem" }}>{message}</p>}
    </div>
  );
}
