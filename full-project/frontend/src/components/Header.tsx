import { Link } from 'react-router-dom'
import { clearAuth, getToken } from "../utils/auth";

import './Header.css'

type HeaderProps = {
    token: string | null;
    isAdmin: boolean;
    updateAuth: () => void;
};

function Header({ token, isAdmin, updateAuth }: HeaderProps) {
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
            <Link to="/profile">Profile</Link>
            <Link to="/logout">Logout</Link>
          </>
        )}

        {isAdmin && <Link to="/admin">Admin</Link>}
      </div>
    </nav>
  );
}

export default Header