import os

def write_file(filename: str, content: str) -> str:
    """Writes content to a file in the current directory."""
    try:
        # Prevent directory traversal attacks
        safe_filename = os.path.basename(filename)
        with open(safe_filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Success: Code written to {safe_filename}. Ready for review."
    except Exception as e:
        return f"Error writing file: {e}"