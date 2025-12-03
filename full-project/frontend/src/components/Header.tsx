import { Link } from 'react-router-dom'
import './Header.css'

function Header() {
    return (
        <nav className="header">
            <div className="nav-links">
                <Link to="/test">Test</Link>
                <Link to="/">Home</Link>
                <Link to="/login">Login</Link>
                <Link to="/create-account">Sign Up</Link>
                <Link to="/profile">Profile</Link>
                <Link to="/liked-reviews">Liked Reviews</Link>
                <Link to="/watchlist">Watchlist</Link>
                <Link to="/favorite-movies">Favorite Movies</Link>
                <Link to="/reset-password">Reset Password</Link>
                <Link to="/admin">Admin</Link>
            </div>
        </nav>
    )
}

export default Header