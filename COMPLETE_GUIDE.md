# 🌊 MarineTrace - Complete Application Guide

## 📋 Ringkasan Aplikasi

Aplikasi full-stack profesional untuk penelitian **"Addressing Plastic Pollution from Seaweed Farming in South Sulawesi and West Sulawesi"**

### Teknologi Stack
- **Frontend**: React 18 + Vite + Axios
- **Backend**: Flask (Python) + Ultralytics YOLO
- **Database**: SQLite (upgradeable to PostgreSQL)
- **ML Model**: YOLOv8 untuk object detection

### Fitur Utama
1. ✅ **Tracking Sampah** - Backtracking alur sampah dari 2 lokasi (Takalar & Mamuju)
2. ✅ **Deteksi Sampah** - YOLO object detection dengan segmentasi
3. ✅ **Database Akumulasi** - Menyimpan dan mengakumulasi data deteksi
4. ✅ **Responsive Design** - Berfungsi di desktop, tablet, dan mobile
5. ✅ **Real-time Processing** - Live detection dan tracking

---

## 📁 Struktur Aplikasi

```
marine-trace-app/
│
├── 📄 README.md                    # Dokumentasi utama
├── 📄 QUICKSTART.md                # Panduan cepat memulai
├── 📄 MODEL_SETUP.md               # Setup model YOLO
├── 📄 DEPLOYMENT.md                # Panduan deployment
├── 🔧 setup.sh                     # Script instalasi otomatis
├── 🧪 test_backend.py              # Test suite backend
├── 🏗️ create_dummy_model.py        # Buat dummy model untuk testing
├── 📝 .gitignore                   # Git ignore file
│
├── backend/                        # 🔙 Backend (Flask + YOLO)
│   ├── app.py                     # Main Flask application
│   ├── requirements.txt           # Python dependencies
│   ├── README.md                  # Backend documentation
│   ├── models/                    # 📦 YOLO model files (.pt)
│   │   └── .gitkeep
│   ├── static/                    # 🖼️ Tracking map images
│   │   └── .gitkeep
│   ├── uploads/                   # 📤 User uploaded images
│   │   └── .gitkeep
│   ├── results/                   # 📊 Detection result images
│   │   └── .gitkeep
│   └── database.db                # 💾 SQLite database (auto-created)
│
└── frontend/                       # 🎨 Frontend (React)
    ├── package.json               # NPM dependencies
    ├── vite.config.js             # Vite configuration
    ├── index.html                 # HTML entry point
    ├── public/                    # Static assets
    │   ├── tracking/              # Tracking map images
    │   └── examples/              # Example images
    ├── src/
    │   ├── main.jsx               # React entry point
    │   ├── App.jsx                # Main App component
    │   ├── App.css                # Global styles
    │   ├── index.css              # Base styles
    │   └── components/            # React components
    │       ├── MainPage.jsx       # Landing page
    │       ├── MainPage.css
    │       ├── TrackingPage.jsx   # Tracking feature
    │       ├── TrackingPage.css
    │       ├── DetectionPage.jsx  # Detection feature
    │       └── DetectionPage.css
```

---

## 🚀 Cara Menggunakan Aplikasi Ini

### Step 1: Persiapan

1. **Clone atau download** folder `marine-trace-app`
2. **Pastikan terinstall:**
   - Python 3.8+ (`python --version`)
   - Node.js 16+ (`node --version`)
   - pip (`pip --version`)
   - npm (`npm --version`)

### Step 2: Install Dependencies

**Option A - Otomatis:**
```bash
cd marine-trace-app
chmod +x setup.sh
./setup.sh
```

**Option B - Manual:**
```bash
# Backend
cd backend
pip install -r requirements.txt --break-system-packages

# Frontend
cd ../frontend
npm install
```

### Step 3: Setup Model YOLO

**PENTING! Ini langkah paling krusial:**

1. **Copy model YOLO .pt Anda** ke folder `backend/models/`:
   ```bash
   cp /path/to/your-model.pt backend/models/best.pt
   ```

2. **Jika nama model berbeda**, edit `backend/app.py` line 20:
   ```python
   MODEL_PATH = os.path.join(BASE_DIR, 'models', 'your-model-name.pt')
   ```

3. **Cek class names model Anda:**
   ```bash
   cd backend
   python -c "from ultralytics import YOLO; m=YOLO('models/best.pt'); print(m.names)"
   ```

4. **Update class mapping** di `backend/app.py` line 180-186 sesuai output di atas
   - Detail lengkap ada di `MODEL_SETUP.md`

### Step 4: (Optional) Add Tracking Images

```bash
# Copy gambar tracking Anda
cp takalar_tracking.png backend/static/
cp mamuju_tracking.png backend/static/
```

Format: PNG, ukuran bebas (recommended 800x600 atau lebih)

### Step 5: Test Backend

```bash
python test_backend.py
```

**Pastikan semua test PASS ✅** sebelum lanjut!

### Step 6: Run Application

**Terminal 1 - Backend:**
```bash
cd backend
python app.py
```
✅ Backend running di: `http://localhost:5000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
✅ Frontend running di: `http://localhost:5173`

### Step 7: Buka Browser

```
http://localhost:5173
```

---

## 🎯 Cara Menggunakan Fitur

### 1. Tracking Sampah

1. Klik "**Tracking Sampah**" di halaman utama
2. Pilih **Lokasi**: Takalar atau Mamuju
3. Input **Latitude & Longitude** (auto-filled berdasarkan lokasi)
4. Pilih **Tanggal Mulai** tracking
5. Input **Durasi** tracking (dalam hari)
6. Klik "**Mulai Tracking**"
7. Lihat hasil: peta tracking + statistik

### 2. Deteksi Sampah

1. Klik "**Deteksi Sampah**" di halaman utama
2. Pilih **Lokasi**: Takalar atau Mamuju
3. **Upload gambar** sampah (klik area upload)
4. Klik "**Mulai Deteksi**"
5. Lihat hasil:
   - Gambar original vs hasil deteksi YOLO
   - Jumlah setiap jenis sampah
   - Statistik akumulasi lokasi

---

## 🔧 Kustomisasi

### Mengubah Class Names

Edit `backend/app.py` sekitar line 180-186:

```python
# Default mapping
plastic_bag = sum(detection_counts.get(name, 0) 
                  for name in ['plastic_bag', 'bag', 'plastik'])
bottle = sum(detection_counts.get(name, 0) 
             for name in ['bottle', 'botol'])
wrapper = sum(detection_counts.get(name, 0) 
              for name in ['wrapper', 'kemasan', 'packaging'])
```

Sesuaikan dengan class names dari model YOLO Anda!

### Mengubah UI/Styling

- **Warna**: Edit `frontend/src/App.css` dan component CSS files
- **Text**: Edit component `.jsx` files di `frontend/src/components/`
- **Logo**: Ganti emoji di `MainPage.jsx` line 8

### Menambah Lokasi

1. **Backend**: Edit `backend/app.py` line 65-66, tambah lokasi baru
2. **Frontend**: Edit semua `<select>` di `TrackingPage.jsx` dan `DetectionPage.jsx`
3. **Database**: Hapus `backend/database.db` untuk reset dengan lokasi baru

---

## 📊 API Endpoints

### Health Check
```bash
GET http://localhost:5000/api/health
```

### Track Waste
```bash
POST http://localhost:5000/api/track
Content-Type: application/json

{
  "location": "Takalar",
  "latitude": -5.3971,
  "longitude": 119.4419,
  "start_date": "2024-02-01",
  "days": 7
}
```

### Detect Waste
```bash
POST http://localhost:5000/api/detect
Content-Type: application/json

{
  "location": "Takalar",
  "image": "data:image/jpeg;base64,/9j/4AAQ..."
}
```

### Get Statistics
```bash
GET http://localhost:5000/api/stats/Takalar
GET http://localhost:5000/api/stats/Mamuju
```

---

## 🐛 Troubleshooting

### Model tidak load?
- ✅ Cek file ada di `backend/models/`
- ✅ Cek nama file sesuai di `app.py`
- ✅ Install ultralytics: `pip install ultralytics`

### Frontend error CORS?
- ✅ Pastikan backend running
- ✅ Cek Flask-CORS installed
- ✅ Restart kedua server

### Database error?
- ✅ Hapus `backend/database.db`
- ✅ Restart backend (akan auto-create)

### Port sudah digunakan?
- ✅ Ubah port di `backend/app.py` (line terakhir)
- ✅ Ubah port di `frontend/vite.config.js`

---

## 🚀 Deployment ke Production

Lihat `DEPLOYMENT.md` untuk panduan lengkap deploy ke:
- ✅ Vercel + Railway (Recommended, Free)
- ✅ Docker + VPS
- ✅ Heroku
- ✅ Google Cloud / AWS

---

## 📝 To-Do untuk Production

- [ ] Add authentication (login system)
- [ ] Upgrade database ke PostgreSQL
- [ ] Add image compression
- [ ] Implement caching
- [ ] Add rate limiting
- [ ] Setup monitoring (Sentry)
- [ ] Add export data (CSV, PDF)
- [ ] Multi-language support
- [ ] Admin dashboard

---

## 📞 Support & Kontribusi

- **GitHub**: [Link repository Anda]
- **Email**: [Email tim penelitian]
- **Issues**: Report bugs via GitHub Issues
- **Documentation**: Baca semua `.md` files

---

## 📜 License

Untuk keperluan penelitian akademik - Universitas Hasanuddin

---

## 🙏 Credits

Developed for research project:
**"Addressing Plastic Pollution from Seaweed Farming in South Sulawesi and West Sulawesi"**

Technology Stack:
- React & Vite
- Flask
- Ultralytics YOLO
- SQLite

---

**Happy Researching! 🌊🔬🇮🇩**
