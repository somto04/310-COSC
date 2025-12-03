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
            </div>
        </nav>
    )
}

export default Header