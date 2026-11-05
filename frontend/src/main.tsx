import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryProvider } from './providers/QueryProvider'
import { AuthProvider } from './context/AuthContext'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryProvider>
      <AuthProvider>
        <App />
      </AuthProvider>
    </QueryProvider>
  </React.StrictMode>,
)
