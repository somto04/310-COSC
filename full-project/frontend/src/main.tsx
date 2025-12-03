import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import './index.css'
import App from './App'

localStorage.removeItem("token");
localStorage.removeItem("userId");
localStorage.removeItem("isAdmin");

createRoot(document.getElementById('root')!).render(
  <StrictMode>
      <App />
  </StrictMode>
)

