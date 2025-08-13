from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDRaisedButton
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.screenmanager import Screen
import cv2
import base64

from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDRaisedButton
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.screenmanager import Screen
import cv2
import base64

class CameraClick(BoxLayout):
    def __init__(self, **kwargs):
        capture_callback = kwargs.pop('capture_callback', None)
        super().__init__(**kwargs)
        self.capture_callback = capture_callback
        self.orientation = 'vertical'
        self.camera = Image()
        self.add_widget(self.camera)
        self.capture_button = MDRaisedButton(text="Capture Face", size_hint=(1, 0.2))
        self.capture_button.bind(on_release=self.capture_face)
        self.add_widget(self.capture_button)
        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update, 1.0 / 30.0)

    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            buf = cv2.flip(frame, 0).tobytes()
            image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.camera.texture = image_texture
            self.current_frame = frame

    def capture_face(self, *args):
        if not hasattr(self, 'current_frame'):
            print("No frame available to capture. Please wait for the camera to initialize.")
            return
        _, buffer = cv2.imencode('.jpg', self.current_frame)
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')
        if self.capture_callback:
            self.capture_callback(None, jpg_as_text)

class FaceCaptureScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.face_encoding = None
        self.face_image_base64 = None

        self.layout = BoxLayout(orientation='vertical')

        self.camera_widget = CameraClick(capture_callback=self.on_face_captured)
        self.layout.add_widget(self.camera_widget)

        self.done_button = MDRaisedButton(text="Done", size_hint=(1, 0.1))
        self.done_button.bind(on_release=self.on_done)
        self.layout.add_widget(self.done_button)

        self.clear_widgets()
        self.add_widget(self.layout)

    def on_face_captured(self, face_encoding, face_image_base64):
        self.face_encoding = face_encoding
        self.face_image_base64 = face_image_base64
        print("Face captured and encoded successfully!")

    def on_done(self, instance):
        register_screen = self.manager.get_screen('register')
        register_screen.face_encoding = self.face_encoding
        register_screen.face_image_base64 = self.face_image_base64
        self.manager.current = 'register'
