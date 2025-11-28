import { useState } from "react";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage("");

    // Create FormData to match FastAPI's Form(...) parameters
    const formData = new FormData();
    formData.append("username", username);
    formData.append("password", password);

    fetch("http://localhost:8000/token", {
      method: "POST",
      body: formData,  // Send as form data, not JSON
    })
      .then(async (res) => {
        const data = await res.json();

        // Handle errors
        if (!res.ok) {
          // Handle 401 (invalid credentials)
          if (res.status === 401) {
            setMessage("Invalid username or password.");
            return;
          }

          // Handle 403 (banned user)
          if (res.status === 403) {
            setMessage(data.detail || "Account banned due to repeated violations.");
            return;
          }

          // Handle validation errors
          if (Array.isArray(data.detail)) {
            const messages = data.detail.map((err: any) => {
              const field = err.loc?.[1] || "Field";
              return `${field}: ${err.msg}`;
            });
            setMessage(messages.join("\n"));
            return;
          }

          if (typeof data.detail === "string") {
            setMessage(data.detail);
            return;
          }

          setMessage("Something went wrong.");
          return;
        }

        // Success! Store the token
        localStorage.setItem("authToken", data.access_token);
        localStorage.setItem("tokenType", data.token_type);
        
        setMessage("Login successful!");

        // Redirect to home page
        setTimeout(() => {
          window.location.href = "/";
        }, 500);
      })
      .catch((err) => {
        console.error("Error logging in:", err);
        setMessage("Network error. Please try again.");
      })
      .finally(() => {
        setIsLoading(false);
      });
  };

  return (
    <div style={{ padding: "2rem", maxWidth: "400px", margin: "0 auto" }}>
      <h1>Login</h1>

      <form
        onSubmit={handleLogin}
        style={{ display: "flex", flexDirection: "column", gap: "0.7rem", marginTop: "1rem" }}
      >
        <input
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          style={{ padding: "0.5rem", border: "1px solid black" }}
          disabled={isLoading}
        />

        <input
          placeholder="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{ padding: "0.5rem", border: "1px solid black" }}
          disabled={isLoading}
        />

        <button
          type="submit"
          style={{
            padding: "0.6rem",
            border: "1px solid black",
            cursor: isLoading ? "not-allowed" : "pointer",
            backgroundColor: isLoading ? "#ccc" : "white",
          }}
          disabled={isLoading}
        >
          {isLoading ? "Logging in..." : "Login"}
        </button>
      </form>

      {message && (
        <pre
          style={{
            marginTop: "1rem",
            whiteSpace: "pre-wrap",
            color: message === "Login successful!" ? "green" : "red",
            fontSize: "0.9rem",
          }}
        >
          {message}
        </pre>
      )}

      <p style={{ marginTop: "1.5rem", textAlign: "center" }}>
        Don't have an account?{" "}
        <a href="/register" style={{ color: "blue", textDecoration: "underline" }}>
          Create one here
        </a>
      </p>

      <p style={{ marginTop: "0.5rem", textAlign: "center" }}>
        <a href="/forgot-password" style={{ color: "blue", textDecoration: "underline" }}>
          Forgot password?
        </a>
      </p>
    </div>
  );
}