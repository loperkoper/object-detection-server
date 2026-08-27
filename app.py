"""
Object Detection and Counting Server
تشخیص و شمارش اشیاء در تصاویر
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
from PIL import Image
import io
import os
from dotenv import load_dotenv
from ultralytics import YOLO
import logging
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'}
MODEL_PATH = os.getenv('MODEL_PATH', 'yolov8m.pt')

# Global model cache
model = None

def load_model():
    """Load YOLO model"""
    global model
    try:
        logger.info(f"Loading YOLO model from {MODEL_PATH}")
        model = YOLO(MODEL_PATH)
        logger.info("Model loaded successfully")
        return model
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image(image_data):
    """
    Process image and detect objects
    بررسی تصویر و تشخیص اشیاء
    
    Args:
        image_data: Image file or bytes
        
    Returns:
        Dictionary with detection results
    """
    try:
        # Load image
        if isinstance(image_data, bytes):
            image = Image.open(io.BytesIO(image_data))
        else:
            image = Image.open(image_data)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert PIL image to numpy array
        img_array = np.array(image)
        
        logger.info(f"Image loaded. Shape: {img_array.shape}")
        
        # Run YOLO detection
        results = model(img_array, conf=0.45, iou=0.5)
        
        # Process results
        detections = []
        object_counts = {}
        
        for result in results:
            boxes = result.boxes
            
            for box in boxes:
                # Get box coordinates
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                confidence = box.conf[0].item()
                class_id = int(box.cls[0].item())
                class_name = result.names[class_id]
                
                # Count objects by class
                if class_name not in object_counts:
                    object_counts[class_name] = 0
                object_counts[class_name] += 1
                
                # Store detection details
                detection = {
                    'object': class_name,
                    'confidence': round(confidence, 4),
                    'coordinates': {
                        'x1': round(x1, 2),
                        'y1': round(y1, 2),
                        'x2': round(x2, 2),
                        'y2': round(y2, 2),
                        'width': round(x2 - x1, 2),
                        'height': round(y2 - y1, 2)
                    }
                }
                detections.append(detection)
        
        # Prepare response
        response = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'image_info': {
                'width': img_array.shape[1],
                'height': img_array.shape[0],
                'channels': img_array.shape[2] if len(img_array.shape) > 2 else 1
            },
            'total_objects_detected': len(detections),
            'object_summary': object_counts,
            'detections': detections
        }
        
        logger.info(f"Detection completed. Found {len(detections)} objects")
        return response
        
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Object Detection Server',
        'version': '1.0.0',
        'model': 'YOLOv8m'
    })

@app.route('/api/detect', methods=['POST'])
def detect_objects():
    """
    Detect objects in uploaded image
    تشخیص اشیاء در تصویر آپلود شده
    """
    try:
        # Check if file is provided
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No file provided',
                'message_fa': 'فایلی ارائه نشده است'
            }), 400
        
        file = request.files['file']
        
        # Check filename
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'Empty filename',
                'message_fa': 'نام فایل خالی است'
            }), 400
        
        # Check file extension
        if not allowed_file(file.filename):
            return jsonify({
                'status': 'error',
                'message': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}',
                'message_fa': f'نوع فایل مجاز نیست. انواع مجاز: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({
                'status': 'error',
                'message': f'File size exceeds maximum ({MAX_FILE_SIZE / 1024 / 1024}MB)',
                'message_fa': f'حجم فایل از حداکثر مجاز ({MAX_FILE_SIZE / 1024 / 1024}MB) بیشتر است'
            }), 400
        
        # Read file content
        file_content = file.read()
        
        # Process image
        result = process_image(file_content)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in detect_objects: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'message_fa': 'خرابی در پردازش تصویر'
        }), 500

@app.route('/api/detect-url', methods=['POST'])
def detect_from_url():
    """
    Detect objects from image URL
    تشخیص اشیاء از URL تصویر
    """
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'status': 'error',
                'message': 'URL not provided',
                'message_fa': 'URL ارائه نشده است'
            }), 400
        
        url = data['url']
        
        # Download image from URL
        import urllib.request
        import ssl
        
        ssl._create_default_https_context = ssl._create_unverified_context
        
        with urllib.request.urlopen(url, timeout=10) as response:
            file_content = response.read()
        
        # Process image
        result = process_image(file_content)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in detect_from_url: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'message_fa': 'خرابی در بارگذاری تصویر از URL'
        }), 500

@app.route('/api/info', methods=['GET'])
def model_info():
    """Get model information"""
    try:
        if model is None:
            return jsonify({
                'status': 'error',
                'message': 'Model not loaded'
            }), 500
        
        return jsonify({
            'status': 'success',
            'model': 'YOLOv8m',
            'model_path': MODEL_PATH,
            'supported_formats': list(ALLOWED_EXTENSIONS),
            'max_file_size_mb': MAX_FILE_SIZE / 1024 / 1024,
            'confidence_threshold': 0.45,
            'iou_threshold': 0.5
        }), 200
        
    except Exception as e:
        logger.error(f"Error in model_info: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found',
        'message_fa': 'نقطه پایانی یافت نشد'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'status': 'error',
        'message': 'Internal server error',
        'message_fa': 'خرابی داخلی سرور'
    }), 500

if __name__ == '__main__':
    # Load model on startup
    load_model()
    
    # Get port from environment or use default
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Object Detection Server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)