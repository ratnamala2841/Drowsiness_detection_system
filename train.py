from ultralytics import YOLO

# Load a pretrained YOLOv8 Nano model 
model = YOLO('yolov8n.pt') 

# Train the model
model.train(
    data='nthuddd-1/data.yaml', 
    epochs=50,                 
    imgsz=640,                
    device='cpu')           