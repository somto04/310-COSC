import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { clearAuth, getToken } from "../utils/auth";

type LogoutProps = {
    updateAuth: () => void;
};
    
export default function Logout({ updateAuth }: LogoutProps) {
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

        updateAuth();
        
        // Redirect to home after logout
        navigate("/");
    }, []);

    return (
        <div style={{ padding: "2rem", color: "white" }}>
            <h1>Logging out…</h1>
        </div>
    );
}
