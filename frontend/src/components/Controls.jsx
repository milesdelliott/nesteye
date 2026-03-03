import { useState } from 'react'

export default function Controls({ onRefresh }) {
  const [capturing, setCapturing] = useState(false)

  const handleCapture = async () => {
    setCapturing(true)
    try {
      const res = await fetch('/api/capture', { method: 'POST' })
      if (!res.ok) throw new Error('Capture failed')
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `nesteye-${Date.now()}.jpg`
      a.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      console.error('Capture error:', err)
    } finally {
      setCapturing(false)
    }
  }

  return (
    <div className="card controls">
      <button onClick={handleCapture} disabled={capturing}>
        {capturing ? 'Capturing...' : '📷 Capture Photo'}
      </button>
      <button onClick={onRefresh}>↻ Refresh Status</button>
    </div>
  )
}
