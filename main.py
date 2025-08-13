from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivy.properties import StringProperty

from screens.login import LoginScreen
from screens.register import RegisterScreen
from screens.student_dashboard import StudentDashboard
from screens.professor_dashboard import ProfessorDashboard
from screens.admin_dashboard import AdminDashboard
#from screens.analytics_dashboard import AnalyticsDashboard

class MainScreenManager(ScreenManager):
    pass

class AttendanceApp(MDApp):
    logged_in_username = StringProperty('')

    def build(self):
        self.title = "Face Attendance App"
        self.theme_cls.primary_palette = "Blue"
        Builder.load_file("screens/login.kv")
        Builder.load_file("screens/register.kv")
        Builder.load_file("screens/student_dashboard.kv")
        Builder.load_file("screens/professor_dashboard.kv")
        Builder.load_file("screens/admin_dashboard.kv")
        # Builder.load_file("screens/analytics_dashboard.kv")

        sm = MainScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(RegisterScreen(name="register"))
        sm.add_widget(StudentDashboard(name="student_dashboard"))
        sm.add_widget(ProfessorDashboard(name="professor_dashboard"))
        sm.add_widget(AdminDashboard(name="admin_dashboard"))
        # sm.add_widget(AnalyticsDashboard(name="analytics_dashboard"))
        return sm

if __name__ == '__main__':
    AttendanceApp().run()
