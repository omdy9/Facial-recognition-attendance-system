import cv2
import numpy as np
import dlib

def encode_face(image_path):
    """
    Encodes a face from the given image and returns the face encoding.
    """
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
    face_rec_model = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")

    image = cv2.imread(image_path)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    dets = detector(rgb_image, 1)
    if len(dets) == 0:
        return None

    shapes = [predictor(rgb_image, det) for det in dets]
    face_descriptors = [face_rec_model.compute_face_descriptor(rgb_image, shape) for shape in shapes]

    if len(face_descriptors) > 0:
        return np.array(face_descriptors[0])
    return None

def capture_face_encoding():
    """
    Captures a face from the webcam and returns the encoding.
    """
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
    face_rec_model = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")

    video_capture = cv2.VideoCapture(0)
    face_encoding = None

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        dets = detector(rgb_frame, 1)
        if len(dets) == 0:
            cv2.imshow('Video', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        shapes = [predictor(rgb_frame, det) for det in dets]
        face_descriptors = [face_rec_model.compute_face_descriptor(rgb_frame, shape) for shape in shapes]

        if len(face_descriptors) > 0:
            face_encoding = np.array(face_descriptors[0])
            det = dets[0]
            cv2.rectangle(frame, (det.left(), det.top()), (det.right(), det.bottom()), (0, 0, 255), 2)
            cv2.putText(frame, "Face Captured!", (det.left(), det.top() - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)
            cv2.imshow('Video', frame)
            cv2.waitKey(1000)
            break

        cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()
    return face_encoding
