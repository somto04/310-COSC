import { Routes, Route } from 'react-router-dom'
import Header from './components/Header'
//import Homepage from './pages/Homepage'
import Login from './pages/Login'
import CreateAccount from './pages/CreateAccount'
import './App.css'

function App() {
  return (
    <>
      <Header />

      <Routes>
        {/* <Route path="/" element={<Homepage />} /> */}
        <Route path="/login" element={<Login />} />
        <Route path="/create-account" element={<CreateAccount />} />
      </Routes>
    </>
  )
}

export default App
