import { useRef, useState } from 'react'

export default function VideoStream() {
  const imgRef = useRef(null)
  const [error, setError] = useState(false)

  const handleFullscreen = () => {
    imgRef.current?.requestFullscreen()
  }

  return (
    <div className="card video-card">
      {error ? (
        <div className="stream-offline">
          <span>📷</span>
          <p>Camera Offline</p>
        </div>
      ) : (
        <img
          ref={imgRef}
          src="/video_feed"
          alt="Live bird box stream"
          className="stream-img"
          onError={() => setError(true)}
        />
      )}
      <button className="fullscreen-btn" onClick={handleFullscreen}>
        ⛶ Fullscreen
      </button>
    </div>
  )
}
