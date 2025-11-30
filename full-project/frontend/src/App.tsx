import { useState } from 'react'
import './App.css'
import CreateAccount from './pages/CreateAccount'
import { BrowserRouter, Routes, Route } from "react-router-dom";
import TempLogin from "./pages/TempLogin";
import Profile from "./pages/Profile";
import LikedReviews from "./pages/LikedReviews";
import FavoriteMovies from "./pages/FavoriteMovies";
import Watchlist from "./pages/Watchlist";


function App() {
  return (
    <BrowserRouter>
      <h1></h1>
      <Routes>
        <Route path="/" element={<h1>Home Page Placeholder</h1>} />
        <Route path="/temp-login" element={<TempLogin />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/create-account" element={<CreateAccount />} />
        <Route path="/liked-reviews" element={<LikedReviews />} />
        <Route path="/watchlist" element={<Watchlist />} />
        <Route path="/favorite-movies" element={<FavoriteMovies />} />

      </Routes>
    </BrowserRouter>
  );
}
export default App;
