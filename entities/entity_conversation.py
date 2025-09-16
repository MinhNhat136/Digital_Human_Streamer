from dataclasses import dataclass
from typing import List

@dataclass
class Message:
    id: str
    content: str
    timestamp: float

@dataclass
class Conversation:
    id: str
    messages: List[Message]
    context: dict
    session_id: str
    created_at: float
    updated_at: float

@dataclass
class Context:
    user_preferences: dict
    conversation_history: List[Message]
    current_topic: str
    emotional_state: str

@dataclass
class StopRequest: 
    conversation_id: str
    stop_reason: str
    