"""
Client script to test the Object Detection Server
اسکریپت کلاینت برای آزمایش سرور تشخیص اشیاء
"""

import requests
import json
import sys
from pathlib import Path

# Server URL
SERVER_URL = "http://localhost:5000"

def upload_image(image_path):
    """
    Upload and process an image
    آپلود و پردازش تصویر
    
    Args:
        image_path: Path to image file
    """
    if not Path(image_path).exists():
        print(f"❌ Error: File '{image_path}' not found")
        return
    
    try:
        print(f"📤 Uploading image: {image_path}")
        
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{SERVER_URL}/api/detect", files=files, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            display_results(result)
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.json())
            
    except Exception as e:
        print(f"❌ Error: {e}")

def detect_from_url(image_url):
    """
    Detect objects from image URL
    تشخیص اشیاء از URL تصویر
    
    Args:
        image_url: URL of the image
    """
    try:
        print(f"📤 Processing image from URL: {image_url}")
        
        payload = {'url': image_url}
        response = requests.post(
            f"{SERVER_URL}/api/detect-url",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            display_results(result)
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.json())
            
    except Exception as e:
        print(f"❌ Error: {e}")

def display_results(result):
    """Display detection results"""
    if result.get('status') == 'success':
        print("\n✅ Detection Successful!")
        print(f"⏰ Timestamp: {result.get('timestamp')}")
        print(f"\n📸 Image Info:")
        print(f"   Size: {result['image_info']['width']}x{result['image_info']['height']}")
        
        print(f"\n🎯 Detection Summary:")
        print(f"   Total Objects: {result['total_objects_detected']}")
        
        print(f"\n📊 Object Count:")
        for obj_name, count in result['object_summary'].items():
            print(f"   • {obj_name}: {count}")
        
        print(f"\n🔍 Detailed Detections:")
        for i, detection in enumerate(result['detections'], 1):
            print(f"   {i}. {detection['object']}")
            print(f"      Confidence: {detection['confidence']}")
            print(f"      Position: ({detection['coordinates']['x1']}, {detection['coordinates']['y1']})")
            print(f"      Size: {detection['coordinates']['width']}x{detection['coordinates']['height']}")
    else:
        print(f"\n❌ Error: {result.get('message')}")
        if 'message_fa' in result:
            print(f"   {result.get('message_fa')}")

def get_server_info():
    """Get server and model information"""
    try:
        print("📋 Fetching server information...")
        response = requests.get(f"{SERVER_URL}/api/info", timeout=10)
        
        if response.status_code == 200:
            info = response.json()
            print("\n✅ Server Information:")
            for key, value in info.items():
                if key != 'status':
                    print(f"   {key}: {value}")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        print("   Make sure the server is running on http://localhost:5000")

def health_check():
    """Check server health"""
    try:
        response = requests.get(f"{SERVER_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Server is healthy")
            return True
        else:
            print("❌ Server returned error")
            return False
    except:
        print("❌ Cannot connect to server")
        return False

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("📖 Usage:")
        print(f"   python client.py info                    # Get server info")
        print(f"   python client.py health                  # Check server health")
        print(f"   python client.py file <image_path>       # Detect from file")
        print(f"   python client.py url <image_url>         # Detect from URL")
        print("\n📝 Examples:")
        print(f"   python client.py file ./image.jpg")
        print(f"   python client.py url https://example.com/image.jpg")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'info':
        get_server_info()
    elif command == 'health':
        health_check()
    elif command == 'file':
        if len(sys.argv) < 3:
            print("❌ Error: Image path required")
            return
        upload_image(sys.argv[2])
    elif command == 'url':
        if len(sys.argv) < 3:
            print("❌ Error: Image URL required")
            return
        detect_from_url(sys.argv[2])
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == '__main__':
    main()