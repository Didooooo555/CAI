from ultralytics import YOLO
import cv2

# Загружаем YOLOv8n-face
model = YOLO("cv/yolov8n-face.pt")

# Открываем видеофайл или камеру (0 - встроенная камера)
cap = cv2.VideoCapture('b1.mp4')
# или: cap = cv2.VideoCapture(0)
 
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Запуск модели на кадре
    results = model(frame)

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)

    # Показываем кадр
    cv2.imshow('Face Detection', frame)

    # Выход по нажатию ESC
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
