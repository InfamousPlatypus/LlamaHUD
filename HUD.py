import wx
import LLMs
from Notifs import easy_notification
from SlashCheck import SlashCheck, determineSlash

class ChatWindow(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(ChatWindow, self).__init__(*args, **kwargs)

        self.prompt = ""
        self.response = "Please enter your prompt."

        self.InitUI()

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

        # Horizontal Box for Input Field and Submit Button
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        # Input Field
        self.input_field = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        self.input_field.Bind(wx.EVT_TEXT_ENTER, self.OnSubmit)  # Bind Enter key to OnSubmit
        hbox.Add(self.input_field, proportion=1, flag=wx.ALL | wx.EXPAND, border=10)

        # Submit Button
        submit_button = wx.Button(panel, label="Submit")
        submit_button.Bind(wx.EVT_BUTTON, self.OnSubmit)
        hbox.Add(submit_button, flag=wx.ALL, border=10)

        # Add the horizontal box to the vertical box
        vbox.Add(hbox, flag=wx.EXPAND)

        panel.SetSizer(vbox)

        self.SetTitle("LlamaHUD")
        self.SetSize((500, 400))  # Increased size for better visibility
        self.Centre()

    def OnSubmit(self, event):
        self.prompt = self.input_field.GetValue()

        # Disable the submit button
        submit_button = event.GetEventObject()
        submit_button.Disable()
        submit_button.label = "Processing..."

        # Get the response from the LLM
        if not SlashCheck(self.prompt): # Check for slashes
            self.response = LLMs.sendToLLM(self.prompt)
        else:
            self.response=determineSlash(self.prompt)

        # Update the response text area
        self.response_text.AppendText(f"\nUser: {self.prompt}\nLLM: {self.response}")
        self.input_field.SetValue("")

        # Re-enable the submit button
        submit_button.Enable()
        submit_button.label = "Submit"
        easy_notification(self.response)


if __name__ == "__main__":
    print("LlamaHUD is starting...")
    app = wx.App()
    frame = ChatWindow(None)
    frame.Show()
    app.MainLoop()