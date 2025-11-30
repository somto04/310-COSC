import { useState } from 'react'
import './App.css'
import CreateAccount from './pages/CreateAccount'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div>
      <CreateAccount />
    </div>
  )
}

export default App
