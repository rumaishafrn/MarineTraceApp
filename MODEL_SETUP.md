# INSTRUKSI UNTUK MODEL YOLO

## Cara Menggunakan Model YOLO Anda

### 1. Copy Model ke Folder

```bash
# Copy file .pt Anda ke folder models/
cp /path/to/your/yolo-model.pt backend/models/best.pt
```

### 2. Update Nama Model (Jika Berbeda)

Jika nama model Anda bukan `best.pt`, edit file `backend/app.py` pada line 20:

```python
# Ganti 'best.pt' dengan nama model Anda
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'nama-model-anda.pt')
```

### 3. Cek Class Names Model Anda

Untuk melihat class names yang ada di model YOLO Anda:

```python
from ultralytics import YOLO

model = YOLO('backend/models/best.pt')
print("Class names:", model.names)
# Output contoh: {0: 'plastic_bag', 1: 'bottle', 2: 'wrapper'}
```

### 4. Sesuaikan Mapping Class Names

Edit file `backend/app.py` sekitar line 180-186 untuk menyesuaikan dengan class names model Anda:

**Contoh 1 - Jika class names adalah: plastic_bag, bottle, wrapper**
```python
plastic_bag = detection_counts.get('plastic_bag', 0)
bottle = detection_counts.get('bottle', 0)
wrapper = detection_counts.get('wrapper', 0)
```

**Contoh 2 - Jika class names adalah: kantong, botol, kemasan**
```python
plastic_bag = detection_counts.get('kantong', 0)
bottle = detection_counts.get('botol', 0)
wrapper = detection_counts.get('kemasan', 0)
```

**Contoh 3 - Jika class names adalah angka: 0, 1, 2**
```python
plastic_bag = detection_counts.get(0, 0)
bottle = detection_counts.get(1, 0)
wrapper = detection_counts.get(2, 0)
```

**Contoh 4 - Jika ada banyak class, gunakan mapping**
```python
# Map multiple classes to categories
plastic_bag = sum(detection_counts.get(name, 0) for name in ['plastic_bag', 'bag', 'plastik', 'kantong'])
bottle = sum(detection_counts.get(name, 0) for name in ['bottle', 'botol', 'pet_bottle'])
wrapper = sum(detection_counts.get(name, 0) for name in ['wrapper', 'kemasan', 'packaging', 'sachet'])
```

### 5. Test Model

Setelah setup, test dengan script ini:

```python
# test_model.py
from ultralytics import YOLO
import cv2

# Load model
model = YOLO('backend/models/best.pt')

# Print class names
print("Available classes:", model.names)

# Test dengan gambar
img_path = 'path/to/test/image.jpg'
results = model(img_path)

# Print detections
for result in results:
    boxes = result.boxes
    print(f"Found {len(boxes)} objects")
    for box in boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        class_name = model.names[cls_id]
        print(f"  - {class_name}: {conf:.2%}")

# Save result image
result_img = results[0].plot()
cv2.imwrite('test_result.jpg', result_img)
print("Result saved to test_result.jpg")
```

Run dengan:
```bash
cd backend
python test_model.py
```

## Troubleshooting

### Model tidak load
- Pastikan file `.pt` ada di `backend/models/`
- Install ultralytics: `pip install ultralytics --break-system-packages`
- Cek PyTorch compatible: `pip install torch torchvision`

### Error saat inference
- Pastikan gambar format JPEG/PNG
- Cek size gambar tidak terlalu besar
- Update ultralytics ke versi terbaru

### Class detection tidak sesuai
- Print `model.names` untuk lihat class names
- Update mapping di `app.py` sesuai class names Anda
- Pastikan threshold confidence sudah sesuai

## Informasi Model

Model YOLO yang digunakan:
- Path: `backend/models/best.pt`
- Format: PyTorch (.pt)
- Framework: Ultralytics YOLOv8

Pastikan model Anda:
- ✅ Sudah trained untuk deteksi sampah plastik
- ✅ Compatible dengan Ultralytics YOLO
- ✅ File size reasonable (<500MB untuk deployment)
- ✅ Class names terdokumentasi

## Contoh Output

Setelah deteksi berhasil, aplikasi akan menampilkan:
1. Gambar dengan bounding boxes
2. Jumlah setiap jenis sampah
3. Akurasi/confidence
4. Akumulasi data per lokasi

Format response API:
```json
{
  "success": true,
  "data": {
    "location": "Takalar",
    "total_detected": 12,
    "confidence": 94.2,
    "breakdown": {
      "plastic_bag": 5,
      "bottle": 4,
      "wrapper": 3
    },
    "all_detections": {
      "plastic_bag": 5,
      "bottle": 4,
      "wrapper": 3
    },
    "result_image": "data:image/jpeg;base64,...",
    "accumulation": {
      "total": 156,
      "plastic_bag": 67,
      "bottle": 48,
      "wrapper": 41,
      "uploads": 13
    }
  }
}
```
