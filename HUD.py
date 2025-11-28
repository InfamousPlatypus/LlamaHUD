import wx
import wx.adv
import LLMs
import threading
import socket
import os
from Notifs import easy_notification
from CommandParser import CommandParser


class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame):
        super().__init__()
        self.frame = frame
        
        # Load custom icon if available
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "util", "LlamaHUD_Logo.png")
        if os.path.exists(icon_path):
            icon = wx.Icon(icon_path, wx.BITMAP_TYPE_PNG)
            self.SetIcon(icon, "LlamaHUD")
            # Also set the frame icon
            frame.SetIcon(icon)
        else:
            self.SetIcon(wx.Icon(wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_OTHER, (16, 16))), "LlamaHUD")
            
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DCLICK, self.OnLeftDClick)
    
    def CreatePopupMenu(self):
        menu = wx.Menu()
        show_item = menu.Append(wx.ID_ANY, "Show Window")
        menu.Bind(wx.EVT_MENU, self.OnShow, show_item)
        menu.AppendSeparator()
        exit_item = menu.Append(wx.ID_EXIT, "Exit")
        menu.Bind(wx.EVT_MENU, self.OnExit, exit_item)
        return menu
    
    def OnLeftDClick(self, event):
        self.frame.Show()
        self.frame.Restore()
    
    def OnShow(self, event):
        self.frame.Show()
        self.frame.Restore()
    
    def OnExit(self, event):
        wx.CallAfter(self.frame.Close)


class IPCServer:
    def __init__(self, frame, port=12345):
        self.frame = frame
        self.port = port
        self.running = False
        self.server_socket = None
        self.thread = None
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()
    
    def stop(self):
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
    
    def _run_server(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('127.0.0.1', self.port))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1.0)
            
            while self.running:
                try:
                    client_socket, addr = self.server_socket.accept()
                    data = client_socket.recv(4096).decode('utf-8')
                    client_socket.close()
                    
                    if data:
                        wx.CallAfter(self.frame.ProcessNotificationReply, data)
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"IPC Server error: {e}")
                    break
        except Exception as e:
            print(f"Failed to start IPC server: {e}")


class ChatWindow(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(ChatWindow, self).__init__(*args, **kwargs)
        
        self.prompt = ""
        self.response = "Please enter your prompt."
        self.taskbar_icon = None
        self.ipc_server = None
        self.command_parser = CommandParser()
        
        # Confirmation state
        self.waiting_for_confirmation = False
        self.pending_command = None
        self.pending_prompt = None
        self.is_submitting = False
        
        self.InitUI()
        self.SetupTaskBarIcon()
        self.StartIPCServer()
        
        # Show startup info
        settings = LLMs.get_current_settings()
        self.response_text.AppendText(f"Current Provider: {settings['provider']} | Model: {settings['model']}\n\n")
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
    
    def InitUI(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Response Text (Scrollable)
        self.response_text = wx.TextCtrl(
            panel,
            value=self.response,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL
        )
        vbox.Add(self.response_text, proportion=1, flag=wx.ALL | wx.EXPAND, border=10)
        
        # Feedback/Status bar
        self.feedback_text = wx.StaticText(panel, label="")
        self.feedback_text.SetForegroundColour(wx.Colour(100, 100, 100))
        vbox.Add(self.feedback_text, flag=wx.ALL | wx.EXPAND, border=5)
        
        # Horizontal Box for Input Field and Submit Button
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        # Input Field
        self.input_field = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        self.input_field.Bind(wx.EVT_TEXT_ENTER, self.OnSubmit)
        self.input_field.Bind(wx.EVT_TEXT, self.OnTextChange)
        hbox.Add(self.input_field, proportion=1, flag=wx.ALL | wx.EXPAND, border=10)
        
        # Submit Button
        self.submit_button = wx.Button(panel, label="Submit")
        self.submit_button.Bind(wx.EVT_BUTTON, self.OnSubmit)
        hbox.Add(self.submit_button, flag=wx.ALL, border=10)
        
        vbox.Add(hbox, flag=wx.EXPAND)
        
        panel.SetSizer(vbox)
        
        self.SetTitle("LlamaHUD")
        self.SetSize((600, 500))
        self.Centre()
        
        # Auto-focus input field
        wx.CallAfter(self.input_field.SetFocus)
    
    def SetupTaskBarIcon(self):
        self.taskbar_icon = TaskBarIcon(self)
    
    def StartIPCServer(self):
        self.ipc_server = IPCServer(self)
        self.ipc_server.start()
    
    def OnTextChange(self, event):
        """Handle text changes for autocomplete and file browser trigger"""
        text = self.input_field.GetValue()
        cursor_pos = self.input_field.GetInsertionPoint()
        
        # Check if user just typed /
        if cursor_pos > 0 and text[cursor_pos-1:cursor_pos] == '/':
            self.ShowPromptAutocomplete()
        
        # Check if user typed @file (trigger file browser)
        if '@file' in text.lower():
            # Find position of @file
            file_pos = text.lower().find('@file')
            if file_pos >= 0:
                self.TriggerFileBrowser(file_pos)
    
    def ShowPromptAutocomplete(self):
        """Show available prompts"""
        prompts = self.command_parser.get_available_prompts()
        if prompts:
            prompt_list = ", ".join(prompts)
            self.SetFeedback(f"Available prompts: {prompt_list}")
    
    def TriggerFileBrowser(self, position):
        """Open file browser when @file is detected"""
        wildcard = "All files (*.*)|*.*|Text files (*.txt)|*.txt|Python files (*.py)|*.py|PDF files (*.pdf)|*.pdf"
        
        dlg = wx.FileDialog(
            self,
            message="Choose a file",
            defaultDir="",
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        )
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            # Replace @file with @filepath
            current_text = self.input_field.GetValue()
            new_text = current_text.lower().replace('@file', f'@{path}', 1)
            self.input_field.SetValue(new_text)
            self.input_field.SetInsertionPoint(len(new_text))
        else:
            # User cancelled, remove @file
            current_text = self.input_field.GetValue()
            new_text = current_text.lower().replace('@file', '', 1)
            self.input_field.SetValue(new_text)
        
        dlg.Destroy()
    
    def SetFeedback(self, message: str):
        """Set feedback message"""
        self.feedback_text.SetLabel(message)
    
    def ProcessNotificationReply(self, message):
        """Handle replies from notifications"""
        self.input_field.SetValue(message)
        self.OnSubmit(None)
    
    def OnSubmit(self, event):
        if self.is_submitting:
            return
            
        self.prompt = self.input_field.GetValue()
        
        if not self.prompt.strip():
            return
            
        # Check for exit command
        if self.prompt.strip().lower() == "#exit":
            self.Close()
            return
        
        self.is_submitting = True
        
        # Check if we're waiting for confirmation
        if self.waiting_for_confirmation:
            response = self.prompt.strip().lower()
            if response in ['y', 'yes']:
                self.response_text.AppendText(f"User: {self.prompt}\n[Confirmed. Command execution disabled in current version]\n\n")
                self.waiting_for_confirmation = False
                self.pending_command = None
                self.input_field.SetValue("")
                self.SetFeedback("Ready")
                self.is_submitting = False
                return
            elif response in ['n', 'no']:
                self.response_text.AppendText(f"User: {self.prompt}\n[Cancelled]\n\n")
                self.waiting_for_confirmation = False
                self.pending_command = None
                self.input_field.SetValue("")
                self.SetFeedback("Ready")
                self.is_submitting = False
                return
            else:
                self.response_text.AppendText(f"User: {self.prompt}\n[Invalid response. Please type Y/Yes or N/No]\n")
                self.input_field.SetValue("")
                self.is_submitting = False
                return
        
        # Disable the submit button
        self.submit_button.Disable()
        self.submit_button.SetLabel("Processing...")
        self.SetFeedback("Processing commands...")
        self.input_field.SetValue("")
        
        # Parse commands (without shell execution for now)
        processed_text, feedback = self.command_parser.parse(
            self.prompt,
            confirmation_callback=None
        )
        
        # Show feedback
        if feedback:
            feedback_str = " ".join(feedback)
            self.SetFeedback(feedback_str)
            self.response_text.AppendText(f"\n{feedback_str}\n")
            
        # If no text remains after processing commands, don't send to LLM
        if not processed_text.strip():
            self.is_submitting = False
            self.submit_button.Enable()
            self.submit_button.SetLabel("Submit")
            self.SetFeedback("Ready")
            self.input_field.SetFocus()
            return
        
        # Update UI with user prompt immediately
        self.response_text.AppendText(f"\nUser: {self.prompt}\n")
        
        # Start background thread for LLM
        threading.Thread(target=self.RunLLMThread, args=(processed_text,), daemon=True).start()

    def RunLLMThread(self, processed_text):
        """Run LLM in background thread"""
        try:
            response = LLMs.sendToLLM(processed_text)
            wx.CallAfter(self.OnLLMResponse, response)
        except Exception as e:
            wx.CallAfter(self.OnLLMResponse, f"Error: {str(e)}")

    def OnLLMResponse(self, response):
        """Handle LLM response on main thread"""
        self.is_submitting = False
        self.response = response
        self.response_text.AppendText(f"LLM: {self.response}\n\n")
        
        # Re-enable controls
        self.submit_button.Enable()
        self.submit_button.SetLabel("Submit")
        self.SetFeedback("Ready")
        
        # Auto-focus input
        self.input_field.SetFocus()
        
        # Send interactive notification
        easy_notification(self.response)
        
        # Save settings
        self.command_parser.save_settings()
    
    def OnClose(self, event):
        # Clean shutdown
        if self.ipc_server:
            self.ipc_server.stop()
        if self.taskbar_icon:
            self.taskbar_icon.RemoveIcon()
            self.taskbar_icon.Destroy()
        self.Destroy()


if __name__ == "__main__":
    print("LlamaHUD is starting...")
    app = wx.App()
    frame = ChatWindow(None)
    frame.Show()
    app.MainLoop()