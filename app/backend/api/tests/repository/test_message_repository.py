import pytest
from pathlib import Path
import json
from repositories.message_repository import MessageRepository


@pytest.fixture
def message_storage(tmp_path: Path) -> Path:
    storage_file = tmp_path / "messages.json"
    storage_file.write_text(json.dumps([]))
    return storage_file

@pytest.fixture
def message_repository(message_storage: Path) -> MessageRepository:
    # MessageRepositoryのコンストラクタにstorage_fileのパスを渡す実装を想定しています。
    return MessageRepository(storage_path=message_storage)

def test_list_messages_empty(message_repository: MessageRepository):
    # 何も追加していない場合、空のリストが返るはず
    messages = message_repository.list_messages()
    assert isinstance(messages, list)
    assert messages == []

def test_list_messages_with_data(message_repository: MessageRepository, message_storage: Path):
    # ここでは、直接ストレージファイルにデータを書き込み、その後list_messagesで読み出すケースをシミュレートします
    sample_messages = [
        {"id": 1, "content": "Hello"},
        {"id": 2, "content": "World"}
    ]
    # 直接JSONファイルに書き込む(実際の実装ではrepository.add_messageなどのメソッドがあるかもしれません)
    message_storage.write_text(json.dumps(sample_messages))
    
    messages = message_repository.list_messages()
    assert isinstance(messages, list)
    assert len(messages) == 2
    assert messages[0]["content"] == "Hello"
    assert messages[1]["content"] == "World"