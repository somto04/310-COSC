import Header from './components/Header'
import Login from './pages/Login'
import Logout from './pages/Logout'
import CreateAccount from './pages/CreateAccount'
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Profile from "./pages/Profile";
import LikedReviews from "./pages/LikedReviews";
import FavoriteMovies from "./pages/FavoriteMovies";
import Watchlist from "./pages/Watchlist";
import ResetPassword from './pages/ResetPassword';
import Homepage from './pages/Homepage';
import './App.css'
import TestPage from './pages/testPage'
import AdminPage from './pages/AdminPage';
import MovieDetails from './pages/MovieDetails';

import { useState, useEffect } from "react";
import { getToken, getIsAdmin, requireAuth } from "./utils/auth";

function App() {
  const [token, setToken] = useState(getToken());
  const [isAdmin, setIsAdmin] = useState(getIsAdmin());

  const updateAuth = () => {
    setToken(getToken());
    setIsAdmin(getIsAdmin());
  };

  return (
    <BrowserRouter>
      <Header token={token} isAdmin={isAdmin} updateAuth={updateAuth} />

      <Routes>
        <Route path="/" element={<Homepage/>} />
        <Route
          path="/login"
          element={<Login updateAuth={updateAuth} />}
        />
        <Route 
          path="/logout" 
          element={requireAuth(<Logout updateAuth={updateAuth} />)} 
        />

        <Route path="/profile" element={requireAuth(<Profile />)} />
        <Route path="/create-account" element={<CreateAccount />} />
        <Route path="/liked-reviews" element={requireAuth(<LikedReviews />)} />
        <Route path="/watchlist" element={requireAuth(<Watchlist />)} />
        <Route path="/favorite-movies" element={requireAuth(<FavoriteMovies />)} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/admin" element={<AdminPage />} />

        <Route path="/test" element={<TestPage />} />
        <Route path="/movies/:movieId" element={<MovieDetails />} />
      </Routes>
    </BrowserRouter>
  );
}
export default App;
