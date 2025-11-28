# Installation Guide

## Prerequisites

Before installing LlamaHUD, ensure you have the following:

*   **Python 3.10+**: [Download Python](https://www.python.org/downloads/)
*   **Ollama**: [Download Ollama](https://ollama.com/) (Required for local LLM support)

## Setup

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/InfamousPlatypus/LlamaHUD.git
    cd LlamaHUD
    ```

2.  **Create a Virtual Environment** (Recommended):
    ```bash
    python -m venv .venv
    # Windows
    .\.venv\Scripts\activate
    # Linux/Mac
    source .venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Application**:
    You can use the provided batch file or run the Python script directly.
    ```bash
    # Windows Batch File
    .\run_hud.bat

    # Python Direct
    python HUD.py
    ```

## Troubleshooting

*   **"ModuleNotFoundError"**: Ensure you have activated your virtual environment and installed `requirements.txt`.
*   **Ollama Connection Error**: Make sure Ollama is running (`ollama serve` or via the system tray app).
