import threading
from plyer import notification

def show_notification(title, message):
    """Display a Windows notification using plyer."""
    try:
        notification.notify(
            title=title,
            message=message,
            timeout=5  # Duration in seconds
        )
    except Exception as e:
        print(f"Error displaying notification: {e}")

def easy_notification(message):
    """Run the notification in a separate thread."""
    threading.Thread(target=show_notification, args=("LlamaHUD", message)).start()

if __name__ == "__main__":
    print("LlamaHUD Notification Module")
    StartupNotification = "This is a test notification from LlamaHUD."
    easy_notification(StartupNotification)
    print("Notification sent.")