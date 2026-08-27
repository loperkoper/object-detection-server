# Object Detection Server
## تشخیص و شمارش دقیق اشیاء در تصاویر

A high-performance Python server for precise object detection and counting in images using YOLOv8.

### ✨ Features

- **Accurate Object Detection**: Uses YOLOv8 medium model for precise detection
- **Fast Processing**: Optimized for server deployment
- **REST API**: Simple HTTP API for integration
- **Multiple Input Methods**: Upload files or provide URLs
- **Detailed Results**: Get object coordinates, confidence scores, and counts
- **CORS Support**: Easy integration with frontend applications
- **Docker Support**: Ready for containerized deployment

### 🚀 Quick Start

#### Installation

1. **Clone the repository**
```bash
git clone https://github.com/loperkoper/object-detection-server.git
cd object-detection-server
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Copy environment configuration**
```bash
cp .env.example .env
```

4. **Run the server**
```bash
python app.py
```

The server will start on `http://localhost:5000`

#### Using Docker

1. **Build the Docker image**
```bash
docker build -t object-detection-server .
```

2. **Run the container**
```bash
docker run -p 5000:5000 object-detection-server
```

Or use Docker Compose:
```bash
docker-compose up -d
```

### 📡 API Endpoints

#### 1. Health Check
**GET** `/`
```bash
curl http://localhost:5000/
```

#### 2. Detect from File Upload
**POST** `/api/detect`
```bash
curl -X POST -F "file=@image.jpg" http://localhost:5000/api/detect
```

#### 3. Detect from URL
**POST** `/api/detect-url`
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/image.jpg"}' \
  http://localhost:5000/api/detect-url
```

#### 4. Model Information
**GET** `/api/info`
```bash
curl http://localhost:5000/api/info
```

### 🧪 Testing

```bash
# Check server health
python client.py health

# Get server information
python client.py info

# Detect objects from file
python client.py file ./path/to/image.jpg

# Detect objects from URL
python client.py url https://example.com/image.jpg
```

### 📊 Configuration

Edit `.env` file to customize:

```env
PORT=5000
DEBUG=False
MODEL_PATH=yolov8m.pt
CONFIDENCE_THRESHOLD=0.45
IOU_THRESHOLD=0.5
```

### 🎯 Supported Object Classes

The YOLOv8m model can detect 80+ object classes including:
- People, vehicles, animals, sports equipment, furniture, food items and more

### 📈 Performance

- **Model**: YOLOv8 Medium
- **Inference Time**: ~50-100ms per image
- **Max File Size**: 50MB
- **Supported Formats**: JPG, JPEG, PNG, GIF, BMP, WebP

### 🐳 Production Deployment

```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
```

### 📝 License

MIT License

### 👨‍💻 Author

Created by loperkoper

---

**Made with ❤️ for accurate object detection**