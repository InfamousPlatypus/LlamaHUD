using System;
using System.Net.Sockets;
using System.Text;
using System.Runtime.InteropServices;
using System.Diagnostics;

#if WINDOWS
using Microsoft.Toolkit.Uwp.Notifications;
#endif

namespace LlamaHUDNotifs
{
    class Program
    {
        static void ShowWindows(string title, string message)
        {
#if WINDOWS
            try
            {
                new ToastContentBuilder()
                    .AddText(title)
                    .AddText(message)
                    .AddInputTextBox("replyBox", placeHolderContent: "Type a reply...")
                    .AddButton(new ToastButton()
                        .SetContent("Send")
                        .AddArgument("action", "reply")
                        .SetBackgroundActivation())
                    .Show();
            }
            catch (Exception e)
            {
                // Fallback to simple notification
                Console.WriteLine($"Toast failed: {e.Message}");
                ShowWindowsFallback(title, message);
            }
#endif
        }

        static void ShowWindowsFallback(string title, string message)
        {
            // Use PowerShell for simple notification
            try
            {
                var psi = new ProcessStartInfo
                {
                    FileName = "powershell.exe",
                    Arguments = $"-Command \"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('{message}', '{title}')\"",
                    CreateNoWindow = true,
                    UseShellExecute = false
                };
                Process.Start(psi);
            }
            catch { }
        }

        static void ShowLinux(string title, string message)
        {
            // Use notify-send on Linux
            try
            {
                var psi = new ProcessStartInfo
                {
                    FileName = "notify-send",
                    Arguments = $"\"{title}\" \"{message}\"",
                    CreateNoWindow = true,
                    UseShellExecute = false
                };
                Process.Start(psi);
            }
            catch (Exception e)
            {
                Console.WriteLine($"Linux notification failed: {e.Message}");
            }
        }

        static void ShowMacOS(string title, string message)
        {
            // Use osascript on macOS
            try
            {
                var script = $"display notification \"{message}\" with title \"{title}\"";
                var psi = new ProcessStartInfo
                {
                    FileName = "osascript",
                    Arguments = $"-e '{script}'",
                    CreateNoWindow = true,
                    UseShellExecute = false
                };
                Process.Start(psi);
            }
            catch (Exception e)
            {
                Console.WriteLine($"macOS notification failed: {e.Message}");
            }
        }

        static void Show(string title, string message)
        {
            if (RuntimeInformation.IsOSPlatform(OSPlatform.Windows))
            {
                ShowWindows(title, message);
            }
            else if (RuntimeInformation.IsOSPlatform(OSPlatform.Linux))
            {
                ShowLinux(title, message);
            }
            else if (RuntimeInformation.IsOSPlatform(OSPlatform.OSX))
            {
                ShowMacOS(title, message);
            }
            else
            {
                Console.WriteLine($"Unsupported platform. {title}: {message}");
            }
        }

        static void SendReplyToHUD(string message)
        {
            try
            {
                using (TcpClient client = new TcpClient("127.0.0.1", 12345))
                using (NetworkStream stream = client.GetStream())
                {
                    byte[] data = Encoding.UTF8.GetBytes(message);
                    stream.Write(data, 0, data.Length);
                }
            }
            catch (Exception e)
            {
                Console.WriteLine($"Failed to send reply to HUD: {e.Message}");
            }
        }

        static void Main(string[] args)
        {
#if WINDOWS
            // Register for toast activation on Windows
            try {
                ToastNotificationManagerCompat.OnActivated += toastArgs =>
                {
                    ToastArguments args = ToastArguments.Parse(toastArgs.Argument);
                    if (args.Contains("action") && args["action"] == "reply")
                    {
                        string? replyText = toastArgs.UserInput["replyBox"] as string;
                        if (!string.IsNullOrEmpty(replyText))
                        {
                            SendReplyToHUD(replyText);
                        }
                    }
                };
            } catch { }
#endif

            if (args.Length > 0)
            {
                if (args[0] == "--reply" && args.Length > 1)
                {
                    // Direct invocation for testing
                    SendReplyToHUD(args[1]);
                    return;
                }
                else if (args.Length >= 2)
                {
                    string title = args[0];
                    string message = args[1];
                    Show(title, message);
                    return;
                }
            }

            Console.WriteLine("Usage: Notifs.exe <title> <message>");
            Console.WriteLine("   or: Notifs.exe --reply <message>");
        }
    }
}
