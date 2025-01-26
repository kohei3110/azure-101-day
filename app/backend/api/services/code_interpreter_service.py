import logging
import os
from typing import Optional
from azure.ai.projects.models import FilePurpose
from tools.action.code_interpreter_tool import create_code_interpreter_tool
from utils.file_handler import FileHandler
from pathlib import Path
from tracing.tracing import tracer


class CodeInterpreterService:
    def __init__(self, project_client):
        self.project_client = project_client

    async def process_file_and_message(self, file, user_message: str, file_handler: FileHandler):
        with tracer.start_as_current_span("process_file_and_message") as span:
            span.set_attributes(
                {
                    "span_type": "HTTP"
                }
            )
            destination: str = os.getenv("DATA_DIR", "/data")
            file_location = await file_handler.save_temp_file(file, destination)
            try:
                uploaded_file = self.upload_file_to_project(file_location)
                agent = self.create_agent(uploaded_file.id)
                thread = self.create_thread()
                self.send_user_message_to_thread(thread.id, user_message)
                run = self.execute_run(thread.id, agent.id)
                self.handle_run_completion(run, thread.id, uploaded_file.id)
                file_name = self.save_generated_images(thread.id)
                return file_name
            finally:
                file_handler.delete_file(file_location)
                print("Deleted file")

    async def process_message_only(self, file, user_message: str, file_handler: FileHandler):
        with tracer.start_as_current_span("process_message_only") as span:
            span.set_attributes(
                {
                    "span_type": "HTTP"
                }
            )
            destination: str = os.getenv("DATA_DIR", "/data")
            file_location = await file_handler.save_temp_file(file, destination)
            try:
                uploaded_file = self.upload_file_to_project(file_location)
                agent = self.create_agent(uploaded_file.id)
                thread = self.create_thread()
                self.send_user_message_to_thread(thread.id, user_message)
                run = self.execute_run(thread.id, agent.id)
                logging.info(f"Run finished with status: {run.status}")
                messages = self.project_client.agents.list_messages(thread_id=thread.id)
                logging.info(f"Messages: {messages}")
                last_msg = messages.get_last_text_message_by_role("assistant")
                if last_msg:
                    return last_msg.text.value
            finally:
                file_handler.delete_file(file_location)
                print("Deleted file")

    def upload_file_to_project(self, file_location: str):
        with tracer.start_as_current_span("upload_file_to_project"):
            uploaded_file = self.project_client.agents.upload_file_and_poll(
                file_path=file_location, purpose=FilePurpose.AGENTS
            )
            logging.info(f"Uploaded file, file ID: {uploaded_file.id}")
            return uploaded_file
        
    def create_agent(self, file_id: Optional[str] = None):
        with tracer.start_as_current_span("create_agent"):
            code_interpreter = create_code_interpreter_tool(file_ids=[file_id] if file_id else [])
            agent = self.project_client.agents.create_agent(
                model="gpt-4o-mini",
                name="code_interpreter",
                instructions="You are helpful agent",
                tools=code_interpreter.definitions,
                tool_resources=code_interpreter.resources,
            )
            return agent
        
    def create_thread(self):
        with tracer.start_as_current_span("create_thread"):
            thread = self.project_client.agents.create_thread()
            logging.info(f"Created thread, thread ID: {thread.id}")
            return thread

    def send_user_message_to_thread(self, thread_id: str, user_message: str):
        with tracer.start_as_current_span("send_user_message_to_thread"):
            message = self.project_client.agents.create_message(
                thread_id=thread_id,
                role="user",
                content=user_message
            )
            logging.info(f"Created message, message ID: {message.id}")

    def execute_run(self, thread_id: str, agent_id: str):
        with tracer.start_as_current_span("execute_run"):
            run = self.project_client.agents.create_and_process_run(thread_id=thread_id, assistant_id=agent_id)
            logging.info(f"Run finished with status: {run.status}")
            return run

    def handle_run_completion(self, run, thread_id: str, file_id: str):
        with tracer.start_as_current_span("handle_run_completion"):
            if run.status == "failed":
                logging.error(f"Run failed: {run.last_error}")
            self.project_client.agents.delete_file(file_id)
            logging.info(f"Deleted file, file ID: {file_id}")

    def save_generated_images(self, thread_id: str):
        with tracer.start_as_current_span("save_generated_images"):
            messages = self.project_client.agents.list_messages(thread_id=thread_id)
            logging.info(f"Messages: {messages}")

            last_msg = messages.get_last_text_message_by_role("assistant")
            if last_msg:
                logging.info(f"Last Message: {last_msg.text.value}")

            for image_content in messages.image_contents:
                logging.info(f"Image File ID: {image_content.image_file.file_id}")
                file_name = f"{image_content.image_file.file_id}_image_file.png"
                self.project_client.agents.save_file(file_id=image_content.image_file.file_id, file_name=file_name)
                logging.info(f"Saved image file to: {Path.cwd() / file_name}")

            return file_name
        
    def get_generated_code(self, thread_id: str):
        with tracer.start_as_current_span("get_generated_code"):
            messages = self.project_client.agents.list_messages(thread_id=thread_id)
            logging.info(f"Messages: {messages}")

            last_msg = messages.get_last_text_message_by_role("assistant")
            if last_msg:
                logging.info(f"Last Message: {last_msg.text.value}")
                return last_msg.text.value