from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import StringProperty
from pymongo import MongoClient
from datetime import datetime

from database import delete_user, mark_attendance

client = MongoClient(
    "mongodb+srv://omdhuri1:saeemeena@cluster0.4duecxr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)
db = client["attendance_db"]
users_col = db["users"]
attendance_col = db["attendance"]
sessions_col = db["sessions"]

class AdminDashboard(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.selected_user_type = "Student"
        self.selected_user = None

        main_layout = MDBoxLayout(orientation='vertical', padding=20, spacing=20)

        header = MDLabel(text="Admin Dashboard", halign="center", theme_text_color="Primary", font_style="H4", size_hint_y=None, height=40)
        main_layout.add_widget(header)

        # User type selection spinner
        self.user_type_spinner = Spinner(
            text='Student',
            values=('Student', 'Professor'),
            size_hint=(None, None),
            size=(150, 44),
            pos_hint={'center_x': 0.5}
        )
        self.user_type_spinner.bind(text=self.on_user_type_select)
        main_layout.add_widget(self.user_type_spinner)

        # User list
        self.user_list = MDList()
        user_list_scroll = ScrollView(size_hint=(1, None), size=(self.width, 300))
        user_list_scroll.add_widget(self.user_list)
        main_layout.add_widget(user_list_scroll)

        # Buttons for user management
        buttons_layout = MDBoxLayout(size_hint_y=None, height=50, spacing=20)
        self.add_user_button = MDRaisedButton(text="Add User", on_release=self.show_add_user_popup)
        self.edit_user_button = MDRaisedButton(text="Edit User", on_release=self.show_edit_user_popup)
        self.delete_user_button = MDRaisedButton(text="Delete User", on_release=self.delete_selected_user)
        buttons_layout.add_widget(self.add_user_button)
        buttons_layout.add_widget(self.edit_user_button)
        buttons_layout.add_widget(self.delete_user_button)
        main_layout.add_widget(buttons_layout)

        # Attendance modification section
        attendance_label = MDLabel(text="Modify Attendance", halign="center", font_style="H6", size_hint_y=None, height=30)
        main_layout.add_widget(attendance_label)

        attendance_layout = GridLayout(cols=2, spacing=10, size_hint_y=None)
        attendance_layout.bind(minimum_height=attendance_layout.setter('height'))

        self.attendance_user_spinner = Spinner(
            text='Select User',
            values=[],
            size_hint=(None, None),
            size=(200, 44),
            pos_hint={'center_x': 0.5}
        )
        attendance_layout.add_widget(MDLabel(text="User:", size_hint_y=None, height=30))
        attendance_layout.add_widget(self.attendance_user_spinner)

        self.attendance_date_field = MDTextField(
            hint_text="Date (YYYY-MM-DD)",
            size_hint=(None, None),
            size=(200, 44),
            pos_hint={'center_x': 0.5}
        )
        attendance_layout.add_widget(MDLabel(text="Date:", size_hint_y=None, height=30))
        attendance_layout.add_widget(self.attendance_date_field)

        self.attendance_period_spinner = Spinner(
            text='Select Period',
            values=[str(i) for i in range(1, 8)] + ['extra'],
            size_hint=(None, None),
            size=(200, 44),
            pos_hint={'center_x': 0.5}
        )
        attendance_layout.add_widget(MDLabel(text="Period:", size_hint_y=None, height=30))
        attendance_layout.add_widget(self.attendance_period_spinner)

        self.attendance_status_spinner = Spinner(
            text='Present',
            values=['Present', 'Absent'],
            size_hint=(None, None),
            size=(200, 44),
            pos_hint={'center_x': 0.5}
        )
        attendance_layout.add_widget(MDLabel(text="Status:", size_hint_y=None, height=30))
        attendance_layout.add_widget(self.attendance_status_spinner)

        self.modify_attendance_button = MDRaisedButton(text="Modify Attendance", size_hint=(None, None), size=(200, 44), pos_hint={'center_x': 0.5})
        self.modify_attendance_button.bind(on_release=self.modify_attendance)
        attendance_layout.add_widget(Widget())
        attendance_layout.add_widget(self.modify_attendance_button)

        main_layout.add_widget(attendance_layout)

        self.add_widget(main_layout)

        self.load_users()

    def on_user_type_select(self, spinner, text):
        self.selected_user_type = text
        self.load_users()

    def load_users(self):
        self.user_list.clear_widgets()
        users = list(users_col.find({"role": self.selected_user_type.lower()}))
        self.user_list_items = []
        self.attendance_user_spinner.values = []
        for user in users:
            username = user.get('username', '')
            full_name = user.get('full_name', '')
            division = user.get('division', '')
            attendance_percentage = self.calculate_attendance_percentage(username)
            item_text = f"{username} - {full_name} - Division: {division} - Attendance: {attendance_percentage:.2f}%"
            item = OneLineListItem(text=item_text, on_release=lambda x, u=user: self.select_user(u))
            self.user_list.add_widget(item)
            self.user_list_items.append(item)
            self.attendance_user_spinner.values.append(username)

    def calculate_attendance_percentage(self, username):
        total_sessions = attendance_col.count_documents({"username": username})
        attended_sessions = attendance_col.count_documents({"username": username, "status": "attended"})
        if total_sessions == 0:
            return 0.0
        return (attended_sessions / total_sessions) * 100

    def select_user(self, user):
        self.selected_user = user
        self.show_user_options_popup(user)

    def show_user_options_popup(self, user):
        content = MDBoxLayout(orientation='vertical', spacing=10, padding=10)
        attendance_btn = MDRaisedButton(text="Modify Attendance", size_hint_y=None, height=40)
        attendance_btn.bind(on_release=lambda x: self.show_modify_attendance_popup(user))
        period_btn = MDRaisedButton(text="Change Period", size_hint_y=None, height=40)
        period_btn.bind(on_release=lambda x: self.show_change_period_popup(user))
        delete_btn = MDRaisedButton(text="Delete User", size_hint_y=None, height=40)
        delete_btn.bind(on_release=lambda x: self.confirm_delete_user(user))

        content.add_widget(attendance_btn)
        content.add_widget(period_btn)
        content.add_widget(delete_btn)

        self.popup = Popup(title=f"Options for {user['username']}", content=content, size_hint=(0.6, 0.4))
        self.popup.open()

    def show_modify_attendance_popup(self, user):
        self.popup.dismiss()
        # Implementation for modifying attendance (to be implemented)
        pass

    def show_change_period_popup(self, user):
        self.popup.dismiss()
        # Implementation for changing period (to be implemented)
        pass

    def confirm_delete_user(self, user):
        self.popup.dismiss()
        delete_user(user['username'])
        self.load_users()

    def show_add_user_popup(self, instance):
        # Implementation for adding user (to be implemented)
        pass

    def show_edit_user_popup(self, instance):
        # Implementation for editing user (to be implemented)
        pass

    def delete_selected_user(self, instance):
        if not self.selected_user:
            return
        delete_user(self.selected_user['username'])
        self.load_users()

    def modify_attendance(self, instance):
        username = self.attendance_user_spinner.text
        date_str = self.attendance_date_field.text
        period = self.attendance_period_spinner.text
        status = self.attendance_status_spinner.text.lower()

        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            # Invalid date format
            return

        mark_attendance(username, date_obj, period, status)
        # Reload data to reflect changes
        self.load_users()
