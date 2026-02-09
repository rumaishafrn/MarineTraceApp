# Quick Start Guide - MarineTrace

## 🚀 Cara Cepat Memulai (5 Menit)

### Langkah 1: Clone atau Download Repository
```bash
git clone https://github.com/yourusername/marine-trace.git
cd marine-trace-app
```

### Langkah 2: Install Dependencies

**Option A - Automatic (Recommended)**
```bash
chmod +x setup.sh
./setup.sh
```

**Option B - Manual**
```bash
# Backend
cd backend
pip install -r requirements.txt --break-system-packages
cd ..

# Frontend
cd frontend
npm install
cd ..
```

### Langkah 3: Add Your YOLO Model
```bash
# Copy model Anda ke folder models
cp /path/to/your/yolo-model.pt backend/models/best.pt
```

**PENTING:** Jika nama model berbeda dari `best.pt`, edit `backend/app.py` line 20

### Langkah 4: (Optional) Add Tracking Images
```bash
# Copy gambar tracking Anda
cp takalar_tracking.png backend/static/
cp mamuju_tracking.png backend/static/
```

### Langkah 5: Test Backend
```bash
python test_backend.py
```

Jika semua test PASS ✅, lanjut ke langkah berikutnya!

### Langkah 6: Run Application

**Terminal 1 - Backend:**
```bash
cd backend
python app.py
```
Server akan running di `http://localhost:5000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
App akan running di `http://localhost:5173`

### Langkah 7: Open Browser
```
http://localhost:5173
```

---

## 🎯 Checklist Setup

- [ ] Dependencies installed (backend & frontend)
- [ ] YOLO model (.pt) copied to `backend/models/`
- [ ] Model path correct in `backend/app.py`
- [ ] Test backend passed (`python test_backend.py`)
- [ ] Backend running (`http://localhost:5000`)
- [ ] Frontend running (`http://localhost:5173`)
- [ ] (Optional) Tracking images added to `backend/static/`

---

## ✅ Verification

### Test Backend API
```bash
# Health check
curl http://localhost:5000/api/health

# Expected response:
{
  "status": "ok",
  "yolo_available": true,
  "model_exists": true
}
```

### Test Frontend
1. Open `http://localhost:5173`
2. Klik "Deteksi Sampah"
3. Pilih lokasi: Takalar
4. Upload gambar sampah
5. Klik "Mulai Deteksi"
6. Lihat hasil deteksi!

---

## 🐛 Troubleshooting

### Backend tidak jalan?
```bash
# Check Python
python --version  # Should be 3.8+

# Check dependencies
pip list | grep flask
pip list | grep ultralytics

# Reinstall if needed
pip install flask ultralytics --break-system-packages
```

### Frontend tidak jalan?
```bash
# Check Node.js
node --version  # Should be 16+
npm --version

# Clear cache and reinstall
cd frontend
rm -rf node_modules
npm install
```

### Model tidak load?
```bash
# Check model file
ls -lh backend/models/

# Test model manually
cd backend
python -c "from ultralytics import YOLO; m = YOLO('models/best.pt'); print(m.names)"
```

### Port already in use?
```bash
# Backend (change port in app.py)
app.run(port=5001)  # Instead of 5000

# Frontend (change port in package.json)
"dev": "vite --port 3000"  # Instead of 5173
```

---

## 📚 Next Steps

1. **Customize Model Mapping**
   - Edit `backend/app.py` line 180-186
   - Match dengan class names model Anda
   - Check `MODEL_SETUP.md` untuk detail

2. **Add Tracking Images**
   - Format: PNG
   - Names: `takalar_tracking.png`, `mamuju_tracking.png`
   - Location: `backend/static/`

3. **Deploy Online**
   - Check `DEPLOYMENT.md` untuk options
   - Recommended: Vercel (frontend) + Railway (backend)

4. **Customize UI**
   - Edit components di `frontend/src/components/`
   - Modify colors/styles di CSS files

---

## 💡 Tips

- **Development:** Use `npm run dev` untuk hot reload
- **Production:** Run `npm run build` untuk optimize
- **Database:** Reset dengan hapus `backend/database.db`
- **Logs:** Check terminal untuk error messages

---

## 📞 Support

- GitHub Issues: Report bugs atau feature requests
- Documentation: Baca `README.md` dan `MODEL_SETUP.md`
- Email: [your-email@university.edu]

---

**Happy Coding! 🌊🔬**
