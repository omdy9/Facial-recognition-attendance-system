from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.list import MDList, OneLineListItem
from kivy.uix.scrollview import ScrollView
from database import get_student_attendance_percentage, mark_attendance_in_db, get_user_by_username, get_active_session, is_attendance_allowed, get_student_attendance_history
from datetime import datetime
import face_recognition
import cv2
from kivymd.app import MDApp
from face_utils import capture_face_encoding

class StudentDashboard(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = MDBoxLayout(orientation='vertical', padding=20, spacing=20)

        header_layout = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=40, padding=(0,0,0,0))
        header = MDLabel(text="Student Dashboard", halign="center", theme_text_color="Primary", font_style="H4")
        header_layout.add_widget(header)

        from kivymd.uix.button import MDIconButton
        refresh_button = MDIconButton(icon="refresh", pos_hint={"center_y": 0.5}, on_release=self.refresh_data)
        header_layout.add_widget(refresh_button)

        layout.add_widget(header_layout)

        self.attendance_label = MDLabel(text="Attendance Percentage: Loading...", halign="center", font_style="H5")
        layout.add_widget(self.attendance_label)

        self.message_label = MDLabel(text="", halign="center", theme_text_color="Error", font_style="Subtitle1")
        layout.add_widget(self.message_label)

        self.mark_attendance_button = MDRaisedButton(
            text="Mark Attendance", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.5},
            on_release=self.mark_attendance
        )
        layout.add_widget(self.mark_attendance_button)

        # Attendance history list wrapped in ScrollView with fixed height
        scroll = ScrollView(size_hint=(1, None), size=(self.width, 300))
        self.history_list = MDList()
        scroll.add_widget(self.history_list)
        layout.add_widget(scroll)

        self.add_widget(layout)

    def on_enter(self):
        self.update_attendance_percentage()
        self.load_attendance_history()
        # Display active session message if session is active and matches user's division
        app = MDApp.get_running_app()
        username = app.logged_in_username
        user = get_user_by_username(username)
        session = get_active_session()
        if session and user and user.get("division") == session.get("division"):
            self.message_label.text = f"Attendance session is active for division {session.get('division')}."
        else:
            self.message_label.text = ""

    def refresh_data(self, instance):
        self.update_attendance_percentage()
        self.load_attendance_history()

    def update_attendance_percentage(self):
        app = MDApp.get_running_app()
        username = app.logged_in_username
        percentage = get_student_attendance_percentage(username)
        self.attendance_label.text = f"Attendance Percentage: {percentage:.2f}%"

    def load_attendance_history(self):
        self.history_list.clear_widgets()
        app = MDApp.get_running_app()
        username = app.logged_in_username
        history = get_student_attendance_history(username)
        for record in history:
            status = record.get("status", "unknown")
            topic = record.get("topic", "")
            period = record.get("period", "")
            timestamp = record.get("timestamp")
            timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S") if timestamp else ""
            item_text = f"{timestamp_str} - {topic} (Period {period}): {status}"
            self.history_list.add_widget(OneLineListItem(text=item_text))

    def mark_attendance(self, instance):
        app = MDApp.get_running_app()
        username = app.logged_in_username

        if not is_attendance_allowed():
            self.message_label.text = "Attendance session is not active."
            return

        user = get_user_by_username(username)
        if not user:
            self.message_label.text = "User not found."
            return

        saved_encoding = user.get("face_encoding")
        print(f"Retrieved face encoding: {saved_encoding}")
        if not saved_encoding:
            self.message_label.text = "No face encoding found for user."
            return


        # Capture face encoding using face_utils function
        captured_encoding = capture_face_encoding()
        if captured_encoding is None:
            self.message_label.text = "No face detected during attendance marking."
            return

        matches = face_recognition.compare_faces([saved_encoding], captured_encoding)

        if matches[0]:
            session = get_active_session()
            if session:
                division = user.get("division")
                if division != session.get("division"):
                    self.message_label.text = f"Attendance session is active for division {session.get('division')}. You cannot mark attendance for division {division}."
                    return
                timestamp = datetime.now()
                roll_no = user.get("roll_no")
                topic = session.get("topic")
                period = session.get("period")

                mark_attendance_in_db(username, "attended", timestamp, roll_no, division, topic, period)
                self.message_label.text = f"Attendance session is active for division {division}. Attendance marked successfully!"
                self.update_attendance_percentage()
                self.load_attendance_history()
            else:
                # No active session, mark absent with last session details if available
                last_session = get_active_session()  # Assuming this returns last session or None
                if last_session:
                    timestamp = datetime.now()
                    roll_no = user.get("roll_no")
                    division = user.get("division")
                    topic = last_session.get("topic")
                    period = last_session.get("period")
                    mark_attendance_in_db(username, "absent", timestamp, roll_no, division, topic, period)
                    self.message_label.text = f"Session ended. Marked absent for topic '{topic}', period {period}."
                    self.update_attendance_percentage()
                    self.load_attendance_history()
                else:
                    self.message_label.text = "No active attendance session."
        else:
            self.message_label.text = "Face does not match. Please try again."
            # Do not close app, allow retry

        # No cap.release() here since capture_face_encoding handles video release
    def add_logout_button(self, screen_manager):
        from kivymd.uix.button import MDRaisedButton

        def logout_callback(instance):
            # Clear any user session or authentication data here if needed
            # Redirect to login screen
            screen_manager.current = 'login'

        logout_button = MDRaisedButton(
            text="Logout",
            size_hint=(None, None),
            size=(100, 40),
            pos_hint={"center_x": 0.5},
            on_release=logout_callback
        )
        return logout_button
