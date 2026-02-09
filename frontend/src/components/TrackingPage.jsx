import React, { useState } from 'react'
import axios from 'axios'
import './TrackingPage.css'

function TrackingPage({ onBack }) {
  const [formData, setFormData] = useState({
    location: '',
    latitude: '',
    longitude: '',
    start_date: new Date().toISOString().split('T')[0],
    days: ''
  })

  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleLocationChange = (e) => {
    const location = e.target.value
    setFormData(prev => ({
      ...prev,
      location,
      // Set default coordinates based on location
      latitude: location === 'Takalar' ? '-5.3971' : location === 'Mamuju' ? '-2.6797' : '',
      longitude: location === 'Takalar' ? '119.4419' : location === 'Mamuju' ? '118.8897' : ''
    }))
  }

  const startTracking = async () => {
    // Validation
    if (!formData.location || !formData.latitude || !formData.longitude || !formData.days) {
      alert('Mohon lengkapi semua field!')
      return
    }

    setLoading(true)
    setProgress(0)
    setError(null)

    // Simulate progress
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval)
          return prev
        }
        return prev + 10
      })
    }, 200)

    try {
      const response = await axios.post('/api/track', {
        location: formData.location,
        latitude: parseFloat(formData.latitude),
        longitude: parseFloat(formData.longitude),
        start_date: formData.start_date,
        days: parseInt(formData.days)
      })

      clearInterval(progressInterval)
      setProgress(100)

      setTimeout(() => {
        setResults(response.data.data)
        setLoading(false)
      }, 500)

    } catch (err) {
      clearInterval(progressInterval)
      setLoading(false)
      setError(err.response?.data?.error || 'Terjadi kesalahan saat tracking')
      console.error('Tracking error:', err)
    }
  }

  const resetTracking = () => {
    setResults(null)
    setProgress(0)
    setError(null)
    setFormData({
      location: '',
      latitude: '',
      longitude: '',
      start_date: new Date().toISOString().split('T')[0],
      days: ''
    })
  }

  const formatDate = (dateString) => {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
    const date = new Date(dateString)
    return `${date.getDate()} ${months[date.getMonth()]} ${date.getFullYear()}`
  }

  return (
    <div className="tracking-page slide-in">
      <div className="container">
        <button className="btn btn-secondary back-btn" onClick={onBack}>
          ← Kembali ke Beranda
        </button>

        <div className="content-box">
          <h1>🌊 Tracking Sampah Plastik</h1>
          <p className="description">
            Masukkan data lokasi dan periode waktu untuk melacak pergerakan sampah plastik
          </p>

          {!results ? (
            <div className="tracking-form">
              <div className="form-group">
                <label>Lokasi Penelitian</label>
                <select
                  name="location"
                  value={formData.location}
                  onChange={handleLocationChange}
                >
                  <option value="">Pilih Lokasi</option>
                  <option value="Takalar">Takalar, Sulawesi Selatan</option>
                  <option value="Mamuju">Mamuju, Sulawesi Barat</option>
                </select>
              </div>

              <div className="input-row">
                <div className="form-group">
                  <label>Latitude</label>
                  <input
                    type="number"
                    name="latitude"
                    step="0.0001"
                    value={formData.latitude}
                    onChange={handleInputChange}
                    placeholder="Contoh: -5.3971"
                  />
                </div>
                <div className="form-group">
                  <label>Longitude</label>
                  <input
                    type="number"
                    name="longitude"
                    step="0.0001"
                    value={formData.longitude}
                    onChange={handleInputChange}
                    placeholder="Contoh: 119.4419"
                  />
                </div>
              </div>

              <div className="input-row">
                <div className="form-group">
                  <label>Tanggal Mulai Tracking</label>
                  <input
                    type="date"
                    name="start_date"
                    value={formData.start_date}
                    onChange={handleInputChange}
                  />
                </div>
                <div className="form-group">
                  <label>Durasi Tracking (Hari)</label>
                  <input
                    type="number"
                    name="days"
                    min="1"
                    max="30"
                    value={formData.days}
                    onChange={handleInputChange}
                    placeholder="Contoh: 7"
                  />
                </div>
              </div>

              {error && (
                <div className="error-message">
                  ⚠️ {error}
                </div>
              )}

              <button className="btn btn-primary" onClick={startTracking}>
                🚀 Mulai Tracking
              </button>
            </div>
          ) : (
            <div className="tracking-results">
              <h2>📊 Hasil Tracking</h2>

              <div className="info-grid">
                <div className="info-card">
                  <h3>Lokasi</h3>
                  <p>{results.location}</p>
                </div>
                <div className="info-card">
                  <h3>Koordinat</h3>
                  <p>{results.coordinates.latitude.toFixed(4)}, {results.coordinates.longitude.toFixed(4)}</p>
                </div>
                <div className="info-card">
                  <h3>Tanggal Mulai</h3>
                  <p>{formatDate(results.start_date)}</p>
                </div>
                <div className="info-card">
                  <h3>Durasi</h3>
                  <p>{results.days} Hari</p>
                </div>
              </div>

              <div className="map-container">
                <h3>Peta Tracking Sampah</h3>
                <div className="image-container">
                  <img
                    src={`/tracking/${results.location.toLowerCase()}_tracking.png`}
                    alt="Tracking Map"
                    onError={(e) => {
                      e.target.src = 'https://via.placeholder.com/800x600/667eea/ffffff?text=Tracking+Map+' + results.location
                      e.target.alt = 'Placeholder - Tambahkan gambar tracking Anda'
                    }}
                  />
                </div>
                <p className="map-note">
                  💡 Tambahkan file <code>{results.location.toLowerCase()}_tracking.png</code> ke folder <code>frontend/public/tracking/</code>
                </p>
              </div>

              <div className="stats-container">
                <h3>📈 Statistik Tracking</h3>
                <div className="stats-grid">
                  <div className="stats-item">
                    <span className="stats-label">Total Jarak Tempuh</span>
                    <span className="stats-value">{results.statistics.total_distance} km</span>
                  </div>
                  <div className="stats-item">
                    <span className="stats-label">Kecepatan Rata-rata</span>
                    <span className="stats-value">{results.statistics.avg_speed} m/s</span>
                  </div>
                  <div className="stats-item">
                    <span className="stats-label">Arah Dominan</span>
                    <span className="stats-value">{results.statistics.dominant_direction}</span>
                  </div>
                  <div className="stats-item">
                    <span className="stats-label">Tanggal Berakhir</span>
                    <span className="stats-value">{formatDate(results.end_date)}</span>
                  </div>
                  <div className="stats-item">
                    <span className="stats-label">Status Tracking</span>
                    <span className="stats-value">{results.statistics.status}</span>
                  </div>
                </div>
              </div>

              <div className="button-group">
                <button className="btn btn-secondary" onClick={resetTracking}>
                  🔄 Tracking Baru
                </button>
                <button className="btn btn-secondary" onClick={onBack}>
                  🏠 Kembali ke Beranda
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Loading Overlay */}
      {loading && (
        <div className="loading-overlay">
          <div className="loading-content">
            <div className="spinner"></div>
            <h2>Memproses Tracking...</h2>
            <p>Menganalisis data oceanografi dan pola arus</p>
            <div className="progress-container">
              <div className="progress-bar" style={{ width: `${progress}%` }}></div>
            </div>
            <p>{progress}%</p>
          </div>
        </div>
      )}
    </div>
  )
}

export default TrackingPage
