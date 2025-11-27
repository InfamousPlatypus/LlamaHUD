# LlamaHUD

## About
LlamaHUD is a minimal, multi-provider LLM frontend that operates under the assumption that there is one conversation, one model, one provider at a time.

The GUI is very simple: chat history, text box, and submit button. This comes from our operating model that has two parts:

### Everything can be done with text.
### Everything can be done in notifications.

Minimal UI, fast, light. `/commands` can run your entire computer. We are starting with json editing, allowing for updating settings.json.

## Currently Implemented

### Core Features
- ✅ **GUI** - Simple wxPython interface with chat history
- ✅ **Interactive Notifications** - C# toast notifications with quick reply capability
- ✅ **Virtual Environment** - Isolated Python dependencies
- ✅ **Flexible Configuration** - JSON-based settings for all providers

### LLM Backends
- ✅ **Ollama** - Local models via Ollama
- ✅ **OpenAI** - ChatGPT and compatible APIs  
- ✅ **GPT4All** - Local GPT4All server
- ✅ **Anthropic** - Claude models
- ✅ **Google** - Gemini models
- ✅ **WatsonX** - IBM WatsonX AI

### Architecture
- Provider pattern for easy extensibility
- Per-provider configuration in `settings.json`
- Automatic chat history management
- Relative paths for portability

## Configuration

Edit `settings.json` to configure providers:

```json
{
  "provider": "Ollama",
  "providers": {
    "Ollama": {"model": "llama3.1"},
    "OpenAI": {"model": "gpt-4", "api_key": "sk-..."},
    "Anthropic": {"model": "claude-3-5-sonnet-20241022", "api_key": "sk-ant-..."},
    "Google": {"model": "gemini-pro", "api_key": "..."},
    "GPT4All": {"model": "gpt4all-lora", "base_url": "http://localhost:4891/v1"},
    "WatsonX": {"model": "ibm/granite-13b-chat-v2", "api_key": "...", "project_id": "..."}
  }
}
```

## Commands

- **`/prompt`** - Inject preconfigured prompts (e.g., `/startup`, `/code_review`)
- **`@file`** - Read file content (supports fuzzy search, auto-creates if missing)
- **`#changeBackend <provider>`** - Switch LLM provider (e.g., `#changeBackend OpenAI`)
- **`#changeModel <model>`** - Switch model (e.g., `#changeModel gpt-4`)
- **`#shell <command>`** - Execute shell command (requires confirmation)
- **`#read @file`** - Read file via command line

## Running

```bash
# Build notifications (first time or after changes)
.\build_notifs.bat

# Run the application
.\run_hud.bat
```

### Medium Priority
- [ ] Cross-platform support (Linux, macOS notifications)
- [ ] MCP server integration
- [ ] Agent support (multi-step reasoning, tool use)
- [ ] AnythingLLM backend

### Low Priority
- [ ] Package as single executable
- [ ] Installer/distribution

## Architecture

**Python Components:**
- `HUD.py` - Main GUI application
- `LLMs.py` - Multi-provider LLM interface
- `Notifs.py` - Python wrapper for C# notifications
- `SlashCheck.py` - Command processor

**C# Components:**
- `Notifs.cs` - Interactive toast notifications with IPC

**Configuration:**
- `settings.json` - Provider settings and API keys
- `requirements.txt` - Python dependencies

## Dependencies

Install Python dependencies:
```bash
.venv\Scripts\pip install -r requirements.txt
```

Included providers:
- wxPython (GUI)
- ollama (Ollama)
- openai (OpenAI, GPT4All)
- anthropic (Claude)
- google-generativeai (Gemini)
- ibm-watsonx-ai (WatsonX)
