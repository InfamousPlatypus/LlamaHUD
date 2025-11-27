"""
FileHandler.py - Handle @ file references
Supports text files, PDFs, absolute/relative paths, fuzzy search
"""
import os
import re
from pathlib import Path
from difflib import get_close_matches
from typing import Optional, List, Tuple

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None


class FileHandler:
    def __init__(self, settings):
        self.settings = settings
        self.recent_files = settings.get("recent_files", [])
        self.max_recent = settings.get("max_recent_files", 3)
        self.search_paths = settings.get("file_search_paths", [os.getcwd(), os.path.expanduser("~")])
    
    def read_file(self, filepath: str) -> Tuple[bool, str]:
        """
        Read a file and return (success, content)
        Supports text and PDF files
        """
        try:
            path = Path(filepath)
            
            # Try to resolve the path
            if not path.is_absolute():
                resolved = self._resolve_path(filepath)
                if resolved:
                    path = Path(resolved)
                else:
                    return False, f"File not found: {filepath}"
            
            if not path.exists():
                return False, f"File not found: {filepath}"
            
            # Add to recent files
            self._add_recent(str(path.absolute()))
            
            # Read based on file type
            if path.suffix.lower() == '.pdf':
                return self._read_pdf(path)
            else:
                return self._read_text(path)
        
        except Exception as e:
            return False, f"Error reading file: {e}"
    
    def _read_text(self, path: Path) -> Tuple[bool, str]:
        """Read text file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            return True, content
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(path, 'r', encoding='latin-1') as f:
                    content = f.read()
                return True, content
            except Exception as e:
                return False, f"Error reading text file: {e}"
    
    def _read_pdf(self, path: Path) -> Tuple[bool, str]:
        """Read PDF file"""
        if not PdfReader:
            return False, "PyPDF2 not installed. Cannot read PDF files."
        
        try:
            reader = PdfReader(str(path))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return True, text.strip()
        except Exception as e:
            return False, f"Error reading PDF: {e}"
    
    def _resolve_path(self, filepath: str) -> Optional[str]:
        """
        Resolve a filepath using:
        1. Exact match in current directory
        2. Exact match in search paths
        3. Fuzzy search
        """
        # Try current directory first
        if os.path.exists(filepath):
            return os.path.abspath(filepath)
        
        # Try search paths
        for search_path in self.search_paths:
            full_path = os.path.join(search_path, filepath)
            if os.path.exists(full_path):
                return full_path
        
        # Fuzzy search
        return self._fuzzy_search(filepath)
    
    def _fuzzy_search(self, filename: str) -> Optional[str]:
        """
        Fuzzy search for filename in search paths
        Returns best match if found
        """
        all_files = []
        
        for search_path in self.search_paths:
            if not os.path.exists(search_path):
                continue
            
            try:
                for root, dirs, files in os.walk(search_path):
                    # Limit depth to avoid slow searches
                    depth = root[len(search_path):].count(os.sep)
                    if depth > 3:
                        continue
                    
                    for file in files:
                        all_files.append(os.path.join(root, file))
            except PermissionError:
                continue
        
        # Get basenames for matching
        basenames = [os.path.basename(f) for f in all_files]
        matches = get_close_matches(filename, basenames, n=1, cutoff=0.6)
        
        if matches:
            # Find the full path of the match
            for full_path in all_files:
                if os.path.basename(full_path) == matches[0]:
                    return full_path
        
        return None
    
    def _add_recent(self, filepath: str):
        """Add file to recent files list"""
        if filepath in self.recent_files:
            self.recent_files.remove(filepath)
        
        self.recent_files.insert(0, filepath)
        
        # Trim to max_recent
        if self.max_recent > 0:
            self.recent_files = self.recent_files[:self.max_recent]
    
    def get_recent_files(self) -> List[str]:
        """Get list of recent files"""
        return self.recent_files.copy()
    
    def create_file(self, filepath: str, content: str = "") -> Tuple[bool, str]:
        """Create a new file"""
        try:
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True, f"Created file: {filepath}"
        except Exception as e:
            return False, f"Error creating file: {e}"
