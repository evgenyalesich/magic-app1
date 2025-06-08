import React, { useEffect, useState } from "react"
import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { initTelegram, fetchCurrentUser } from "./telegram"
import ProductList from "./components/ProductList"
import ProductDetail from "./components/ProductDetail"
import ChatWindow from "./components/ChatWindow"
import "./App.css"

const queryClient = new QueryClient()

function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function authenticate() {
      try {
        // если открыли внутри Telegram WebApp — сначала логин
        if (window.Telegram?.WebApp) {
          await initTelegram()
        }
        // потом подгружаем профиль по куки
        const me = await fetchCurrentUser()
        setUser(me)
      } catch (err) {
        console.error("Ошибка авторизации:", err)
        setUser(null)
      } finally {
        setLoading(false)
      }
    }
    authenticate()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">Загрузка...</div>
    )
  }
  if (!user) {
    return (
      <div className="flex items-center justify-center h-screen">
        Не авторизован
      </div>
    )
  }

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-gray-200">
          <Routes>
            <Route path="/" element={<ProductList />} />
            <Route path="/product/:id" element={<ProductDetail />} />
            <Route path="/chat/:sessionId" element={<ChatWindow user={user} />} />
          </Routes>
        </div>
      </Router>
    </QueryClientProvider>
  )
}

export default App
