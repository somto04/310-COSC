import { BrowserRouter, Routes, Route } from "react-router-dom";
import TempLogin from "./pages/TempLogin";
import Profile from "./pages/Profile";

function App() {
  return (
    <BrowserRouter>
      <h1>Sample homepage</h1>
      <Routes>
        <Route path="/" element={<h1>Home Page Placeholder</h1>} />
        <Route path="/temp-login" element={<TempLogin />} />
        <Route path="/profile" element={<Profile />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
