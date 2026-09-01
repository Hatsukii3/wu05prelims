import cv2
from ultralytics import YOLO

# 1. Load the pre-trained YOLOv8 Nano model (automatically downloads on first run)
model = YOLO("./runs/vehicle_model/weights/best.pt")

# 2. Initialize the webcam (0 is usually the default built-in camera)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

while True:
    # Capture frame-by-frame
    frame = cv2.imread(f"./test.jpg")
    

    # 3. Run YOLOv8 inference on the frame
    # stream=True utilizes a generator for memory efficiency during video processing
    results = model(frame, stream=True)

    # 4. Process and visualize the results
    for r in results:
        # Use Ultralytics' built-in plotter to draw bounding boxes and labels
        annotated_frame = r.plot()

    # 5. Display the frame using OpenCV
    cv2.imshow("YOLOv8 Real-Time Detection", annotated_frame)

    # Break the loop if 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up and close windows
cap.release()
cv2.destroyAllWindows()