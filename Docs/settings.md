# Settings Configuration

LlamaHUD is highly configurable via the `settings.json` file located in the root directory.

## Structure

```json
{
    "default_app": "Ollama",
    "default_model": "llama3.1",
    "providers": {
        "Ollama": { "model": "llama3.1" },
        "OpenAI": { "api_key": "sk-...", "model": "gpt-4" }
    },
    "prompts": {
        "summarize": "Please summarize the following text:",
        "debug": "Analyze the following code for bugs:"
    },
    "shell_execution": {
        "enabled": true,
        "safety_level": 1,
        "safe_commands": ["dir", "ls", "echo"]
    }
}
```

## Key Sections

*   **`default_app`**: The active LLM provider (e.g., "Ollama", "OpenAI").
*   **`default_model`**: The active model name.
*   **`providers`**: Configuration for each provider. API keys should be stored here (or use environment variables).
*   **`prompts`**: Custom shortcuts triggered by `/`.
*   **`shell_execution`**: Controls the `#shell` command safety.
    *   `safety_level`: `0` (No checks), `1` (Whitelist/Confirmation), `2` (Disabled).
