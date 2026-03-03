function formatUptime(seconds) {
  if (seconds == null) return '--'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  return `${h}h ${m}m ${s}s`
}

export default function StatusBar({ status }) {
  const isOnline = status?.status === 'online'

  return (
    <div className="card status-bar">
      <div className="live-indicator">
        <span className={`dot ${isOnline ? 'dot-live' : 'dot-offline'}`} />
        <span>{isOnline ? 'LIVE' : 'OFFLINE'}</span>
      </div>
      <div className="status-stats">
        <div className="stat">
          <span className="stat-label">Uptime</span>
          <span className="stat-value">{formatUptime(status?.uptime_seconds)}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Camera</span>
          <span className="stat-value">{status?.camera ?? '--'}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Last Update</span>
          <span className="stat-value">
            {status?.timestamp
              ? new Date(status.timestamp).toLocaleTimeString()
              : '--'}
          </span>
        </div>
      </div>
    </div>
  )
}
