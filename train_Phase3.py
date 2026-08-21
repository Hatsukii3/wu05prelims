import os
from ultralytics import YOLO

def main():
    model = YOLO("yolov8n.pt")

    model.train(
        data="dataset.yaml",
        epochs=100,
        batch=16,
        imgsz=640,
        workers=4,
        device="cpu",  
        lr0=0.01,
        lrf=0.01,
        
        # Augmentation 
        degrees=15.0,
        translate=0.1,
        scale=0.5,
        shear=2.0,
        perspective=0.0005,
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        fliplr=0.5,
        flipud=0.0,
        mosaic=1.0,
        mixup=0.15,
        
        project="runs",
        name="vehicle_model",
        exist_ok=True
    )

    metrics = model.val(data="dataset.yaml", split="val")

    best_weights = "runs/vehicle_model/weights/best.pt"
    if os.path.exists(best_weights):
        trained_model = YOLO(best_weights)
        trained_model.export(format="onnx", int8=True, data="dataset.yaml")

if __name__ == "__main__":
    main()