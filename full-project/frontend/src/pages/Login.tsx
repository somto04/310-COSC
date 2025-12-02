import { useState } from "react";

export default function Login() {
  const [username, setUsername] = useState("");
  const [pw, setPw] = useState("");
  const [msg, setMsg] = useState("");
  const BASE_URL = "http://localhost:8000";
  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();

    const formData = new URLSearchParams();
    formData.append("username", username);
    formData.append("password", pw);

    fetch(`${BASE_URL}/token`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: formData.toString(),
    })
      .then((res) => res.json())
      .then((data) => {
        console.log("LOGIN RESPONSE:", data);

        if (data.access_token) {
          localStorage.setItem("token", data.access_token);
          localStorage.setItem("userId", data.userId); // your backend must return this
          setMsg("Logged in! Token + userId saved.");
        } else {
          setMsg("Login failed. Check username/password.");
        }
      })
      .catch(() => setMsg("Network error"));
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Login</h1>

      <form onSubmit={handleLogin} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        <input
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          style={{ padding: "0.5rem", border: "1px solid black" }}
        />

        <input
          placeholder="Password"
          type="password"
          value={pw}
          onChange={(e) => setPw(e.target.value)}
          style={{ padding: "0.5rem", border: "1px solid black" }}
        />

        <button type="submit" style={{ padding: "0.5rem", border: "1px solid black" }}>
          Login
        </button>
      </form>

      {msg && <p>{msg}</p>}
    </div>
  );
}


