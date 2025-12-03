import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { clearAuth, getToken } from "../utils/auth";

export default function Logout() {
    const navigate = useNavigate();

    useEffect(() => {
        const API = import.meta.env.VITE_API_URL;
        const token = getToken();

        // Try logging out on backend, but don't die if it fails
        fetch(`${API}/logout`, {
            method: "POST",
            headers: { Authorization: `Bearer ${token}` }
        }).catch(() => {});

        // Clear local auth info
        clearAuth();

        // After a tiny moment, redirect home
        setTimeout(() => navigate("/"), 300);
    }, []);

    return (
        <div style={{ padding: "2rem", color: "white" }}>
            <h1>Logging out…</h1>
        </div>
    );
}
