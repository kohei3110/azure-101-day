import os
from utils.file_handler import FileHandler

class FileRepository:
    def __init__(self, file_handler: FileHandler):
        self.file_handler = file_handler

    async def save_temp_file(self, file, destination: str):
        return await self.file_handler.save_temp_file(file, destination)

    def delete_file(self, file_location: str):
        self.file_handler.delete_file(file_location)