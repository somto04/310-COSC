import { useState } from "react";
import { useNavigate } from "react-router-dom";

const API = import.meta.env.VITE_API_URL;

export default function ResetPassword() {
  const [username, setUsername] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");
  
  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    if (!resetToken) {
      const formData = new FormData();
      formData.appen
    }
  }
  const handleReset = (e: React.FormEvent) => {
    e.preventDefault();

    // placeholder for future fetch call
    // will do API call here later
    // then redirect:
    setMessage("Password reset successful!");
    setTimeout(() => navigate("/login"), 1200);
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
          type="username"
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

      {message && (
        <p style={{ color: "green", marginTop: "1rem" }}>{message}</p>
      )}
    </div>
  );
}
