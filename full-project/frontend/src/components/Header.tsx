import { Link } from 'react-router-dom'
import './Header.css'

function Header() {
    const token = localStorage.getItem("token");
    const isAdmin = localStorage.getItem("isAdmin") === "true";
    const API = import.meta.env.VITE_API_URL;


    return (
        <nav className="header">
            <div className="nav-links">
                <Link to="/test">Test</Link>
                <Link to="/">Home</Link>
                

                {/* Only show these if NOT logged in */}
                {!token && (
                <>
                    <Link to="/login">Login</Link>
                    <Link to="/create-account">Sign Up</Link>
                </>
                )}
                {/* Only show these if logged in */}
                {token && (
                <>
                    <button
                        onClick={() => {
                        const token = localStorage.getItem("token");
                        fetch(`${API}/default/logout`, {

                            method: "POST",
                            headers: { Authorization: `Bearer ${token}` },
                        }).catch(() => {});

                        localStorage.removeItem("token");
                        localStorage.removeItem("userId");
                        localStorage.removeItem("isAdmin");
                        window.location.href = "/login";
                        }}
                        style={{
                        padding: "0.5rem 1rem",
                        border: "1px solid black",
                        background: "red",
                        cursor: "pointer",
                        marginTop: "1rem",
                        }}
                    >
                        Logout
                    </button>
                    <Link to="/profile">Profile</Link>
                    <Link to="/watchlist">Watchlist</Link>
                    <Link to="/favorite-movies">Favorite Movies</Link>
                </>
                )}
                {isAdmin && <Link to="/admin">Admin</Link>}
            </div>
        </nav>
    )
}

export default Header