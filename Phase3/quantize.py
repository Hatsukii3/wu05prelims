from pathlib import Path
from ultralytics import YOLO

def main():
    base_dir = Path(__file__).resolve().parent
    weights_path = base_dir / "runs" / "vehicle_model" / "weights" / "best.pt"
    dataset_yaml = base_dir / "dataset.yaml"

    if not weights_path.exists():
        print(f"Error: Could not find the weights at {weights_path}")
        return

    if not dataset_yaml.exists():
        print(f"Error: Could not find dataset config at {dataset_yaml}")
        return

    print("Loading model for INT8 quantization...")
    model = YOLO(str(weights_path))

    exported_path = model.export(
        format="litert",
        int8=True,
        data=str(dataset_yaml),
        imgsz=(640, 640),
        fraction=0.05  # Uses ~250 images instead of ~5,000 to prevent hanging
    )

    print(f"Quantized model successfully exported to: {exported_path}")

if __name__ == "__main__":
    main()
