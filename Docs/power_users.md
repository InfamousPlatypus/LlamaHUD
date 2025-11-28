# Power Users Guide: Shell Commands

> [!WARNING]
> Shell commands allow LlamaHUD to execute code on your computer. Use with caution.

## Enabling Shell Commands

By default, shell commands are restricted for safety. To enable them:

1.  Open `settings.json`.
2.  Locate the `shell_execution` section.
3.  Set `"enabled": true`.

## Usage

Use the `#shell` prefix followed by your command.

```bash
#shell dir
#shell python --version
#shell ipconfig
```

## Safety Levels

You can configure the safety level in `settings.json`:

*   **Level 0 (Unsafe)**: Commands run immediately without confirmation. **NOT RECOMMENDED**.
*   **Level 1 (Default)**:
    *   **Whitelisted Commands**: Run immediately (e.g., `dir`, `echo`).
    *   **Unknown Commands**: Require user confirmation (Y/N).
*   **Level 2 (Strict)**: All commands are disabled.

## Whitelist

You can add safe commands to the `"safe_commands"` list in `settings.json` to bypass confirmation for frequent tasks.
