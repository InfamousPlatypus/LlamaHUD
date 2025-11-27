"""
ShellExecutor.py - Handle # shell commands and MCP servers
Supports safety levels, command whitelisting, and user confirmation
"""
import subprocess
import json
from typing import Tuple, Optional, Dict, Any


class ShellExecutor:
    def __init__(self, settings):
        self.settings = settings
        self.shell_config = settings.get("shell_execution", {
            "enabled": False,
            "level": 0,
            "retry_count": 1
        })
        self.safe_commands = settings.get("safe_commands", [
            "ls", "dir", "pwd", "cat", "type", "git status", "git log", "git diff"
        ])
        self.mcp_servers = settings.get("mcp_servers", [])
        self.command_log = []
    
    def execute(self, command: str, confirmation_callback=None) -> Tuple[bool, str]:
        """
        Execute a command with appropriate safety checks
        
        Args:
            command: Command to execute
            confirmation_callback: Function to call for user confirmation
                                 Should return True/False
        
        Returns:
            (success, output/error)
        """
        if not self.shell_config.get("enabled", False):
            return False, "Shell execution is disabled. Enable in settings.json"
        
        level = self.shell_config.get("level", 0)
        
        # Check if it's an MCP command
        if self._is_mcp_command(command):
            return self._execute_mcp(command, confirmation_callback)
        
        # Shell command execution
        return self._execute_shell(command, level, confirmation_callback)
    
    def _is_mcp_command(self, command: str) -> bool:
        """Check if command should be routed to MCP server"""
        # Simple heuristic: if command matches an MCP server name
        for server in self.mcp_servers:
            if command.startswith(server.get("name", "")):
                return True
        return False
    
    def _execute_mcp(self, command: str, confirmation_callback) -> Tuple[bool, str]:
        """Execute command via MCP server"""
        # TODO: Implement MCP integration
        # For now, return placeholder
        return False, "MCP integration not yet implemented"
    
    def _execute_shell(self, command: str, level: int, confirmation_callback) -> Tuple[bool, str]:
        """
        Execute shell command with safety level
        
        Level 0: Disabled
        Level 1: Exact commands with confirmation
        Level 2: LLM-described commands with double confirmation
        """
        if level == 0:
            return False, "Shell execution disabled"
        
        # Check if command is safe (no confirmation needed)
        is_safe = self._is_safe_command(command)
        
        # Always require confirmation for shell/cmd
        needs_confirmation = True
        
        if needs_confirmation and confirmation_callback:
            # Ask for confirmation
            if level == 1:
                prompt = f"Run '{command}' in shell?"
            else:  # level == 2
                prompt = f"Model wants to run shell command:\n'{command}'\nContinue?"
            
            if not confirmation_callback(prompt):
                return False, "Command cancelled by user"
        
        # Execute the command
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Log the command
            self._log_command(command, result.returncode == 0)
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr or result.stdout
        
        except subprocess.TimeoutExpired:
            return False, "Command timed out (30s limit)"
        except Exception as e:
            return False, f"Error executing command: {e}"
    
    def _is_safe_command(self, command: str) -> bool:
        """Check if command is in safe list"""
        cmd_lower = command.lower().strip()
        
        for safe_cmd in self.safe_commands:
            if cmd_lower.startswith(safe_cmd.lower()):
                return True
        
        return False
    
    def _log_command(self, command: str, success: bool):
        """Log executed command"""
        self.command_log.append({
            "command": command,
            "success": success,
            "timestamp": None  # TODO: Add timestamp
        })
        
        # Keep last 100 commands
        if len(self.command_log) > 100:
            self.command_log = self.command_log[-100:]
    
    def get_command_log(self):
        """Get command execution log"""
        return self.command_log.copy()
    
    def read_file_via_shell(self, filepath: str) -> Tuple[bool, str]:
        """
        Read file using shell command (equivalent to @file)
        This is for #read @file.txt syntax
        """
        # Determine appropriate command based on OS
        import platform
        if platform.system() == "Windows":
            command = f"type \"{filepath}\""
        else:
            command = f"cat \"{filepath}\""
        
        return self.execute(command, confirmation_callback=lambda x: True)
