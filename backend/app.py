from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import base64
import io
import sqlite3
from datetime import datetime, timedelta
import json
import numpy as np
from PIL import Image
import cv2

# Import YOLO
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("WARNING: ultralytics not installed. Install with: pip install ultralytics")

app = Flask(__name__)
CORS(app)

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'best.pt')  # GANTI DENGAN NAMA MODEL ANDA
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
RESULTS_FOLDER = os.path.join(BASE_DIR, 'results')
DATABASE_PATH = os.path.join(BASE_DIR, 'database.db')

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# Load YOLO model
yolo_model = None
if YOLO_AVAILABLE and os.path.exists(MODEL_PATH):
    try:
        print(f"Loading YOLO model from {MODEL_PATH}...")
        yolo_model = YOLO(MODEL_PATH)
        print(f"YOLO model loaded successfully!")
        print(f"Model classes: {yolo_model.names}")
    except Exception as e:
        print(f"Error loading YOLO model: {e}")
else:
    if not YOLO_AVAILABLE:
        print("YOLO not available - please install ultralytics")
    else:
        print(f"Model file not found at {MODEL_PATH}")
        print("Please copy your YOLO .pt model to backend/models/best.pt")

# Initialize database
def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Table for detection results
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL,
            image_path TEXT NOT NULL,
            result_path TEXT,
            plastic_bag INTEGER DEFAULT 0,
            bottle INTEGER DEFAULT 0,
            wrapper INTEGER DEFAULT 0,
            total_items INTEGER DEFAULT 0,
            confidence REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table for accumulation stats
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accumulations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL UNIQUE,
            total_items INTEGER DEFAULT 0,
            plastic_bag INTEGER DEFAULT 0,
            bottle INTEGER DEFAULT 0,
            wrapper INTEGER DEFAULT 0,
            total_uploads INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Initialize locations if not exist
    cursor.execute("INSERT OR IGNORE INTO accumulations (location) VALUES ('Takalar')")
    cursor.execute("INSERT OR IGNORE INTO accumulations (location) VALUES ('Mamuju')")
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

init_db()


@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if API and YOLO model are ready"""
    return jsonify({
        'status': 'ok',
        'yolo_available': yolo_model is not None,
        'model_path': MODEL_PATH,
        'model_exists': os.path.exists(MODEL_PATH)
    })


@app.route('/api/track', methods=['POST'])
def track_waste():
    """
    Tracking sampah berdasarkan lokasi, koordinat, tanggal, dan durasi
    """
    try:
        data = request.json
        location = data.get('location')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        start_date = data.get('start_date')
        days = data.get('days')
        
        # Validate input
        if not all([location, latitude, longitude, start_date, days]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Calculate tracking data
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = start_dt + timedelta(days=int(days))
        
        # Simulate tracking data (replace with real calculation)
        distance = np.random.uniform(5, 20)  # km
        avg_speed = np.random.uniform(0.2, 0.5)  # m/s
        direction = np.random.choice(['Tenggara', 'Timur Laut', 'Barat Daya', 'Utara'])
        
        response = {
            'success': True,
            'data': {
                'location': location,
                'coordinates': {
                    'latitude': float(latitude),
                    'longitude': float(longitude)
                },
                'start_date': start_date,
                'end_date': end_dt.strftime('%Y-%m-%d'),
                'days': int(days),
                'tracking_map': f'/api/tracking-map/{location.lower()}',
                'statistics': {
                    'total_distance': round(distance, 2),
                    'avg_speed': round(avg_speed, 3),
                    'dominant_direction': direction,
                    'status': 'Selesai'
                }
            }
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/detect', methods=['POST'])
def detect_waste():
    """
    Deteksi sampah menggunakan YOLO model
    """
    try:
        if yolo_model is None:
            return jsonify({
                'error': 'YOLO model not loaded',
                'message': 'Please ensure your YOLO .pt model is in backend/models/ folder'
            }), 500
        
        data = request.json
        location = data.get('location')
        image_b64 = data.get('image')
        
        if not location or not image_b64:
            return jsonify({'error': 'Missing location or image'}), 400
        
        # Decode base64 image
        if ',' in image_b64:
            image_b64 = image_b64.split(',')[1]
        
        image_bytes = base64.b64decode(image_b64)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Save uploaded image
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        image_filename = f"{location}_{timestamp}.jpg"
        image_path = os.path.join(UPLOAD_FOLDER, image_filename)
        image.save(image_path)
        
        # Convert to numpy array for YOLO
        image_np = np.array(image)
        
        # Run YOLO detection/segmentation
        results = yolo_model(image_np)
        
        # Process results
        detection_counts = {}
        total_items = 0
        confidences = []
        
        # Parse YOLO results (works for both detection and segmentation)
        for result in results:
            # For segmentation models, use masks; for detection, use boxes
            if hasattr(result, 'masks') and result.masks is not None:
                # Segmentation model
                boxes = result.boxes
                masks = result.masks
                print(f"Segmentation model detected: {len(boxes)} objects with masks")
            else:
                # Detection model
                boxes = result.boxes
                print(f"Detection model: {len(boxes)} objects")
            
            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = yolo_model.names[cls_id]
                
                # Count detections
                detection_counts[class_name] = detection_counts.get(class_name, 0) + 1
                total_items += 1
                confidences.append(conf)
        
        # Map class names to categories (customize based on your model)
        plastic_bag = sum(detection_counts.get(name, 0) for name in ['plastic_bag', 'bag', 'plastik'])
        bottle = sum(detection_counts.get(name, 0) for name in ['bottle', 'botol'])
        wrapper = sum(detection_counts.get(name, 0) for name in ['wrapper', 'kemasan', 'packaging'])
        
        # If your model has different class names, update the mapping above
        # Or use direct counts:
        if not plastic_bag and not bottle and not wrapper and total_items > 0:
            # Fallback: distribute evenly if class names don't match
            classes = list(detection_counts.keys())
            if len(classes) >= 3:
                plastic_bag = detection_counts.get(classes[0], 0)
                bottle = detection_counts.get(classes[1], 0)
                wrapper = detection_counts.get(classes[2], 0)
            elif len(classes) == 2:
                plastic_bag = detection_counts.get(classes[0], 0)
                bottle = detection_counts.get(classes[1], 0)
            elif len(classes) == 1:
                plastic_bag = detection_counts.get(classes[0], 0)
        
        avg_confidence = np.mean(confidences) if confidences else 0
        
        # Save detection/segmentation result image
        # For segmentation models, this will include masks
        # For detection models, this will include bounding boxes
        result_image = results[0].plot()  # Automatically handles both detection and segmentation
        result_filename = f"{location}_{timestamp}_result.jpg"
        result_path = os.path.join(RESULTS_FOLDER, result_filename)
        
        # Convert RGB to BGR for cv2 (plot() returns RGB)
        result_image_bgr = cv2.cvtColor(result_image, cv2.COLOR_RGB2BGR)
        cv2.imwrite(result_path, result_image_bgr)
        
        # Save to database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO detections 
            (location, image_path, result_path, plastic_bag, bottle, wrapper, total_items, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (location, image_path, result_path, plastic_bag, bottle, wrapper, total_items, avg_confidence))
        
        # Update accumulation
        cursor.execute('''
            UPDATE accumulations 
            SET total_items = total_items + ?,
                plastic_bag = plastic_bag + ?,
                bottle = bottle + ?,
                wrapper = wrapper + ?,
                total_uploads = total_uploads + 1,
                last_updated = CURRENT_TIMESTAMP
            WHERE location = ?
        ''', (total_items, plastic_bag, bottle, wrapper, location))
        
        conn.commit()
        
        # Get updated accumulation
        cursor.execute('SELECT * FROM accumulations WHERE location = ?', (location,))
        acc_row = cursor.fetchone()
        
        conn.close()
        
        # Determine dominant waste
        waste_types = {
            'Kantong Plastik': plastic_bag,
            'Botol Plastik': bottle,
            'Kemasan/Wrapper': wrapper
        }
        dominant = max(waste_types.items(), key=lambda x: x[1])
        
        # Convert result image to base64
        with open(result_path, 'rb') as f:
            result_b64 = base64.b64encode(f.read()).decode('utf-8')
        
        response = {
            'success': True,
            'data': {
                'location': location,
                'total_detected': total_items,
                'confidence': round(avg_confidence * 100, 1),
                'dominant': {
                    'name': dominant[0],
                    'count': dominant[1],
                    'percentage': round(dominant[1] / total_items * 100, 1) if total_items > 0 else 0
                },
                'breakdown': {
                    'plastic_bag': plastic_bag,
                    'bottle': bottle,
                    'wrapper': wrapper
                },
                'all_detections': detection_counts,
                'result_image': f'data:image/jpeg;base64,{result_b64}',
                'accumulation': {
                    'total': acc_row[2],
                    'plastic_bag': acc_row[3],
                    'bottle': acc_row[4],
                    'wrapper': acc_row[5],
                    'uploads': acc_row[6]
                } if acc_row else None
            }
        }
        
        return jsonify(response)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats/<location>', methods=['GET'])
def get_stats(location):
    """
    Get accumulation statistics for a location
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM accumulations WHERE location = ?', (location,))
        row = cursor.fetchone()
        
        if not row:
            return jsonify({'error': 'Location not found'}), 404
        
        cursor.execute('''
            SELECT COUNT(*), AVG(confidence) 
            FROM detections 
            WHERE location = ?
        ''', (location,))
        det_stats = cursor.fetchone()
        
        conn.close()
        
        return jsonify({
            'location': row[1],
            'total_items': row[2],
            'plastic_bag': row[3],
            'bottle': row[4],
            'wrapper': row[5],
            'total_uploads': row[6],
            'last_updated': row[7],
            'avg_confidence': round(det_stats[1] * 100, 1) if det_stats[1] else 0
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/tracking-map/<location>', methods=['GET'])
def get_tracking_map(location):
    """
    Serve tracking map image for location
    """
    try:
        # Look for tracking map image
        map_path = os.path.join(BASE_DIR, 'static', f'{location}_tracking.png')
        
        if os.path.exists(map_path):
            return send_file(map_path, mimetype='image/png')
        else:
            # Return placeholder or error
            return jsonify({
                'error': 'Map not found',
                'message': f'Please add {location}_tracking.png to backend/static/ folder'
            }), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("MarineTrace Backend Server")
    print("="*60)
    print(f"YOLO Model: {'✓ Loaded' if yolo_model else '✗ Not loaded'}")
    print(f"Database: ✓ Initialized")
    print(f"Server: http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
