# System Architecture

The smart parking system is composed of the following components:

Input Layer (Configuration)
-Create Camera Objects linking RTSP/HTTP urls
-Define Parking Spots for every Camera Objectq

Input Layer
- IP Camera
- Sensing Unit Program

Communication Layer
- RabbitMQ
- Redis

Processing Layer
- Kubernetes
- Inference Pods
- YOLO Model

Storage Layer
- MongoDB

Output Layer
- ReactJS / React Native Frontend

The inference pods consume messages from RabbitMQ, retrieve images from Redis, perform vehicle detection using YOLO, execute the occupancy algorithm, and update MongoDB.