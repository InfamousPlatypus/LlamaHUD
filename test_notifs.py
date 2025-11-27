from Notifs import easy_notification
import sys

print("Testing notification...")
try:
    easy_notification("This is a test notification from the test script.")
    print("Notification function called successfully.")
except Exception as e:
    print(f"Notification failed with error: {e}")
