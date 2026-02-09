import React, { useState, useRef } from 'react'
import axios from 'axios'
import './DetectionPage.css'

function DetectionPage({ onBack }) {
  const [location, setLocation] = useState('')
  const [imageFile, setImageFile] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)
  const fileInputRef = useRef(null)

  const handleImageUpload = (e) => {
    const file = e.target.files[0]
    if (file) {
      setImageFile(file)
      
      // Create preview
      const reader = new FileReader()
      reader.onload = (e) => {
        setImagePreview(e.target.result)
      }
      reader.readAsDataURL(file)
    }
  }

  const startDetection = async () => {
    if (!location || !imageFile) {
      alert('Mohon pilih lokasi dan upload gambar!')
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
    }, 300)

    try {
      // Convert image to base64
      const reader = new FileReader()
      reader.onload = async (e) => {
        const base64Image = e.target.result

        try {
          const response = await axios.post('/api/detect', {
            location: location,
            image: base64Image
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
          setError(err.response?.data?.error || err.response?.data?.message || 'Terjadi kesalahan saat deteksi')
          console.error('Detection error:', err)
        }
      }

      reader.readAsDataURL(imageFile)

    } catch (err) {
      clearInterval(progressInterval)
      setLoading(false)
      setError('Gagal membaca file gambar')
      console.error('File read error:', err)
    }
  }

  const resetDetection = () => {
    setResults(null)
    setLocation('')
    setImageFile(null)
    setImagePreview(null)
    setProgress(0)
    setError(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="detection-page slide-in">
      <div className="container">
        <button className="btn btn-secondary back-btn" onClick={onBack}>
          ← Kembali ke Beranda
        </button>

        <div className="content-box">
          <h1>🔍 Deteksi Sampah Plastik</h1>
          <p className="description">
            Upload foto sampah untuk mendeteksi dan mengidentifikasi jenis sampah menggunakan AI
          </p>

          {!results ? (
            <div className="detection-form">
              <div className="form-group">
                <label>Lokasi Sampah</label>
                <select
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                >
                  <option value="">Pilih Lokasi</option>
                  <option value="Takalar">Takalar, Sulawesi Selatan</option>
                  <option value="Mamuju">Mamuju, Sulawesi Barat</option>
                </select>
              </div>

              <div className="form-group">
                <label>Upload Gambar Sampah</label>
                <div className="upload-area" onClick={() => fileInputRef.current?.click()}>
                  {imagePreview ? (
                    <img src={imagePreview} alt="Preview" className="preview-image" />
                  ) : (
                    <div className="upload-placeholder">
                      <div className="upload-icon">📷</div>
                      <p>Klik untuk upload gambar</p>
                      <p className="upload-hint">Format: JPG, PNG (Max 10MB)</p>
                    </div>
                  )}
                </div>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  style={{ display: 'none' }}
                />
              </div>

              {error && (
                <div className="error-message">
                  ⚠️ {error}
                  {error.includes('model not loaded') && (
                    <div className="error-details">
                      <p>Pastikan model YOLO Anda sudah tersedia di folder <code>backend/models/</code></p>
                      <p>Update nama model di <code>backend/app.py</code> jika berbeda dari <code>best.pt</code></p>
                    </div>
                  )}
                </div>
              )}

              <button
                className="btn btn-primary"
                onClick={startDetection}
                disabled={!location || !imageFile}
              >
                🚀 Mulai Deteksi
              </button>
            </div>
          ) : (
            <div className="detection-results">
              <h2>✅ Hasil Deteksi</h2>

              <div className="info-grid">
                <div className="info-card">
                  <h3>Lokasi</h3>
                  <p>{results.location}</p>
                </div>
                <div className="info-card">
                  <h3>Total Terdeteksi</h3>
                  <p>{results.total_detected} Item</p>
                </div>
                <div className="info-card">
                  <h3>Sampah Dominan</h3>
                  <p>{results.dominant.name}</p>
                </div>
                <div className="info-card">
                  <h3>Akurasi Model</h3>
                  <p>{results.confidence}%</p>
                </div>
              </div>

              <div className="result-images">
                <div className="image-comparison">
                  <div className="comparison-item">
                    <h4>Gambar Original</h4>
                    <div className="image-container">
                      <img src={imagePreview} alt="Original" />
                    </div>
                  </div>
                  <div className="comparison-item">
                    <h4>Hasil Deteksi YOLO</h4>
                    <div className="image-container">
                      <img src={results.result_image} alt="Detection Result" />
                    </div>
                  </div>
                </div>
              </div>

              <div className="stats-container">
                <h3>📊 Detail Deteksi</h3>
                <div className="stats-grid">
                  <div className="stats-item">
                    <span className="stats-label">🛍️ Kantong Plastik</span>
                    <span className="stats-value">{results.breakdown.plastic_bag} item</span>
                  </div>
                  <div className="stats-item">
                    <span className="stats-label">🍼 Botol Plastik</span>
                    <span className="stats-value">{results.breakdown.bottle} item</span>
                  </div>
                  <div className="stats-item">
                    <span className="stats-label">📦 Kemasan/Wrapper</span>
                    <span className="stats-value">{results.breakdown.wrapper} item</span>
                  </div>
                  <div className="stats-item">
                    <span className="stats-label">📊 Total Sampah</span>
                    <span className="stats-value">{results.total_detected} item</span>
                  </div>
                  <div className="stats-item">
                    <span className="stats-label">🎯 Sampah Dominan</span>
                    <span className="stats-value">
                      {results.dominant.name} ({results.dominant.percentage}%)
                    </span>
                  </div>
                </div>
              </div>

              {results.all_detections && Object.keys(results.all_detections).length > 0 && (
                <div className="stats-container">
                  <h3>🔬 Semua Class Terdeteksi</h3>
                  <div className="stats-grid">
                    {Object.entries(results.all_detections).map(([className, count]) => (
                      <div className="stats-item" key={className}>
                        <span className="stats-label">{className}</span>
                        <span className="stats-value">{count} item</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {results.accumulation && (
                <div className="stats-container highlight">
                  <h3>📈 Akumulasi Data {results.location}</h3>
                  <div className="stats-grid">
                    <div className="stats-item">
                      <span className="stats-label">Total Akumulasi Sampah</span>
                      <span className="stats-value">{results.accumulation.total} item</span>
                    </div>
                    <div className="stats-item">
                      <span className="stats-label">Kantong Plastik</span>
                      <span className="stats-value">{results.accumulation.plastic_bag} item</span>
                    </div>
                    <div className="stats-item">
                      <span className="stats-label">Botol Plastik</span>
                      <span className="stats-value">{results.accumulation.bottle} item</span>
                    </div>
                    <div className="stats-item">
                      <span className="stats-label">Kemasan/Wrapper</span>
                      <span className="stats-value">{results.accumulation.wrapper} item</span>
                    </div>
                    <div className="stats-item">
                      <span className="stats-label">📤 Total Upload</span>
                      <span className="stats-value">{results.accumulation.uploads} kali</span>
                    </div>
                  </div>
                  <p className="accumulation-note">
                    💡 Data akumulasi berdasarkan semua deteksi yang pernah dilakukan untuk lokasi {results.location}
                  </p>
                </div>
              )}

              <div className="button-group">
                <button className="btn btn-secondary" onClick={resetDetection}>
                  🔄 Deteksi Baru
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
            <h2>Mendeteksi Sampah...</h2>
            <p>Model YOLO sedang menganalisis gambar</p>
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

export default DetectionPage
