"""Chat persistence repository."""

from sqlalchemy.orm import Session

from app.infrastructure.database.models import ChatMessage, ChatSession, Citation
from app.repositories.base import BaseRepository


class ChatRepository(BaseRepository[ChatSession]):
    """Encapsulate persistence operations for chat records."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, ChatSession)

    def add_message(self, message: ChatMessage) -> ChatMessage:
        """Stage a chat message for insertion."""

        self.session.add(message)
        return message

    def add_citation(self, citation: Citation) -> Citation:
        """Stage a citation for insertion."""

        self.session.add(citation)
        return citation
