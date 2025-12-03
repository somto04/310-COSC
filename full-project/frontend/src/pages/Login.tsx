import { use, useState } from "react";
import { Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import { setAuth } from "../utils/auth";

type LoginProps = {
  updateAuth: () => void;
};
  
export default function Login({ updateAuth }: LoginProps) {
  const [username, setUsername] = useState("");
  const [pw, setPw] = useState("");
  const [msg, setMsg] = useState("");
  const API = import.meta.env.VITE_API_URL;
  const navigate = useNavigate();
  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();

  

    const formData = new URLSearchParams();
    formData.append("username", username);
    formData.append("password", pw);

    fetch(`${API}/token`, {
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
          setAuth(data.access_token, data.user_id, data.is_admin);
          updateAuth();

          setMsg("You Have Logged In Successfully!");
          navigate("/");

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

    {/* reset password button */}
      <div style={{ marginTop: "1rem" }}>
        <Link to="/reset-password">
          <button style={{ padding: "0.5rem", border: "1px solid black" }}>
            Forgot password? Reset here!
          </button>
        </Link>
      </div>

     {/* New Create Account Button */}
      <div style={{ marginTop: "1rem" }}>
        <Link to="/create-account">
          <button style={{ padding: "0.5rem", border: "1px solid black" }}>
            Create an Account
          </button>
        </Link>
      </div>
    
      {msg && <p>{msg}</p>}
    </div>
  );
}


