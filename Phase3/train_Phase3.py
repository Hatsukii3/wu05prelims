import os
from ultralytics import YOLO

def main():
    print("[3/3] Initializing model fine-tuning...")
    model = YOLO("yolov8n.pt")

    print("Training YOLOv8n on processed dataset...")
    model.train(
        data="dataset.yaml",
        epochs=100,
        batch=16,
        imgsz=640,
        workers=4,
        device="cpu",
        lr0=0.01,
        lrf=0.01,
        degrees=15.0,
        translate=0.1,
        scale=0.5,
        shear=2.0,
        perspective=0.0005,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.15,
        project="runs",
        name="vehicle_model",
        exist_ok=True
    )
    print("Fine-tuning training phase completed.")

    metrics = model.val(data="dataset.yaml", split="val")

    best_weights = "runs/vehicle_model/weights/best.pt"
    if os.path.exists(best_weights):
        trained_model = YOLO(best_weights)
        trained_model.export(format="onnx", int8=True, data="dataset.yaml")
        print("Model successfully exported to ONNX INT8 format.")
    
    print("All Phase 3 pipeline!")

if __name__ == "__main__":
    main()