import os
import time
import json
from datetime import datetime
from PIL import ImageGrab, Image
from ultralytics import YOLO
import requests
import base64

class ImageAnalyzer:
    def __init__(self, vision_model="llava-phi3:latest"):
        self.vision_model = vision_model
        self.ollama_url = "http://localhost:11434/api/chat"

    def encode_image_to_base64(self, image_path):
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"❌ Error reading image: {e}")
            return None

    def analyze_image(self, image_path, prompt="Please describe this image less than 5 words"):
        absolute_path = os.path.abspath(image_path)

        if not os.path.exists(absolute_path):
            print(f"❌ File not found: {absolute_path}")
            return

        image_data = self.encode_image_to_base64(absolute_path)
        if not image_data:
            print("❌ Failed to encode image.")
            return

        messages = [
            {
                "role": "user",
                "content": prompt,
                "images": [image_data]
            }
        ]

        try:
            response = requests.post(
                self.ollama_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps({
                    "model": self.vision_model,
                    "messages": messages,
                    "stream": True
                }),
                stream=True
            )

            if response.status_code != 200:
                print(f"❌ Vision model error: {response.status_code}")
                print(response.text)
                return

            print(f"\n🖼️ Analyzing: {os.path.basename(image_path)}")
            print("Assistant: ", end="", flush=True)
            full_response = ""

            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line)
                        if "message" in chunk and "content" in chunk["message"]:
                            content = chunk["message"]["content"]
                            if content:
                                print(content, end="", flush=True)
                                full_response += content
                        if chunk.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue

            print()
            return full_response

        except Exception as e:
            print(f"❌ Error analyzing image: {e}")

class ScreenDescriptor:
    def __init__(self):
        self.model = YOLO("screen_descriptor/model.pt")
        self.image_analyzer = ImageAnalyzer()
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
    
    def describe_objects(self, results, image_path):
        """Describe each detected object using the ImageAnalyzer"""
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
            
            # 顯示分析資訊
            print(f"\n📊 Analyzing object {i+1}/{len(boxes)}...")
            print(f"📄 Saved to: {crop_path}")
            
            # Analyze the cropped image
            description = self.image_analyzer.analyze_image(
                crop_path, 
                prompt = r"Describe this UI element in one sentence, if there's any text, please include it. response me like the format: {type:{folder/file/button}, text:{content you see/icon}}"
            )
            
            # Add to objects data
            objects_data.append({
                "position": position,
                "description": description,
                "image_path": crop_path
            })
            
            # Small delay to avoid overwhelming the API
            time.sleep(1)
        
        return objects_data
    
    def run(self):
        """Run the full screen description process"""
        # Capture the screen
        screenshot_path = self.capture_screen()
        
        # Detect objects in the screenshot
        results = self.detect_objects(screenshot_path)

        # 印出總共有幾個icon
        print(f"🔍 Found {len(results.boxes)} objects in the screenshot.")

        # 只保留面積前20大的物件
        if len(results.boxes) > 20:
            # Calculate area as (xmax - xmin) * (ymax - ymin)
            areas = []
            for box in results.boxes:
                x1, y1, x2, y2 = box.xyxy[0]  # Correct access to coordinates
                area = (x2 - x1) * (y2 - y1)  # Calculate the area
                areas.append(area)
            
            top_20_indices = sorted(range(len(areas)), key=lambda i: areas[i], reverse=True)[:20]
            results.boxes = results.boxes[top_20_indices]
            print(f"🔍 Keeping top 20 largest objects: {len(results.boxes)} objects remaining.")
        
        # Describe each detected object
        objects_data = self.describe_objects(results, screenshot_path)
        
        # Save the results to a JSON file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = os.path.join(self.history_logs_dir, f"screen_analysis_{timestamp}.json")
        
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(objects_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Analysis complete! Results saved to: {json_path}")
        print(f"📊 Found and described {len(objects_data)} objects on screen")
        
        return objects_data

# Run the screen descriptor if the script is executed directly
if __name__ == "__main__":
    print("🖥️ Running Screen Descriptor")
    descriptor = ScreenDescriptor()
    objects = descriptor.run()
    
    # Print a summary of the detected objects
    print("\n📋 Summary of detected objects:")
    for i, obj in enumerate(objects):
        pos = obj["position"]
        desc_preview = obj["description"][:50] + "..." if obj["description"] and len(obj["description"]) > 50 else obj["description"]
        print(f"{i+1}. Position: ({pos['x1']},{pos['y1']}) to ({pos['x2']},{pos['y2']}), Description: {desc_preview}")