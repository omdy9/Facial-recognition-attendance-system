import cv2
import face_recognition
from kivymd.uix.screen import MDScreen
from kivymd.toast import toast
from database import get_user_by_username, mark_attendance_in_db, is_attendance_allowed, get_active_session
from face_utils import capture_face_encoding
from gps_utils import get_current_location
from geopy.distance import geodesic
from kivy.clock import Clock
# Removed unused import get_professor_location


class AttendanceScreen(MDScreen):
    def on_pre_enter(self):
        self.ids.timer_label.text = "Time left: -- seconds"
        self.ids.gps_label.text = "Checking location..."
        self.remaining_time = 60
        self.update_timer_label(0)
        self.timer_event = Clock.schedule_interval(self.update_timer_label, 1)

        if not is_attendance_allowed():
            self.ids.timer_label.text = "Attendance window closed"
            self.timer_event.cancel()
            self.ids.mark_attendance_button.disabled = True
        else:
            self.ids.mark_attendance_button.disabled = False

    def update_timer_label(self, dt):
        if self.remaining_time > 0:
            self.ids.timer_label.text = f"Time left: {self.remaining_time} seconds"
            self.remaining_time -= 1
        else:
            self.ids.timer_label.text = "Attendance window closed"
            self.timer_event.cancel()
            self.ids.mark_attendance_button.disabled = True

    def mark_attendance(self):
        username = self.manager.get_screen("login").ids.username.text
        user = get_user_by_username(username)

        if not user:
            toast("User not found.")
            return

        if not is_attendance_allowed():
            toast("Attendance session is not active.")
            return

        saved_encoding = user.get("face_encoding")
        if not saved_encoding:
            toast("No face encoding found for user.")
            return

        # Capture new face image for comparison
        video_capture = cv2.VideoCapture(0)
        ret, frame = video_capture.read()

        if not ret:
            toast("Failed to capture image.")
            video_capture.release()
            return

        face_locations = face_recognition.face_locations(frame)
        if len(face_locations) == 0:
            toast("No face detected. Please try again.")
            video_capture.release()
            return

        new_face_encoding = face_recognition.face_encodings(frame, face_locations)[0]
        video_capture.release()

        # Compare the captured face with the stored encoding
        face_distance = face_recognition.face_distance([saved_encoding], new_face_encoding)

        if face_distance[0] < 0.6:  # Adjust threshold as needed
            session = get_active_session()
            if session:
                mark_attendance_in_db(
                    username,
                    "attended",
                    None,
                    user.get("roll_no"),
                    user.get("division"),
                    session.get("topic"),
                    session.get("period"),
                )
                toast("Attendance marked successfully!")
            else:
                toast("No active attendance session.")
        else:
            toast("Face not recognized.")

    def on_leave(self):
        if self.timer_event:
            self.timer_event.cancel()
