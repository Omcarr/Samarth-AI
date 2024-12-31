import json
from datetime import datetime
import uuid
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()

#chat history storage
class ChatHistory(Base):
    __tablename__ = 'chat_history'

    # Use UUID as the primary key to ensure global uniqueness
    id = sa.Column(sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Explicitly generate a separate session_id using UUID
    session_id = sa.Column(sa.String(36), nullable=False, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    user_id = sa.Column(sa.String, nullable=False)
    bot_mode = sa.Column(sa.String, nullable=True, default='default')
    chat_summary = sa.Column(sa.Text, nullable=True)
    full_chat_history = sa.Column(JSONB, nullable=False)
    total_messages = sa.Column(sa.Integer, nullable=False)
    start_time = sa.Column(sa.DateTime(timezone=True), nullable=False, default=datetime.now())
    end_time = sa.Column(sa.DateTime(timezone=True), nullable=False, default=datetime.now())
    
    def __repr__(self):
        return f"<ChatHistory(session_id={self.session_id}, user_id={self.user_id})>"
   
   
def save_chat_history(redis_client, redis_key, SessionLocal, user_id, logger):
    """
    Save chat history to PostgreSQL in a synchronous manner.
    Args:
        redis_client: Synchronous Redis client.
        redis_key: Redis key for chat history.
        SessionLocal: SQLAlchemy Session Factory.
        user_id: User identifier.
        logger: Logging object.
    """
    try:
        # Retrieve chat history synchronously
        chat_history = redis_client.lrange(redis_key, 0, -1)

        if not chat_history:
            logger.warning(f"No chat history found for key: {redis_key}")
            return

        # Parse chat history
        parsed_history = [json.loads(entry.decode('utf-8')) for entry in chat_history]

        # Generate chat summary
        chat_summary = generate_chat_summary(parsed_history)

        # Extract session details
        first_entry = parsed_history[0]
        last_entry = parsed_history[-1]

        start_time = datetime.fromisoformat(first_entry['timestamp'])
        end_time = datetime.fromisoformat(last_entry['timestamp'])
        session_id = first_entry.get('session_id', str(uuid.uuid4()))

        # Save to the database synchronously
        db_session = SessionLocal()
        try:
            new_chat_record = ChatHistory(
                user_id=user_id,
                session_id=session_id,
                bot_mode=first_entry.get('bot_mode', 'default'),
                chat_summary=chat_summary,
                full_chat_history=parsed_history,
                total_messages=len(parsed_history),
                start_time=start_time,
                end_time=end_time
            )

            db_session.add(new_chat_record)
            db_session.commit()
            logger.info(f"Chat history saved for user {user_id}, session {session_id}")
        except Exception as commit_error:
            db_session.rollback()
            logger.error(f"Error committing chat history: {str(commit_error)}")
            raise
        finally:
            db_session.close()

    except Exception as e:
        logger.error(f"Error saving chat history: {str(e)}")
        
def generate_chat_summary(chat_history):
    return 'summary by gemini'