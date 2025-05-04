import os
import time
import json
from datetime import datetime
from PIL import ImageGrab, Image
from ultralytics import YOLO
import numpy as np
import easyocr  # 導入 EasyOCR 用於文字識別

# Add a custom JSON encoder to handle NumPy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

class ScreenRecognizer:
    def __init__(self):
        self.model = YOLO("screen_descriptor/model.pt")
        self.reader = easyocr.Reader(['ch_tra', 'en'])  # 支援繁體中文和英文
        self.history_logs_dir = "history_logs"
        
        # Create history_logs directory if it doesn't exist
        if not os.path.exists(self.history_logs_dir):
            os.makedirs(self.history_logs_dir)
    
    def capture_screen(self):
        """Capture the current screen and save it to history_logs directory"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = os.path.join(self.history_logs_dir, f"screen_{timestamp}.png")
        
        # Capture the screen
        screenshot = ImageGrab.grab()
        screenshot.save(screenshot_path)
        
        print(f"📸 Screenshot saved to: {screenshot_path}")
        return screenshot_path
    
    def detect_objects(self, image_path):
        """Perform object detection on the given image"""
        print("🔍 Detecting objects...")
        results = self.model(image_path)
        
        # Save the detection result image
        result_path = image_path.replace(".png", "_detected.png")
        results[0].save(filename=result_path)
        print(f"✅ Detection result saved to: {result_path}")
        
        return results[0]
    
    def recognize_text(self, image_path):
        """使用 EasyOCR 識別圖片中的文字"""
        print(f"📝 Recognizing text in: {os.path.basename(image_path)}")
        
        # 使用 PIL 讀取圖片，然後轉換為 numpy array 給 EasyOCR 使用
        img = Image.open(image_path)
        img_array = np.array(img)
        
        # 使用 EasyOCR 識別文字
        results = self.reader.readtext(img_array)
        
        recognized_text = []
        for (bbox, text, prob) in results:
            if prob > 0.2:  # 只保留置信度 > 0.2 的結果
                recognized_text.append({
                    "text": text,
                    "confidence": float(prob),
                    "bbox": bbox
                })
        
        return recognized_text
    
    def analyze_objects(self, results, image_path):
        """Analyze each detected object using EasyOCR"""
        boxes = results.boxes
        objects_data = []
        
        if len(boxes) == 0:
            print("❗ No objects detected in the image.")
            return objects_data
        
        print(f"🔎 Found {len(boxes)} objects. Analyzing each object...")
        
        # Create a directory to store the cropped objects
        crops_dir = os.path.join(self.history_logs_dir, "crops")
        if not os.path.exists(crops_dir):
            os.makedirs(crops_dir)
        
        # Load the original image
        original_image = Image.open(image_path)
        
        # For each detected object
        for i, box in enumerate(boxes):
            # Get the bounding box coordinates (xmin, ymin, xmax, ymax)
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            # Create position dictionary
            position = {
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "width": x2 - x1,
                "height": y2 - y1,
                "center_x": (x1 + x2) // 2,
                "center_y": (y1 + y2) // 2
            }
            
            # Crop the object from the original image
            crop = original_image.crop((x1, y1, x2, y2))
            
            # Save the cropped image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            crop_path = os.path.join(crops_dir, f"object_{i}_{timestamp}.png")
            crop.save(crop_path)
            
            # 顯示進度資訊
            print(f"\n📊 Analyzing object {i+1}/{len(boxes)}...")
            print(f"📄 Saved to: {crop_path}")
            
            # 使用 EasyOCR 識別文字
            text_results = self.recognize_text(crop_path)
            
            # 組合所有識別出的文字
            all_text = " ".join([item["text"] for item in text_results if item["text"].strip()])
            
            # Add to objects data
            objects_data.append({
                "position": position,
                "ocr_results": text_results,
                "all_text": all_text,
                "image_path": crop_path  # 保存圖片路徑，以便後續檢視
            })
            
            # Small delay
            time.sleep(0.5)
        
        return objects_data
    
    def run(self):
        """Run the full screen recognition process"""
        # Capture the screen
        screenshot_path = self.capture_screen()
        
        # Detect objects in the screenshot
        results = self.detect_objects(screenshot_path)

        # 印出總共有幾個物件
        print(f"🔍 Found {len(results.boxes)} objects in the screenshot.")
        
        # 只保留面積前50大的物件
        if len(results.boxes) > 50:
            # Calculate area as (xmax - xmin) * (ymax - ymin)
            areas = []
            for box in results.boxes:
                x1, y1, x2, y2 = box.xyxy[0]  # 取得座標
                area = (x2 - x1) * (y2 - y1)  # 計算面積
                areas.append(area)
            
            # 獲取前50大物件的索引
            top_50_indices = sorted(range(len(areas)), key=lambda i: areas[i], reverse=True)[:50]
            results.boxes = results.boxes[top_50_indices]
            print(f"🔍 Keeping top 50 largest objects: {len(results.boxes)} objects remaining.")
        
        # 分析篩選後的物件
        objects_data = self.analyze_objects(results, screenshot_path)
        
        # Save the results to a JSON file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = os.path.join(self.history_logs_dir, f"screen_ocr_{timestamp}.json")
        
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(objects_data, f, ensure_ascii=False, indent=2, cls=NumpyEncoder)
        
        print(f"\n✅ Analysis complete! Results saved to: {json_path}")
        print(f"📊 Recognized {len(objects_data)} objects on screen")
        
        return objects_data

# Run the screen recognizer if the script is executed directly
if __name__ == "__main__":
    print("🖥️ Running Screen Recognizer")
    recognizer = ScreenRecognizer()
    objects = recognizer.run()
    
    # Print a summary of the recognized objects
    print("\n📋 Summary of recognized objects:")
    for i, obj in enumerate(objects):
        pos = obj["position"]
        text_preview = obj["all_text"][:50] + "..." if obj["all_text"] and len(obj["all_text"]) > 50 else obj["all_text"]
        print(f"{i+1}. Position: ({pos['x1']},{pos['y1']}) to ({pos['x2']},{pos['y2']}), Text: {text_preview}")