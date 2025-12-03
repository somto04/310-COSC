import { useState } from "react";
import { useNavigate } from "react-router-dom";
const API = import.meta.env.VITE_API_URL;

const navigate = useNavigate();

export default function Register() {
  const [username, setUsername] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [pw, setPassword] = useState("");
  const [age, setAge] = useState("");
  const [message, setMessage] = useState("");
  
  // Clean labels for each backend field
  const fieldLabels: Record<string, string> = {
    username: "Username",
    firstName: "First name",
    lastName: "Last name",
    email: "Email",
    age: "Age",
    pw: "Password",
  };

  // Convert backend error messages into user-friendly format
  function formatError(field: string, msg: string, ctx: any) {
    const label = fieldLabels[field] || field;

    
    if (msg.includes("at least 1 character") || msg.includes("too_short")) {
      return `${label} cannot be empty.`;
    }

    
    if (msg.includes("at least") && msg.includes("characters")) {
      return `${label} must be at least ${ctx?.min_length} characters.`;
    }

    
    if (msg.includes("greater than or equal")) {
      return `${label} must be at least ${ctx?.ge}.`;
    }

    // required field
    if (msg === "Field required") {
      return `${label} is required.`;
    }

    return `${label}: ${msg}`;
  }

  const handleRegister = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    fetch(`${API}/users`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    username,
    firstName,
    lastName,
    email,
    age: Number(age),
    pw,
  }),
})

      .then(async (res) => {
        const data = await res.json();

        // Handle backend validation errors
        if (!res.ok) {
          if (Array.isArray(data.detail)) {
            const messages = data.detail.map((err: any) =>
              formatError(err.loc?.[1], err.msg, err.ctx)
            );
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

        
        setMessage("Account created successfully!");

        
        navigate("/");
      })
      .catch((err) => {
        console.error("Error creating account:", err);
        setMessage("Network error. Please try again.");
      });
  };

  return (
    <div style={{ padding: "2rem", maxWidth: "400px", margin: "0 auto" }}>
      <h1>Create Account</h1>

      <form
        onSubmit={handleRegister}
        style={{ display: "flex", flexDirection: "column", gap: "0.7rem", marginTop: "1rem" }}
      >
        <input
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          style={{ padding: "0.5rem", border: "1px solid black" }}
        />

        <input
          placeholder="First name"
          value={firstName}
          onChange={(e) => setFirstName(e.target.value)}
          style={{ padding: "0.5rem", border: "1px solid black" }}
        />

        <input
          placeholder="Last name"
          value={lastName}
          onChange={(e) => setLastName(e.target.value)}
          style={{ padding: "0.5rem", border: "1px solid black" }}
        />

        <input
          placeholder="Email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={{ padding: "0.5rem", border: "1px solid black" }}
        />

        <input
          placeholder="Password"
          type="password"
          value={pw}
          onChange={(e) => setPassword(e.target.value)}
          style={{ padding: "0.5rem", border: "1px solid black" }}
        />

        <input
          placeholder="Age"
          type="number"
          value={age}
          onChange={(e) => setAge(e.target.value)}
          style={{ padding: "0.5rem", border: "1px solid black" }}
        />

        <button
          type="submit"
          style={{ padding: "0.6rem", border: "1px solid black", cursor: "pointer" }}
        >
          Create Account
        </button>
      </form>

      {message && (
        <pre
          style={{
            marginTop: "1rem",
            whiteSpace: "pre-wrap",
            color: "red",
            fontSize: "0.9rem",
          }}
        >
          {message}
        </pre>
      )}
    </div>
  );
}
