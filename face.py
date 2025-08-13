# capture_face_image.py
import cv2


def capture_face_image(image_path="captured_face.jpg"):
    cap = cv2.VideoCapture(0)  # Start the webcam
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Show the live camera feed
        cv2.imshow("Face Capture", frame)

        # Capture image when the 'Enter' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('\r'):
            cv2.imwrite(image_path, frame)  # Save the image to a file
            break

    cap.release()
    cv2.destroyAllWindows()
