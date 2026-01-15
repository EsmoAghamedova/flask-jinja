from extensions import db
from models import ChatSession, ChatMessage

def get_or_create_active_session(user_id: int) -> ChatSession:
    session = ChatSession.query.filter_by(user_id=user_id, is_active=True).first()
    if not session:
        session = ChatSession(user_id=user_id, is_active=True)
        db.session.add(session)
        db.session.commit()
    return session

def load_recent_messages(session_id: int, limit: int = 20):
    # load newest then reverse so AI reads in the correct order
    msgs = (ChatMessage.query
            .filter_by(session_id=session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
            .all())
    return list(reversed(msgs))
