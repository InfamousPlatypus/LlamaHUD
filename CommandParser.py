"""
CommandParser.py - Parse and execute /, @, and # commands
Handles prompt references, file injection, and shell execution
"""
import re
import json
from typing import Tuple, List, Dict, Any, Optional, Callable
from FileHandler import FileHandler
from ShellExecutor import ShellExecutor


class CommandParser:
    def __init__(self, settings_path="settings.json"):
        self.settings = self._load_settings(settings_path)
        self.file_handler = FileHandler(self.settings)
        self.shell_executor = ShellExecutor(self.settings)
        self.prompts = self._load_prompts()
    
    def _load_settings(self, path: str) -> Dict[str, Any]:
        """Load settings from JSON file"""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._create_default_settings(path)
    
    def _create_default_settings(self, path: str) -> Dict[str, Any]:
        """Create default settings file"""
        defaults = {
            "provider": "Ollama",
            "providers": {},
            "prompts": {
                "startup": "You are a helpful assistant.",
                "code_review": "You are an expert code reviewer. Analyze code for bugs, style, and improvements.",
                "technical": "Use technical, precise language. Be concise and accurate."
            },
            "prompts_file": None,
            "shell_execution": {
                "enabled": False,
                "level": 0,
                "retry_count": 1
            },
            "mcp_servers": [],
            "mcp_config_file": None,
            "safe_commands": ["ls", "dir", "pwd", "cat", "type", "git status"],
            "file_search_paths": [],
            "recent_files": [],
            "max_recent_files": 3,
            "file_browser_default": True
        }
        
        try:
            with open(path, 'w') as f:
                json.dump(defaults, f, indent=4)
        except:
            pass
        
        return defaults
    
    def _load_prompts(self) -> Dict[str, str]:
        """Load prompts from settings and external file if specified"""
        prompts = self.settings.get("prompts", {}).copy()
        
        # Load from external file if specified
        prompts_file = self.settings.get("prompts_file")
        if prompts_file:
            try:
                with open(prompts_file, 'r') as f:
                    external_prompts = json.load(f)
                    prompts.update(external_prompts)
            except:
                pass
        
        return prompts
    
    def parse(self, text: str, confirmation_callback: Optional[Callable] = None) -> Tuple[str, List[str]]:
        """
        Parse text and execute commands
        
        Returns:
            (processed_text, feedback_messages)
        """
        feedback = []
        
        # Process in order: / -> @ -> #
        text, prompt_feedback = self._process_prompts(text)
        feedback.extend(prompt_feedback)
        
        text, file_feedback = self._process_files(text)
        feedback.extend(file_feedback)
        
        text, shell_feedback = self._process_shell(text, confirmation_callback)
        feedback.extend(shell_feedback)
        
        return text, feedback
    
    def _process_prompts(self, text: str) -> Tuple[str, List[str]]:
        """Process / prompt commands"""
        feedback = []
        
        # Find all /prompt references
        pattern = r'/(\w+)'
        matches = re.finditer(pattern, text)
        
        replacements = []
        for match in matches:
            prompt_name = match.group(1)
            
            if prompt_name in self.prompts:
                prompt_text = self.prompts[prompt_name]
                
                # Resolve prompt references recursively
                prompt_text = self._resolve_prompt_references(prompt_text)
                
                replacements.append((match.start(), match.end(), prompt_text))
                feedback.append(f"[Using prompt: /{prompt_name}]")
            # If not found, leave it as-is (treat as char)
        
        # Apply replacements in reverse order to maintain positions
        for start, end, replacement in reversed(replacements):
            text = text[:start] + replacement + text[end:]
        
        return text, feedback
    
    def _resolve_prompt_references(self, prompt_text: str, depth: int = 0) -> str:
        """Recursively resolve prompt references within prompts"""
        if depth > 5:  # Prevent infinite recursion
            return prompt_text
        
        pattern = r'/(\w+)'
        matches = re.finditer(pattern, prompt_text)
        
        replacements = []
        for match in matches:
            ref_name = match.group(1)
            if ref_name in self.prompts:
                ref_text = self.prompts[ref_name]
                # Recursively resolve
                ref_text = self._resolve_prompt_references(ref_text, depth + 1)
                replacements.append((match.start(), match.end(), ref_text))
        
        # Apply replacements
        for start, end, replacement in reversed(replacements):
            prompt_text = prompt_text[:start] + replacement + prompt_text[end:]
        
        return prompt_text
    
    def _process_files(self, text: str) -> Tuple[str, List[str]]:
        """Process @ file references"""
        feedback = []
        
        # Find all @file references
        pattern = r'@([\w\-./\\:]+(?:\.\w+)?)'
        matches = re.finditer(pattern, text)
        
        replacements = []
        for match in matches:
            filepath = match.group(1)
            
            # Try to read the file
            success, content = self.file_handler.read_file(filepath)
            
            if success:
                replacements.append((match.start(), match.end(), content))
                feedback.append(f"[Read: {filepath}]")
            else:
                # File doesn't exist - create it
                create_success, create_msg = self.file_handler.create_file(filepath)
                if create_success:
                    replacements.append((match.start(), match.end(), ""))
                    feedback.append(f"[Created: {filepath}]")
                else:
                    feedback.append(f"[Error: {content}]")
        
        # Apply replacements in reverse order
        for start, end, replacement in reversed(replacements):
            text = text[:start] + replacement + text[end:]
        
        return text, feedback
    
    def _process_shell(self, text: str, confirmation_callback: Optional[Callable]) -> Tuple[str, List[str]]:
        """Process # shell commands and system commands"""
        feedback = []
        
        # Find all #command references - capture until end of word/phrase
        pattern = r'#([a-zA-Z0-9_\-\s./\\:]+)'
        matches = re.finditer(pattern, text)
        
        replacements = []
        for match in matches:
            full_command = match.group(1).strip()
            print(f"DEBUG: Found potential command: '{full_command}'")
            
            if not full_command:  # Just # alone
                continue
            
            # Check for special #read @file syntax
            if full_command.startswith("read @"):
                filepath = full_command[6:].strip()
                success, content = self.file_handler.read_file(filepath)
                if success:
                    replacements.append((match.start(), match.end(), content))
                    feedback.append(f"[Read via #: {filepath}]")
                else:
                    feedback.append(f"[Error: {content}]")
                continue
            
            # Check for #changeBackend
            if full_command.lower().startswith("changebackend"):
                print("DEBUG: Detected changeBackend command")
                import LLMs
                # Case insensitive check for the command, but preserve case for argument
                parts = full_command.split(maxsplit=1)
                if len(parts) > 1:
                    provider = parts[1].strip()
                    print(f"DEBUG: Switching to provider: {provider}")
                    result = LLMs.change_provider(provider)
                    replacements.append((match.start(), match.end(), ""))
                    feedback.append(f"[{result}]")
                else:
                    print("DEBUG: Missing provider argument")
                continue
            
            # Check for #changeModel
            if full_command.lower().startswith("changemodel"):
                print("DEBUG: Detected changeModel command")
                import LLMs
                parts = full_command.split(maxsplit=1)
                if len(parts) > 1:
                    model = parts[1].strip()
                    result = LLMs.change_model(model)
                    replacements.append((match.start(), match.end(), ""))
                    feedback.append(f"[{result}]")
                continue
            
            # Check for explicit #shell prefix
            if full_command.lower().startswith("shell "):
                print("DEBUG: Detected shell command")
                shell_cmd = full_command[6:].strip()
                success, output = self.shell_executor.execute(shell_cmd, confirmation_callback)
                
                if success:
                    replacements.append((match.start(), match.end(), output))
                    feedback.append(f"[Executed: {shell_cmd}]")
                else:
                    feedback.append(f"[Shell error: {output}]")
                continue
            
            # If no prefix match, treat as MCP command (placeholder) or ignore
            print(f"DEBUG: No handler found for '{full_command}'")
            pass
        
        # Apply replacements in reverse order
        for start, end, replacement in reversed(replacements):
            text = text[:start] + replacement + text[end:]
        
        return text, feedback
    
    def get_recent_files(self) -> List[str]:
        """Get list of recent files"""
        return self.file_handler.get_recent_files()
    
    def get_available_prompts(self) -> List[str]:
        """Get list of available prompt names"""
        return list(self.prompts.keys())
    
    def save_settings(self):
        """Save current settings back to file"""
        self.settings["recent_files"] = self.file_handler.recent_files
        try:
            with open("settings.json", 'w') as f:
                json.dump(self.settings, f, indent=4)
        except:
            pass
