
import Header from './components/Header'
import Login from './pages/Login'
import CreateAccount from './pages/CreateAccount'
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Profile from "./pages/Profile";
import LikedReviews from "./pages/LikedReviews";
import FavoriteMovies from "./pages/FavoriteMovies";
import Watchlist from "./pages/Watchlist";
import ResetPassword from './pages/ResetPassword';
import Homepage from './pages/Homepage';


function App() {
  return (
    <BrowserRouter>
      <Header />
      <Routes>
        <Route path="/homepage" element={<Homepage/>} />
        <Route path="/login" element={<Login />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/create-account" element={<CreateAccount />} />
        <Route path="/liked-reviews" element={<LikedReviews />} />
        <Route path="/watchlist" element={<Watchlist />} />
        <Route path="/favorite-movies" element={<FavoriteMovies />} />
        <Route path="/reset-password" element={<ResetPassword />} />

      </Routes>
    </BrowserRouter>
  );
}
export default App;
