# Backend - MarineTrace API

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt --break-system-packages
```

Atau install satu per satu:
```bash
pip install flask flask-cors ultralytics opencv-python pillow numpy pandas --break-system-packages
```

### 2. Add Your YOLO Model

**PENTING:** Copy model YOLO `.pt` Anda ke folder `models/`

```bash
cp /path/to/your/model.pt models/best.pt
```

Atau jika model Anda punya nama lain, update di `app.py` line 20:
```python
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'nama-model-anda.pt')
```

### 3. Add Tracking Map Images

Copy gambar tracking Anda ke folder `static/`:
- `static/takalar_tracking.png` - Tracking map untuk Takalar
- `static/mamuju_tracking.png` - Tracking map untuk Mamuju

### 4. Run Server

```bash
python app.py
```

Server akan berjalan di `http://localhost:5000`

## API Endpoints

### Health Check
```bash
GET /api/health
```

Response:
```json
{
  "status": "ok",
  "yolo_available": true,
  "model_path": "/path/to/model.pt",
  "model_exists": true
}
```

### Track Waste
```bash
POST /api/track
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
POST /api/detect
Content-Type: application/json

{
  "location": "Takalar",
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEA..."
}
```

### Get Statistics
```bash
GET /api/stats/Takalar
GET /api/stats/Mamuju
```

## Database Schema

### Table: detections
- id (INTEGER PRIMARY KEY)
- location (TEXT)
- image_path (TEXT)
- result_path (TEXT)
- plastic_bag (INTEGER)
- bottle (INTEGER)
- wrapper (INTEGER)
- total_items (INTEGER)
- confidence (REAL)
- created_at (TIMESTAMP)

### Table: accumulations
- id (INTEGER PRIMARY KEY)
- location (TEXT UNIQUE)
- total_items (INTEGER)
- plastic_bag (INTEGER)
- bottle (INTEGER)
- wrapper (INTEGER)
- total_uploads (INTEGER)
- last_updated (TIMESTAMP)

## Folder Structure

```
backend/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── models/            # YOLO model files (.pt)
│   └── best.pt        # Your YOLO model
├── static/            # Static files
│   ├── takalar_tracking.png
│   └── mamuju_tracking.png
├── uploads/           # Uploaded images (auto-created)
├── results/           # Detection results (auto-created)
└── database.db        # SQLite database (auto-created)
```

## Customizing YOLO Class Names

Jika model YOLO Anda memiliki class names yang berbeda, update mapping di `app.py` sekitar line 180-186:

```python
# Map class names to categories
plastic_bag = sum(detection_counts.get(name, 0) for name in ['plastic_bag', 'bag', 'plastik'])
bottle = sum(detection_counts.get(name, 0) for name in ['bottle', 'botol'])
wrapper = sum(detection_counts.get(name, 0) for name in ['wrapper', 'kemasan', 'packaging'])
```

Sesuaikan dengan class names dari model Anda. Untuk cek class names:
```python
print(yolo_model.names)
```

## Troubleshooting

### Model tidak load
- Pastikan file `.pt` ada di folder `models/`
- Cek nama file sesuai dengan `MODEL_PATH` di `app.py`
- Pastikan ultralytics terinstall: `pip install ultralytics`

### Error saat deteksi
- Cek format image (harus JPEG/PNG)
- Pastikan image tidak terlalu besar (max 10MB recommended)

### Database error
- Delete `database.db` dan restart server untuk reset database

## Testing

Test API dengan curl:

```bash
# Health check
curl http://localhost:5000/api/health

# Track waste
curl -X POST http://localhost:5000/api/track \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Takalar",
    "latitude": -5.3971,
    "longitude": 119.4419,
    "start_date": "2024-02-01",
    "days": 7
  }'

# Get stats
curl http://localhost:5000/api/stats/Takalar
```
