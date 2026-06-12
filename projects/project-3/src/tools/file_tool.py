from src.core.file_manager import FileManager

file_manager = FileManager()

def move_file_tool(source: str, destination: str):
    file_manager.move(source, destination)