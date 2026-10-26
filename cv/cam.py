from ultralytics import YOLO
import cv2
import face_recognition
import numpy as np
import subprocess
import os


model_throw = YOLO("cv/best.pt")
model_face = YOLO("cv/yolov8n-face.pt")


known_encodings = []
known_names = []

people_folder = "static/people"
for filename in os.listdir(people_folder):
    if filename.lower().endswith(('.jpg', '.png', '.jpeg')):
        path = os.path.join(people_folder, filename)
        image = face_recognition.load_image_file(path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_encodings.append(encodings[0])
            known_names.append(os.path.splitext(filename)[0])
            print(f"Эталон добавлен: {filename}")
        else:
            print(f"Лицо не найдено в эталоне: {filename}")

print(f"Всего эталонов: {len(known_encodings)}")


cap = cv2.VideoCapture("b1.mp4")

saved = False
final_message = None


prev_hand_center = None
prev_trash_center = None
throw_confirmed = False

while cap.isOpened():
    ret, frame = cap.read()
    if not ret or saved:
        break

    hand_center = None
    trash_center = None

    results_throw = model_throw(frame)

    for result in results_throw:
        for box in result.boxes:
            cls = int(box.cls[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            if cls == 0:  # рука
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                hand_center = (cx, cy)
            elif cls == 1:  # мусор
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                trash_center = (cx, cy)

    if prev_hand_center and prev_trash_center and hand_center and trash_center:
        dist_now = np.linalg.norm(np.array(hand_center) - np.array(trash_center))
        dist_prev = np.linalg.norm(np.array(prev_hand_center) - np.array(prev_trash_center))
        diff = dist_now - dist_prev

        if diff > 50:  
            throw_confirmed = True

    prev_hand_center = hand_center
    prev_trash_center = trash_center

    if throw_confirmed:
        
        results_face = model_face(frame)
        recognized_name = None

        for result in results_face:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                pad = 5
                x1 = max(0, x1 - pad)
                y1 = max(0, y1 - pad)
                x2 = min(frame.shape[1], x2 + pad)
                y2 = min(frame.shape[0], y2 + pad)

                face_crop = frame[y1:y2, x1:x2]
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
                            cv2.imwrite("recognized_face.jpg", face_crop)
                            final_message = f"МУСОР выброшен — лицо распознано: {recognized_name}"

                            subprocess.run(['python', 'mes.py', recognized_name])

                            saved = True
                            break

            if saved:
                break

        if not saved and not final_message:
            final_message = "МУСОР выброшен — лицо НЕ распознано"

    elif not throw_confirmed and not final_message:
        final_message = "НЕТ броска"

    cv2.imshow("Detection-CAI", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

if final_message:
    print(final_message)
else:
    print("НЕТ мусора (финально)")
