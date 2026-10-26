from ultralytics import YOLO
import cv2
import face_recognition
import numpy as np
import os

# === YOLO модель для лица ===
model_face = YOLO("cv/yolov8n-face.pt")

# === Загружаем эталоны ===
known_encodings = []
known_names = []

people_folder = "static/people"
for filename in os.listdir(people_folder):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        path = os.path.join(people_folder, filename)
        image = face_recognition.load_image_file(path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_encodings.append(encodings[0])
            known_names.append(os.path.splitext(filename)[0])
            print(f"✅ Эталон добавлен: {filename}")
        else:
            print(f"⚠️ Нет лица в эталоне: {filename}")

print(f"🔍 Всего эталонов: {len(known_encodings)}")

# === Видео ===
cap = cv2.VideoCapture('b1.mp4')

saved = False  # флаг, чтобы сохранить только 1 раз
frame_id = 0

while cap.isOpened() and not saved:
    ret, frame = cap.read()
    if not ret:
        break

    frame_id += 1

    results_face = model_face(frame)

    for result in results_face:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            h, w, _ = frame.shape

            # === Добавляем запас к рамке ===
            pad_w = int((x2 - x1) * 0.3)
            pad_h = int((y2 - y1) * 0.3)

            x1 = max(0, x1 - pad_w)
            y1 = max(0, y1 - pad_h)
            x2 = min(w, x2 + pad_w)
            y2 = min(h, y2 + pad_h)

            face_crop = frame[y1:y2, x1:x2]

            if face_crop.size == 0:
                continue

            rgb_face = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
            encodings = face_recognition.face_encodings(rgb_face)

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            if encodings:
                face_encoding = encodings[0]
                matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
                face_distances = face_recognition.face_distance(known_encodings, face_encoding)

                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        recognized_name = known_names[best_match_index]
                        print(f"✅ Лицо распознано: {recognized_name}")

                        # === Сохраняем и выходим ===
                        save_dir = "saved_faces"
                        os.makedirs(save_dir, exist_ok=True)
                        save_path = os.path.join(save_dir, f"{recognized_name}_{frame_id}.jpg")
                        cv2.imwrite(save_path, face_crop)
                        print(f"💾 Сохранено в: {save_path}")

                        saved = True
                        break  # выходим из цикла по box

            else:
                print("⚠️ Лицо не найдено face_recognition")

        if saved:
            break  # выходим из цикла по result

    cv2.imshow("Face YOLO + Recognition", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

if saved:
    print("🎉 Лицо успешно распознано и сохранено. Работа завершена.")
else:
    print("❌ Совпадений не найдено.")
