# Commands Guide

LlamaHUD uses a powerful prefix system to give you control over your workflow.

## `/` Prompts (Prompt Chaining)

Type `/` to trigger the prompt autocomplete menu. This allows you to insert pre-defined prompts or "personas" into your current query.

*   **Usage**: `/summarize`, `/code`, `/debug`
*   **Configuration**: You can add your own prompts in `settings.json` under the `"prompts"` section.

## `@` File References

Type `@file` (or just `@` followed by a path) to include the contents of a file in your prompt.

*   **Trigger**: Typing `@file` opens a file browser dialog.
*   **Manual Entry**: You can also type `@path/to/file.txt` directly.
*   **Supported Formats**: Text files (`.txt`, `.py`, `.md`, etc.) and PDFs (`.pdf`).
*   **Fuzzy Search**: LlamaHUD attempts to find files even if you don't type the exact path.

## `#` System Commands

The `#` prefix is used for controlling the LlamaHUD application itself.

### Core Commands
*   `#changeBackend <provider>`: Switch the LLM provider (e.g., `#changeBackend Ollama`, `#changeBackend OpenAI`).
*   `#changeModel <model>`: Switch the model for the current provider (e.g., `#changeModel llama3`, `#changeModel gpt-4`).
*   `#read @file`: Explicitly read and display the content of a file without sending it to the LLM.

### Shell Commands (Power Users)
*   `#shell <command>`: Execute a system shell command.
    *   **Safety**: By default, this requires confirmation.
    *   **Example**: `#shell dir`, `#shell python script.py`
    *   See [Power Users Guide](power_users.md) for more details.
