import os
from pathlib import Path
from ultralytics import YOLO

def main():
    base_dir = Path(__file__).resolve().parent
    runs_dir = base_dir / "runs"
    checkpoint_path = runs_dir / "vehicle_model" / "weights" / "last.pt"

    if checkpoint_path.exists():
        print("[3/3] Resuming model fine-tuning from checkpoint...")
        model = YOLO(str(checkpoint_path))
        
        model.train(resume=True)
    else:
        print("[3/3] Initializing new model fine-tuning...")
        model = YOLO("yolov8n.pt")
        model.train(
            data = str(base_dir / "dataset.yaml"),
            epochs = 100,
            batch = 16,                 
            imgsz = 640,
            workers = 4,                  
            device = 0,                  
            amp = True,                  
            cache = False,             
            lr0 = 0.01,
            lrf = 0.01,

            # Updated Augmentation parameters
            hsv_h = 1.0,           # Hue variation
            hsv_s = 0.0,           # Saturation set to 0 to preserve grayscaling
            hsv_v = 0.5,           # Brightness variation
            degrees = 180.0,       # Allow all orientations (180 degrees)
            translate = 0.0,       # Translation set to 0
            scale = 0.5,           # Scale factor (0.5 means range 0.5x to 1.5x)
            perspective = 0.0005,  # Perspective adjustment
            flipud = 0.5,          # 50% chance vertical flip
            fliplr = 0.5,          # 50% chance horizontal flip
            mosaic = 0.0,          # Mosaic disabled (0)
            erasing = 0.4,         # Random erasing probability

            project = str(runs_dir),
            name = "vehicle_model",
            exist_ok = True
        )

    print("Fine tuning phase completed.")

    metrics = model.val(data=str(base_dir / "dataset.yaml"), split="val")

    best_weights = runs_dir / "vehicle_model" / "weights" / "best.pt"
    if best_weights.exists():
        trained_model = YOLO(str(best_weights))
        print("ALL Phase 3 tasks completed successfully.")

if __name__ == "__main__":
    main()