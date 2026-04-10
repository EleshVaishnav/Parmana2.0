import os
from .registry import registry

@registry.register(
    name="read_file",
    description="Reads the contents of a file at the specified path.",
    parameters={
        "file_path": {
            "type": "string",
            "description": "The absolute or relative path to the file to read."
        }
    }
)
def read_file(file_path: str) -> str:
    """Reads and returns the content of a file."""
    try:
        if not os.path.exists(file_path):
            return f"Error: File not found at {file_path}"
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file {file_path}: {str(e)}"


@registry.register(
    name="write_file",
    description="Creates a new file or overwrites an existing file with the provided content.",
    parameters={
        "file_path": {
            "type": "string",
            "description": "The absolute or relative path where the file should be written."
        },
        "content": {
            "type": "string",
            "description": "The content to write into the file."
        }
    }
)
def write_file(file_path: str, content: str) -> str:
    """Writes content to a file."""
    try:
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing to file {file_path}: {str(e)}"
