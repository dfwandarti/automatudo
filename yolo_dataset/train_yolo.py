from ultralytics import YOLO

# Carregar modelo pré-treinado (ex: YOLOv8n)
model = YOLO("yolo11n.pt")

# Treinar com os dados customizados
results = model.train(data="custom.yaml", epochs=100, imgsz=640,
                      patience=10, name="logos", verbose=True,
                      cache=False)
