import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

import pytest

from repositories.message_repository import MessageRepository


class FakeAgents:
    def list_messages(self, thread_id):
        return ["message1", "message2"]


class FakeProjectClient:
    def __init__(self):
        self.agents = FakeAgents()


def test_list_messages_normal():
    # Arrange
    thread_id = "thread_123"
    expected_messages = ["message1", "message2"]
    fake_project_client = FakeProjectClient()
    repository = MessageRepository(fake_project_client)

    # Act
    messages = repository.list_messages(thread_id)

    # Assert
    assert messages == expected_messages