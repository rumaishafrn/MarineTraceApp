# 🎯 YOLO Segmentation Model - Setup Guide

## ✅ Konfirmasi: Anda Menggunakan YOLO Segmentation Model

YOLO Segmentation berbeda dengan YOLO Detection:
- **Detection**: Hanya bounding boxes (kotak)
- **Segmentation**: Bounding boxes + mask/outline objek (lebih detail)

Aplikasi ini **sudah di-update** untuk mendukung kedua jenis model!

---

## 📋 Yang Perlu Anda Ketahui

### 1. Class Names Model Segmentation

Jalankan perintah ini untuk cek class names model Anda:

```python
from ultralytics import YOLO

model = YOLO('backend/models/best.pt')
print("Class names:", model.names)
print("Model task:", model.task)  # Harusnya 'segment'
```

**Output contoh:**
```python
Class names: {0: 'plastic_bag', 1: 'bottle', 2: 'wrapper'}
Model task: segment
```

### 2. Update Class Mapping

Edit file `backend/app.py` pada **line 188-194** sesuai class names Anda:

**Contoh - Jika class names adalah: plastic_bag, bottle, wrapper**
```python
# Direct mapping (jika nama class persis sama)
plastic_bag = detection_counts.get('plastic_bag', 0)
bottle = detection_counts.get('bottle', 0)
wrapper = detection_counts.get('wrapper', 0)
```

**Contoh - Jika class names berbeda**
```python
# Sesuaikan dengan class names Anda
# Misal class names: plastik, botol_plastik, kemasan_plastik
plastic_bag = detection_counts.get('plastik', 0)
bottle = detection_counts.get('botol_plastik', 0)
wrapper = detection_counts.get('kemasan_plastik', 0)
```

**Contoh - Jika menggunakan angka/index**
```python
# Jika model Anda pakai index: {0: 'class1', 1: 'class2'}
plastic_bag = detection_counts.get(model.names[0], 0)
bottle = detection_counts.get(model.names[1], 0)
wrapper = detection_counts.get(model.names[2], 0)
```

**Contoh - Multiple classes untuk satu kategori**
```python
# Jika ada banyak jenis plastik bag, botol, dll
plastic_bag = sum(detection_counts.get(name, 0) 
                  for name in ['plastic_bag', 'bag', 'kantong', 'plastik_bag'])
bottle = sum(detection_counts.get(name, 0) 
             for name in ['bottle', 'botol', 'pet_bottle', 'botol_air'])
wrapper = sum(detection_counts.get(name, 0) 
              for name in ['wrapper', 'kemasan', 'sachet', 'packaging'])
```

---

## 🧪 Test Model Segmentation

### Step 1: Test dengan Script

```bash
cd backend
python test_backend.py
```

**Expected Output:**
```
============================================================
Testing Model Inference...
============================================================
Creating test image...
Running inference...
✅ Inference successful!
   Model Type: SEGMENTATION ✓
   Detected X objects with segmentation masks
   
✅ PASS - Model Inference
```

### Step 2: Test dengan Gambar Asli

Buat file `test_segmentation.py` di folder `backend`:

```python
from ultralytics import YOLO
import cv2

# Load model
model = YOLO('models/best.pt')

# Print info
print("Model type:", model.task)
print("Class names:", model.names)
print()

# Test dengan gambar
image_path = 'path/to/your/test/image.jpg'  # Ganti dengan path gambar Anda
results = model(image_path)

# Print detections
result = results[0]
print(f"Found {len(result.boxes)} objects")

for i, box in enumerate(result.boxes):
    cls_id = int(box.cls[0])
    conf = float(box.conf[0])
    class_name = model.names[cls_id]
    print(f"{i+1}. {class_name}: {conf:.2%}")

# Check if masks exist
if hasattr(result, 'masks') and result.masks is not None:
    print(f"\nSegmentation masks: {len(result.masks)} masks generated ✓")
else:
    print("\nNo masks (this is a detection model)")

# Save result with masks
result_img = result.plot()  # Includes masks if segmentation model
cv2.imwrite('test_result.jpg', cv2.cvtColor(result_img, cv2.COLOR_RGB2BGR))
print("\nResult saved to: test_result.jpg")
print("Check the image - you should see colored masks over objects!")
```

Run test:
```bash
python test_segmentation.py
```

---

## 🎨 Hasil Segmentation vs Detection

### Detection Model Output:
```
┌─────────────────┐
│  ┌──────────┐   │
│  │ Bottle   │   │  ← Kotak saja
│  └──────────┘   │
│    ┌─────┐      │
│    │ Bag │      │  ← Kotak saja
│    └─────┘      │
└─────────────────┘
```

### Segmentation Model Output:
```
┌─────────────────┐
│  ┌──────────┐   │
│  │▓▓▓▓▓▓▓▓▓▓│   │  ← Kotak + mask warna
│  │▓ Bottle ▓│   │
│  └──────────┘   │
│    ┌─────┐      │
│    │▒▒▒▒▒│      │  ← Kotak + mask warna
│    │▒Bag▒│      │
│    └─────┘      │
└─────────────────┘
```

**Segmentation lebih akurat** karena:
- Outline tepat mengikuti bentuk objek
- Bisa deteksi objek yang overlap
- Lebih presisi dalam counting

---

## 🔧 Troubleshooting Segmentation

### Error: "Expected model task to be 'segment'"
**Solusi:**
- Model Anda bukan segmentation model
- Download atau train ulang dengan task='segment'

### Error: "Masks is None"
**Solusi:**
- Model loaded salah
- Check path model benar
- Reload model: `model = YOLO('models/best.pt', task='segment')`

### Hasil gambar tidak ada mask/warna
**Solusi:**
```python
# Pastikan pakai plot() untuk visualisasi
result_img = results[0].plot()  # Otomatis include masks

# Bukan pakai:
# result_img = results[0].orig_img  # Ini gambar original tanpa annotasi
```

### Confidence terlalu rendah
**Solusi:**
```python
# Set confidence threshold saat inference
results = model(image, conf=0.25)  # Default 0.25

# Atau lebih tinggi untuk hasil lebih presisi
results = model(image, conf=0.5)
```

---

## 📊 Keunggulan Segmentation untuk Penelitian Anda

### 1. Akurasi Lebih Tinggi
- Deteksi tepat bentuk sampah
- Bisa hitung area/volume sampah
- Lebih akurat dalam counting

### 2. Analisis Lebih Detail
- Size/ukuran setiap sampah
- Bentuk dan pattern
- Distribusi spasial

### 3. Visualisasi Lebih Baik
- Mask warna-warni per class
- Lebih mudah dipahami
- Lebih menarik untuk presentasi

---

## 💡 Tips Penggunaan

### 1. Optimize Performance
```python
# Jika inference lambat, turunkan image size
results = model(image, imgsz=640)  # Default
results = model(image, imgsz=480)  # Lebih cepat, akurasi sedikit turun
```

### 2. Batch Processing
```python
# Process multiple images sekaligus
results = model(['image1.jpg', 'image2.jpg', 'image3.jpg'])
```

### 3. Export Masks
```python
# Jika perlu export mask untuk analisis lanjutan
if result.masks is not None:
    masks = result.masks.data  # Tensor mask
    masks_np = masks.cpu().numpy()  # Convert to numpy
    # Save atau process masks
```

---

## ✅ Checklist Segmentation Model

- [ ] Model adalah YOLO Segmentation (.pt)
- [ ] Model sudah di `backend/models/best.pt`
- [ ] Class names sudah dicek
- [ ] Class mapping di `app.py` sudah update
- [ ] Test script PASS
- [ ] Test dengan gambar asli berhasil
- [ ] Hasil ada mask/warna (bukan kotak saja)
- [ ] Confidence reasonable (>50%)
- [ ] Backend bisa run tanpa error
- [ ] Frontend bisa detect dan show hasil

---

## 🎓 Next Steps

Setelah model berfungsi:

1. **Test dengan berbagai gambar sampah**
2. **Adjust confidence threshold** jika perlu
3. **Fine-tune class mapping** 
4. **Collect real data** dari Takalar & Mamuju
5. **Analyze results** dan compile statistik

---

**Model segmentation Anda sekarang sudah fully supported! 🎉**

Jalankan `python test_backend.py` untuk verify semuanya OK!
