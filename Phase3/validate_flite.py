from pathlib import Path
from ultralytics import YOLO

def main():
    base_dir = Path(__file__).resolve().parent

    dataset_yaml = base_dir / "dataset.yaml"

    tflite_model_path = base_dir / "runs" / "vehicle_model" / "weights" / "best_saved_model" / "best_int8.tflite"

    if not tflite_model_path.exists():
        tflite_model_path = base_dir / "runs" / "vehicle_model" / "weights" / "best_int8.tflite"

    if not tflite_model_path.exists():
        print(f"Error: TFLite model file could not be found. Please run quantization.py first.")
        return

    print(f"Validating TFLite model at: {tflite_model_path}")
    model = YOLO(str(tflite_model_path))

    # Match the image size used during export
    metrics = model.val(data=str(dataset_yaml), split="val", imgsz=(736, 1280))

    precision = metrics.box.mp
    recall = metrics.box.mr
    map50 = metrics.box.map50
    map50_95 = metrics.box.map
    f1_score = metrics.box.f1.mean() if hasattr(metrics.box.f1, 'mean') else 0.0

    print("\n" + "=" * 40)
    print("     QUANTIZED MODEL EVALUATION")
    print("=" * 40)
    print(f"Precision:       {precision:.4f}")
    print(f"Recall:          {recall:.4f}")  
    print(f"mAP@0.5:         {map50:.4f}")
    print(f"mAP@0.5:0.95:    {map50_95:.4f}")
    print(f"F1 Score:        {f1_score:.4f}")
    print("=" * 40 + "\n")

if __name__ == "__main__":
    main()