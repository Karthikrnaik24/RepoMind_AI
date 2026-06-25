"""Chat application service placeholder."""

from app.repositories.chat_repository import ChatRepository


class ChatService:
    """Coordinates future chat use cases through repository dependencies."""

    def __init__(self, chat_repository: ChatRepository) -> None:
        self.chat_repository = chat_repository
