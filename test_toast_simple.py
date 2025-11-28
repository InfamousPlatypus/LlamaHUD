from windows_toasts import InteractableWindowsToaster, Toast, ToastInputTextBox, ToastButton

try:
    print("Creating toaster...")
    toaster = InteractableWindowsToaster("TestApp")
    
    print("Creating toast...")
    toast = Toast()
    toast.text_fields = ["Title", "Body"]
    
    print("Adding input...")
    text_input = ToastInputTextBox("reply", "Type here", "Reply")
    toast.AddInput(text_input)
    
    print("Adding button...")
    btn = ToastButton("Send", "send")
    toast.AddAction(btn)
    
    print("Showing toast...")
    toaster.show_toast(toast)
    print("Success!")
except Exception as e:
    print(f"Error: {e}")
