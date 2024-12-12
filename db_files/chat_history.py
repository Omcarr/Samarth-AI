import json
from datetime import datetime
import uuid
from sqlalchemy import insert

# async def save_chat_history(redis, redis_key, SessionLocal, chat_history_table, user_id, logger):
#     try:
#         if redis_key:
#             # Retrieve chat history from Redis
#             chat_history = await redis.lrange(redis_key, 0, -1)  # Asynchronously retrieve chat history

#             # Format and log chat history
#             formatted_history = []
#             db_entries = []

#             for entry in chat_history:
#                 chat_entry = json.loads(entry)
#                 user_message = chat_entry.get("user_message", "N/A")
#                 bot_response = chat_entry.get("bot_response", "N/A")
#                 timestamp = chat_entry.get("timestamp", "N/A")

#                 formatted_history.append(f"{timestamp}: User: {user_message}, Chatbot: {bot_response}")

#                 # Prepare entry for database insertion
#                 db_entries.append({
#                     "user_id": user_id,
#                     "timestamp": datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f"),  # Parse timestamp
#                     "user_message": user_message,
#                     "bot_message": bot_response,
#                     "bot_mode": "default",  # Set bot mode accordingly
#                     "session_id": str(uuid.uuid4())  # Ensure it's a string for consistency
#                 })

#             logger.info("Formatted Chat History:")
#             for line in formatted_history:
#                 logger.info(line)

#             # Save to the database
#             async with SessionLocal() as session:
#                 # Use the insert construct in a loop or with executemany
#                 stmt = insert(chat_history_table).values(db_entries)
#                 await session.execute(stmt)  # Execute the statement with the entries
#                 await session.commit()  # Commit the transaction

#     except Exception as e:
#         logger.error(f"Error saving chat history: {e}")



# def create_title_for_chat_history(session_history):
#     #use gemini to create the chat history



def generate_chat_summary(chat_history):
    return 'summary by gemini'