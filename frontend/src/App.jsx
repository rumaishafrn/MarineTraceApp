import React, { useState } from 'react'
import './App.css'
import MainPage from './components/MainPage'
import TrackingPage from './components/TrackingPage'
import DetectionPage from './components/DetectionPage'

function App() {
  const [currentPage, setCurrentPage] = useState('main')

  const renderPage = () => {
    switch (currentPage) {
      case 'main':
        return <MainPage onNavigate={setCurrentPage} />
      case 'tracking':
        return <TrackingPage onBack={() => setCurrentPage('main')} />
      case 'detection':
        return <DetectionPage onBack={() => setCurrentPage('main')} />
      default:
        return <MainPage onNavigate={setCurrentPage} />
    }
  }

  return (
    <div className="app">
      {renderPage()}
    </div>
  )
}

export default App
