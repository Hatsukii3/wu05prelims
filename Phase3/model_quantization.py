from ultralytics import YOLO

model = YOLO("runs/vehicle_model/weights/best.pt")
model.export(format="engine", half=True)