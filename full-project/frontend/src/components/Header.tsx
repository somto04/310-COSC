import { Link } from 'react-router-dom'

import './Header.css'

type HeaderProps = {
    token: string | null;
    isAdmin: boolean;
    username: string | null;
};

function Header({ token, isAdmin, username }: HeaderProps) {
    return (
        <nav className="header">
            <div className="nav-links">

            <Link to="/test">Test</Link>
            <Link to="/">Home</Link>

            {!token && (
                <>
                <Link to="/login">Login</Link>
                <Link to="/create-account">Sign Up</Link>
                </>
            )}

            {token && (
                <>
                <Link to="/profile">{username || "Profile"}</Link>
                <Link to="/logout">Logout</Link>
                </>
            )}

            {isAdmin && <Link to="/admin">Admin</Link>}
            </div>
        </nav>
    );
}

export default Header