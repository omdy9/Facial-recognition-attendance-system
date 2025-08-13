from datetime import datetime, timedelta
from database import get_active_session

def is_attendance_active():
    active_session = get_active_session()
    if not active_session:
        print("No active session found in DB.")
        return False
    start_time = active_session.get("start_time")
    if not start_time:
        print("Active session has no start_time.")
        return False
    # Convert start_time to datetime if needed
    try:
        from bson import ObjectId, datetime as bson_datetime
        if hasattr(start_time, 'as_datetime'):
            start_time = start_time.as_datetime()
    except ImportError:
        pass
    now = datetime.utcnow()
    print(f"Current UTC time: {now}, Session start_time: {start_time}")
    # Attendance allowed for 1 minute from start_time
    return now < start_time + timedelta(minutes=1)

def start_attendance():
    # This function is kept for compatibility but actual start time is stored in DB
    pass
