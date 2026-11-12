
import cv2
import webbrowser
import time

camera = cv2.VideoCapture(0)
detector = cv2.QRCodeDetector()

last_item = None
last_time = 0

print("Smart Lost & Found Scanner Started")
print("Show a QR code to the webcam.")
print("Press Q to quit.")

while True:
    success, frame = camera.read()

    if not success:
        print("Camera not detected.")
        break

    data, points, _ = detector.detectAndDecode(frame)

    if data:
        cv2.putText(
            frame,
            f"Item: {data}",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        current_time = time.time()

        if data != last_item or current_time - last_time > 5:
            print("QR detected:", data)

            url = f"http://127.0.0.1:5001/item/{data}"
            print("Opening:", url)
            webbrowser.open(url)

            last_item = data
            last_time = current_time

    cv2.imshow("Smart Lost & Found Scanner", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()
