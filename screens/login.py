from kivy.uix.screenmanager import Screen
from database import get_user_by_username
from kivymd.app import MDApp

class LoginScreen(Screen):
    def login_user(self):
        username = self.ids.username_input.text
        password = self.ids.password_input.text

        if username == "admin" and password == "admin":
            self.manager.current = "admin_dashboard"
            return

        user = get_user_by_username(username)
        if user and user['password'] == password:
            print("Login successful!")
            # Set logged in username in app instance
            app = MDApp.get_running_app()
            app.logged_in_username = username
            # Proceed to the appropriate dashboard screen
            if user['role'] == 'Student':
                self.manager.current = 'student_dashboard'
            elif user['role'] == 'Professor':
                self.manager.current = 'professor_dashboard'
        else:
            print("Invalid credentials.")

    def go_to_analytics(self):
        self.manager.current = "analytics_dashboard"
