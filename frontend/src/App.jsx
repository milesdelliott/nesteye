import { useState, useEffect, useCallback } from 'react'
import VideoStream from './components/VideoStream'
import StatusBar from './components/StatusBar'
import Controls from './components/Controls'
import SystemInfo from './components/SystemInfo'

export default function App() {
  const [status, setStatus] = useState(null)

  const fetchStatus = useCallback(async () => {
    try {
      const res = await fetch('/api/status')
      setStatus(res.ok ? await res.json() : { status: 'offline', camera: 'disconnected' })
    } catch {
      setStatus({ status: 'offline', camera: 'disconnected' })
    }
  }, [])

  useEffect(() => {
    fetchStatus()
    const interval = setInterval(fetchStatus, 5000)
    return () => clearInterval(interval)
  }, [fetchStatus])

  return (
    <div className="app">
      <header className="app-header">
        <h1>Bird Box Camera</h1>
        <p className="subtitle">Live Wildlife Monitor</p>
      </header>
      <main className="app-main">
        <VideoStream />
        <StatusBar status={status} />
        <Controls onRefresh={fetchStatus} />
        <SystemInfo />
      </main>
    </div>
  )
}
