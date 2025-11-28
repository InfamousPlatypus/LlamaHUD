# Basic Usage

LlamaHUD is designed to be a minimalist, keyboard-centric interface for interacting with LLMs.

## Interface Overview

*   **Input Field**: The bottom text box where you type your prompts. It auto-focuses on startup.
*   **Response Area**: The main text area showing the chat history.
*   **Status Bar**: Located just above the input field, showing feedback, current mode, or errors.
*   **System Tray Icon**: A LlamaHUD icon in your system tray. Double-click to show/hide the window.

## Interacting

1.  **Type & Enter**: Simply type your query and press Enter to send it to the LLM.
2.  **Notifications**: When the LLM replies, you will receive a system notification.
    *   **Interactive Toasts**: On Windows, you can reply directly from the notification! Type in the text box and click "Send".
    *   **Click to Open**: Clicking the notification body will bring LlamaHUD to the front.

## Key Features

*   **Prompt Chaining**: Use `/` to access saved prompts.
*   **File Context**: Use `@file` to include file contents in your query.
*   **Commands**: Use `#` to control the application (change models, backend, etc.).

See the [Commands Guide](commands.md) for more details.
