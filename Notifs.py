from windows_toasts import InteractableWindowsToaster, Toast, ToastImageAndText2, ToastInputTextBox, ToastButton, ToastActivatedEventArgs
import socket
import threading
import sys

# Define a custom AUMID
AUMID = "LlamaHUD.App"

def send_reply_to_hud(reply_text):
    """Send the reply text to the running HUD instance via IPC"""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('127.0.0.1', 12345))
        client_socket.sendall(reply_text.encode('utf-8'))
        client_socket.close()
        print(f"Sent reply: {reply_text}")
    except Exception as e:
        print(f"Failed to send reply: {e}")

def show_interactive_notification(title: str, message: str):
    """Show an interactive toast with text input"""
    try:
        toaster = InteractableWindowsToaster(AUMID)
        
        # Create toast
        toast = ToastImageAndText2()
        toast.SetHeadline(title)
        toast.SetBody(message)
        
        # Add input box
        text_input = ToastInputTextBox("reply_box", "Type a reply...", "Reply")
        toast.AddInput(text_input)
        
        # Add send button
        send_button = ToastButton("Send", "send_action")
        toast.AddAction(send_button)
        
        # Define callback
        def handle_activation(args: ToastActivatedEventArgs):
            if args.inputs and 'reply_box' in args.inputs:
                reply = args.inputs['reply_box']
                # Send to HUD in a separate thread to avoid blocking
                threading.Thread(target=send_reply_to_hud, args=(reply,)).start()
        
        toast.on_activated = handle_activation
        
        toaster.show_toast(toast)
        print("Toast shown successfully.")
        
    except Exception as e:
        print(f"Toast failed: {e}. Fallback to MessageBox.")
        # Fallback
        import subprocess
        safe_message = message.replace("'", "''")
        safe_title = title.replace("'", "''")
        ps_script = f"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('{safe_message}', '{safe_title}')"
        subprocess.run(["powershell", "-Command", ps_script], check=False)

def easy_notification(message: str):
    """Convenient function to send a notification with a default title."""
    show_interactive_notification("LlamaHUD", message)

if __name__ == "__main__":
    # Test
    easy_notification("Test interactive notification. Type a reply and click Send.")
    # Keep alive for a moment to receive callback if testing
    import time
    time.sleep(10)