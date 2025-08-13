from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from database import start_attendance_session, stop_attendance_session, get_all_students_attendance, mark_absent_for_missing_students, get_aggregate_attendance_history
from screens.attendance_state import start_attendance, is_attendance_active

class ProfessorDashboard(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.division = None
        self.subjects = ["AI", "Research", "DevOps", "AI lab", "Full stack", "Elective", "SSD"]
        self.divisions = ["A", "B", "C", "D"]
        self.periods = [str(i) for i in range(1, 8)] + ["extra"]

        # Outer ScrollView for the whole page
        outer_scroll = ScrollView(size_hint=(1, 1))

        # Main vertical layout inside scrollview
        layout = MDBoxLayout(orientation='vertical', padding=20, spacing=15, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        header = MDLabel(text="Professor Dashboard", halign="center", theme_text_color="Primary", font_style="H4", size_hint_y=None, height=40)
        layout.add_widget(header)

        # Division dropdown
        self.division_button = MDRaisedButton(text="Select Division", size_hint=(0.9, None), height=40, pos_hint={"center_x": 0.5})
        self.division_menu = MDDropdownMenu(
            caller=self.division_button,
            items=[{"text": d, "on_release": lambda x=d: self.set_division(x)} for d in self.divisions],
            width_mult=4,
        )
        self.division_button.bind(on_release=lambda x: self.division_menu.open())
        layout.add_widget(self.division_button)

        # Subject dropdown
        self.subject_button = MDRaisedButton(text="Select Subject", size_hint=(0.9, None), height=40, pos_hint={"center_x": 0.5})
        self.subject_menu = MDDropdownMenu(
            caller=self.subject_button,
            items=[{"text": s, "on_release": lambda x=s: self.set_subject(x)} for s in self.subjects],
            width_mult=4,
        )
        self.subject_button.bind(on_release=lambda x: self.subject_menu.open())
        layout.add_widget(self.subject_button)

        # Period dropdown
        self.period_button = MDRaisedButton(text="Select Period", size_hint=(0.9, None), height=40, pos_hint={"center_x": 0.5})
        self.period_menu = MDDropdownMenu(
            caller=self.period_button,
            items=[{"text": p, "on_release": lambda x=p: self.set_period(x)} for p in self.periods],
            width_mult=4,
        )
        self.period_button.bind(on_release=lambda x: self.period_menu.open())
        layout.add_widget(self.period_button)

        # Buttons layout centered horizontally
        buttons_layout = MDBoxLayout(size_hint_y=None, height=50, spacing=20, padding=[0,0,0,0], pos_hint={"center_x": 0.5})
        self.start_button = MDRaisedButton(
            text="Start Attendance", size_hint=(None, None), size=(150, 40),
            on_release=self.start_attendance
        )
        self.stop_button = MDRaisedButton(
            text="Stop Attendance", size_hint=(None, None), size=(150, 40),
            on_release=self.stop_attendance
        )
        buttons_layout.add_widget(Widget())  # Spacer
        buttons_layout.add_widget(self.start_button)
        buttons_layout.add_widget(self.stop_button)
        buttons_layout.add_widget(Widget())  # Spacer
        layout.add_widget(buttons_layout)

        from kivymd.uix.button import MDIconButton
        refresh_button = MDIconButton(icon="refresh", pos_hint={"center_x": 0.5}, on_release=self.refresh_data)
        layout.add_widget(refresh_button)

        # Student attendance list wrapped in ScrollView with fixed height
        self.student_list = MDList()
        scroll = ScrollView(size_hint=(1, None), size=(self.width, 300))
        scroll.add_widget(self.student_list)
        layout.add_widget(scroll)

        # Aggregate attendance label wrapped in ScrollView with fixed height
        self.aggregate_label = MDLabel(text="Aggregate Attendance History:", halign="center", font_style="H6", size_hint_y=None)
        self.aggregate_label.bind(texture_size=self.aggregate_label.setter('size'))
        scroll_agg = ScrollView(size_hint=(1, None), size=(self.width, 150))
        scroll_agg.add_widget(self.aggregate_label)
        layout.add_widget(scroll_agg)

        outer_scroll.add_widget(layout)
        self.add_widget(outer_scroll)

        self.selected_subject = None
        self.selected_period = None
        self.selected_division = None

    def on_enter(self):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        username = app.logged_in_username
        from database import get_user_by_username
        user = get_user_by_username(username)
        if user and user.get("role") == "Professor":
            self.division = user.get("division")
            self.selected_division = self.division
            if self.division:
                self.division_button.text = self.division
            else:
                self.division_button.text = "Select Division"
            self.load_student_attendance()
        else:
            self.division = None
            self.division_button.text = "Select Division"
            self.student_list.clear_widgets()
            self.aggregate_label.text = "No data available."

    def set_division(self, division):
        self.selected_division = division
        self.division_button.text = division
        self.division_menu.dismiss()
        self.load_student_attendance()

    def set_subject(self, subject):
        self.selected_subject = subject
        self.subject_button.text = subject
        self.subject_menu.dismiss()

    def set_period(self, period):
        self.selected_period = period
        self.period_button.text = period
        self.period_menu.dismiss()

    def start_attendance(self, instance):
        if not self.selected_subject or not self.selected_period or not self.selected_division:
            print("Please select division, subject and period before starting attendance.")
            return
        division = self.selected_division
        topic = self.selected_subject
        period = self.selected_period

        from database import is_period_available
        if period != "extra" and not is_period_available(division, period):
            print(f"Period {period} is already taken for division {division} today.")
            return

        start_attendance_session(division, topic, period)
        start_attendance()
        print("Attendance session started!")
        self.load_student_attendance()
        # Display message that attendance is active
        self.aggregate_label.text = f"Attendance session is active for division {division}, subject {topic}, period {period}."

    def stop_attendance(self, instance):
        division = self.selected_division
        topic = self.selected_subject
        period = self.selected_period
        mark_absent_for_missing_students(division, topic, period)
        stop_attendance_session()
        print("Attendance session stopped.")
        self.load_student_attendance()
        self.aggregate_label.text = "Attendance session stopped."

    def load_student_attendance(self):
        self.student_list.clear_widgets()
        if not self.selected_division:
            return
        students = get_all_students_attendance(self.selected_division)
        for student in students:
            item_text = f"{student['roll_no']} - {student['username']}: {student['attendance_percentage']:.2f}%"
            self.student_list.add_widget(OneLineListItem(text=item_text))
        self.load_aggregate_attendance()

    def load_aggregate_attendance(self):
        if not self.selected_division:
            self.aggregate_label.text = "No data available."
            return
        aggregate = get_aggregate_attendance_history(self.selected_division)
        text_lines = []
        for record in aggregate:
            topic = record["_id"]["topic"]
            period = record["_id"]["period"]
            total = record["total"]
            attended = record["attended"]
            percentage = (attended / total) * 100 if total > 0 else 0
            text_lines.append(f"Period {period} - {topic}: {percentage:.2f}% attendance")
        self.aggregate_label.text = "\n".join(text_lines) if text_lines else "No aggregate attendance data."

    def refresh_data(self, instance):
        self.load_student_attendance()

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
