from ultralytics import YOLO

# Carregar modelo pré-treinado (ex: YOLOv8n)
model = YOLO("yolo11n.pt")

# Treinar com os dados customizados
results = model.train(data="custom.yaml", 
                      epochs=150, 
                    #   patience=20, 
                      name="logos", 
                      verbose=True,
                      cache=False,
                      mosaic=1.0,       # Ativa Mosaic
                      close_mosaic=10,  # Desativa Mosaic nas últimas 10 épocas
                      hsv_h=0.015,      # Variação de cor
                      fliplr=0.5,       # 50% de chance de espelhar
                      flipud=0.0        # Nunca inverter verticalmente)
                      )
