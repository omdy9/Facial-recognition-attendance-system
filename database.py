from pymongo import MongoClient
import face_recognition

# MongoDB connection string
client = MongoClient(
"mongodb+srv://omdhuri1:saeemeena@cluster0.4duecxr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["attendance_db"]
users_col = db["users"]
attendance_col = db["attendance"]
sessions_col = db["sessions"] # Collection for professor's attendance session

# Function to get user by username
def get_user_by_username(username):
    return users_col.find_one({"username": username})

# Function to save user data to the database
def save_user(username, password, role, face_encoding, face_image_base64, roll_no, division):
    user = users_col.find_one({"username": username})
    if user:
        return False # Username already exists
    new_user = {
        "username": username,
        "password": password,
        "role": role,
        "face_encoding": face_encoding,
        "face_image_base64": face_image_base64,
        "roll_no": roll_no,
        "division": division
    }
    users_col.insert_one(new_user)
    return True

# Function to encode face from an image file
def encode_face(image_path):
    image = face_recognition.load_image_file(image_path)
    face_encodings = face_recognition.face_encodings(image)
    if len(face_encodings) > 0:
        return face_encodings[0]
    return None

# Function to mark attendance in the database
def mark_attendance_in_db(username, status, timestamp, roll_no, division, topic, period):
    attendance = {
        "username": username,
        "status": status,
        "timestamp": timestamp,
        "roll_no": roll_no,
        "division": division,
        "topic": topic,
        "period": period
    }
    attendance_col.insert_one(attendance)

# Function to get a student's attendance percentage
def get_student_attendance_percentage(username):
    user = users_col.find_one({"username": username})
    if user:
        roll_no = user.get("roll_no")
        division = user.get("division")
        total_classes = attendance_col.count_documents({"roll_no": roll_no, "division": division})
        attended_classes = attendance_col.count_documents(
            {"roll_no": roll_no, "division": division, "status": "attended"}
        )
        if total_classes == 0:
            return 0
        return (attended_classes / total_classes) * 100
    return 0

# Function to start a professor's attendance session
from datetime import datetime, timedelta

from datetime import datetime, time

def start_attendance_session(division, topic, period):
    # Set existing active sessions to inactive
    sessions_col.update_many({"status": "active"}, {"$set": {"status": "inactive"}})

    session = {
        "division": division,
        "topic": topic,
        "period": period,
        "status": "active",
        "start_time": datetime.utcnow() # Set start_time when session starts
    }
    sessions_col.insert_one(session)

# Function to check if a period is available for a division on the current day
def is_period_available(division, period):
    now = datetime.utcnow()
    start_of_day = datetime.combine(now.date(), time(6, 0)) # 6 AM today UTC
    end_of_day = start_of_day + timedelta(days=1)

    # Count attendance sessions for the division and period between 6 AM today and 6 AM next day
    count = sessions_col.count_documents({
        "division": division,
        "period": period,
        "start_time": {"$gte": start_of_day, "$lt": end_of_day},
        "status": "active"
    })
    return count == 0

# Function to get aggregate attendance history filtered by division and date
def get_aggregate_attendance_history(division):
    now = datetime.utcnow()
    start_of_day = datetime.combine(now.date(), time(6, 0)) # 6 AM today UTC
    end_of_day = start_of_day + timedelta(days=1)

    pipeline = [
        {"$match": {
            "division": division,
            "timestamp": {"$gte": start_of_day, "$lt": end_of_day}
        }},
        {"$group": {
            "_id": {"topic": "$topic", "period": "$period"},
            "total": {"$sum": 1},
            "attended": {"$sum": {"$cond": [{"$eq": ["$status", "attended"]}, 1, 0]}}
        }},
        {"$sort": {"_id.period": 1}}
    ]
    result = list(attendance_col.aggregate(pipeline))
    return result

# Function to stop the active attendance session
def stop_attendance_session():
    sessions_col.update_one({"status": "active"}, {"$set": {"status": "inactive"}})

# Function to get the active attendance session
def get_active_session():
    return sessions_col.find_one({"status": "active"})

# Function to check if attendance is allowed (active session and timer)
from screens.attendance_state import is_attendance_active

def is_attendance_allowed():
    active_session = get_active_session()
    return active_session is not None and is_attendance_active()

# Placeholder for get_professor_location function
def get_professor_location():
    # This function can be implemented to retrieve professor's location if needed
    return None

# Function to get all students with their attendance percentages
def get_all_students_attendance(division):
    students = list(users_col.find({"role": "Student", "division": division}))
    result = []
    for student in students:
        roll_no = student.get("roll_no")
        total_classes = attendance_col.count_documents({"roll_no": roll_no, "division": division})
        attended_classes = attendance_col.count_documents(
            {"roll_no": roll_no, "division": division, "status": "attended"}
        )
        percentage = (attended_classes / total_classes) * 100 if total_classes > 0 else 0
        result.append({
            "username": student.get("username"),
            "roll_no": roll_no,
            "attendance_percentage": percentage
        })
    return result

# Function to get personal attendance history for a student
def get_student_attendance_history(username):
    user = users_col.find_one({"username": username})
    if not user:
        return []
    roll_no = user.get("roll_no")
    division = user.get("division")
    history = list(attendance_col.find({"roll_no": roll_no, "division": division}).sort("timestamp", -1))
    return history

# Function to get aggregate attendance history for a division
def get_aggregate_attendance_history(division):
    pipeline = [
        {"$match": {"division": division}},
        {"$group": {
            "_id": {"topic": "$topic", "period": "$period"},
            "total": {"$sum": 1},
            "attended": {"$sum": {"$cond": [{"$eq": ["$status", "attended"]}, 1, 0]}}
        }},
        {"$sort": {"_id.period": 1}}
    ]
    result = list(attendance_col.aggregate(pipeline))
    return result

# Function to mark absent for students who did not mark attendance before session stopped
def mark_absent_for_missing_students(division, topic, period):
    students = list(users_col.find({"role": "Student", "division": division}))
    for student in students:
        username = student.get("username")
        roll_no = student.get("roll_no")
        attendance_record = attendance_col.find_one({
            "username": username,
            "topic": topic,
            "period": period,
            "division": division
        })
        if not attendance_record:
            # Mark absent
            attendance_col.insert_one({
                "username": username,
                "status": "absent",
                "timestamp": datetime.utcnow(),
                "roll_no": roll_no,
                "division": division,
                "topic": topic,
                "period": period
            })

# Additional functions for admin panel

def get_all_users(role):
    return list(users_col.find({"role": role}))

def add_user(user_data):
    users_col.insert_one(user_data)
    return True

def update_user(username, update_data):
    result = users_col.update_one({"username": username}, {"$set": update_data})
    return result.modified_count > 0

def delete_user(username):
    result = users_col.delete_one({"username": username})
    return result.deleted_count > 0

def get_user_attendance(username):
    return list(attendance_col.find({"username": username}))

def mark_attendance(username, date_obj, period, status):
    date_str = date_obj.strftime("%Y-%m-%d")
    result = attendance_col.update_one(
        {"username": username, "date": date_str, "period": period},
        {"$set": {"status": status}},
        upsert=True
    )
    return result.acknowledged

def change_user_division(username, new_division):
    result = users_col.update_one({"username": username}, {"$set": {"division": new_division}})
    return result.modified_count > 0

def change_user_period(username, new_period):
    result = users_col.update_one({"username": username}, {"$set": {"period": new_period}})
    return result.modified_count > 0
