import os
from pyexpat import model
from ultralytics import YOLO

def main():
    print("[3/3] Initializing model fine-tuning...")
    model = YOLO("yolov8n.pt")

    print("Training yolov8n model on processed dataset...")
    model.train(
        data = "dataset.yaml",
        epochs = 100,
        batch = 16,
        imgsz = 640,
        workers = 8,
        device = 0,
        amp = True,
        lr0 = 0.01,
        lrf = 0.01,

        #Augmentation
        degrees = 15.0,
        translate = 0.1,
        scale = 0.5,
        shear = 2.0,
        perspective = 0.0005,
        fliplr = 0.5,
        mosaic = 1.0,
        mixup = 0.5,

        project = "runs",
        name = "vehicle_model",
        exist_ok = True
        )
    print("Fine tuning phase completed.")

    metrics = model.val(data="dataset.yaml", split="val")

    best_weights = "runs/vehicle_model/weights/best.pt"
    if os.path.exists(best_weights):
        trained_model = YOLO(best_weights)
        print("ALL Phase 3 tasks completed successfully.")

if __name__ == "__main__":
    main()