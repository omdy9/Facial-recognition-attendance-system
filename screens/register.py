import face_recognition
import base64  # Added to handle image encoding
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import cv2

from database import save_user  # Your database saving function


class CameraClick(BoxLayout):
    def __init__(self, capture_callback, camera_index=0, **kwargs):
        super().__init__(**kwargs)
        self.capture_callback = capture_callback
        self.orientation = 'vertical'
        self.camera = Image()
        self.add_widget(self.camera)
        self.capture_button = MDRaisedButton(text="Capture Face", size_hint=(1, 0.2))
        self.capture_button.bind(on_release=self.capture_face)
        self.add_widget(self.capture_button)
        self.capture = cv2.VideoCapture(camera_index)
        if not self.capture.isOpened():
            print(f"Error: Unable to open camera with index {camera_index}")
        Clock.schedule_interval(self.update, 1.0 / 30.0)

    def update(self, dt):
        if not self.capture.isOpened():
            return
        ret, frame = self.capture.read()
        if ret:
            # Convert image to texture
            buf = cv2.flip(frame, 0).tobytes()
            image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.camera.texture = image_texture
            self.current_frame = frame

    def capture_face(self, *args):
        if not hasattr(self, 'current_frame'):
            print("No frame available to capture. Please wait for the camera to initialize.")
            return
        # Capture the current frame and convert to base64
        _, buffer = cv2.imencode('.jpg', self.current_frame)
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')

        # Compute face encoding
        rgb_frame = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb_frame)
        if len(encodings) > 0:
            face_encoding = encodings[0]
        else:
            print("No face detected. Please try again.")
            return

        self.capture_callback(face_encoding, jpg_as_text)


class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.menu = None
        self.selected_role = None
        self.face_encoding = None
        self.face_image_base64 = None
        self.create_role_menu()

    def create_role_menu(self):
        menu_items = [
            {"text": "Student", "on_release": lambda x="Student": self.set_role(x)},
            {"text": "Professor", "on_release": lambda x="Professor": self.set_role(x)},
        ]
        self.menu = MDDropdownMenu(
            items=menu_items,
            width_mult=4,
        )

    def open_role_menu(self):
        if not self.menu.caller:
            self.menu.caller = self.ids.role_button
        self.menu.open()

    def set_role(self, role_text):
        self.selected_role = role_text
        self.menu.dismiss()
        self.ids.role_button.text = role_text
        self.update_role_dependent_fields()

    def update_role_dependent_fields(self):
        if self.selected_role == "Professor":
            self.ids.rollno_input.disabled = True
            self.ids.division_input.disabled = True
            self.ids.capture_face_button.disabled = True
            if hasattr(self, 'camera_widget') and self.camera_widget.parent:
                self.ids.camera_box.clear_widgets()
                self.ids.camera_box.height = 0
        else:
            self.ids.rollno_input.disabled = False
            self.ids.division_input.disabled = False
            self.ids.capture_face_button.disabled = False

    def open_camera(self):
        if hasattr(self, 'camera_widget') and self.camera_widget.parent:
            return
        self.camera_widget = CameraClick(self.on_face_captured)
        self.ids.camera_box.clear_widgets()
        self.ids.camera_box.add_widget(self.camera_widget)
        self.ids.camera_box.height = 300

    def on_face_captured(self, face_encoding, face_image_base64):
        self.face_encoding = face_encoding
        self.face_image_base64 = face_image_base64
        print("Face captured and encoded successfully!")

        def close_dialog(obj):
            self.dialog.dismiss()
            if hasattr(self, 'camera_widget') and self.camera_widget.parent:
                self.ids.camera_box.clear_widgets()
                self.ids.camera_box.height = 0

        self.dialog = MDDialog(
            text="Face captured successfully!",
            buttons=[
                MDFlatButton(text="Done", on_release=close_dialog)
            ],
        )
        self.dialog.open()

    def load_kv_ui(self):
        from kivy.lang import Builder
        self.clear_widgets()
        try:
            widget = Builder.load_file('screens/register.kv')
            self.add_widget(widget)
        except Exception as e:
            print(f"Error loading register.kv: {e}")

    def register_user(self):
        username = self.ids.username_input.text.strip()
        password = self.ids.password_input.text.strip()
        roll_no = self.ids.rollno_input.text.strip()
        division = self.ids.division_input.text.strip()
        role = self.selected_role

        if role != "Professor":
            if not username or not password or not roll_no or not division or not role:
                print("Please fill all fields and select role.")
                return
            import numpy as np
            if self.face_encoding is None or self.face_image_base64 is None or (isinstance(self.face_encoding, np.ndarray) and self.face_encoding.size == 0):
                print("Please capture a face image first.")
                return

            # Process face encoding for student
            import numpy as np
            import cv2
            img_data = base64.b64decode(self.face_image_base64)
            nparr = np.frombuffer(img_data, np.uint8)
            img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            rgb_img = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
            encodings = face_recognition.face_encodings(rgb_img)
            face_encoding_list = encodings[0].tolist() if len(encodings) > 0 else None

        else:
            # For professor: skip face processing
            if not username or not password or not role:
                print("Please fill all required fields and select role.")
                return
            roll_no = None
            division = None
            self.face_image_base64 = None
            face_encoding_list = None

        print(f"Computed face encoding list: {face_encoding_list}")

        # Save user to MongoDB
        result = save_user(username, password, role, face_encoding_list, self.face_image_base64, roll_no, division)

        if result:
            print("User registered successfully!")
            if role != "Professor" and self.face_image_base64:
                import io
                from kivy.core.image import Image as CoreImage
                img_data = base64.b64decode(self.face_image_base64)
                buf = io.BytesIO(img_data)
                core_image = CoreImage(buf, ext="jpg")
                self.ids.face_preview.texture = core_image.texture
            self.manager.current = "login"
        else:
            print("Username already exists.")
