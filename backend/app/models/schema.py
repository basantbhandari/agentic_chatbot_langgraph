from typing import Annotated, Literal, Optional

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from pydantic import BaseModel, Field


class IntentClassification(BaseModel):
    """Structured response from the intent classifier."""
    intent: Literal["knowledge_base", "appointment", "casual_conversation", "other"] = Field(
        description="The classified intent of the user's message."
    )
    confidence: Literal["high", "medium", "low"] = Field(
        description="How confident the model is in this classification."
    )
    reason: str = Field(
        description="One short sentence explaining why this intent was chosen."
    )


class ChatState(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages]
    intent: Optional[str] = None
    confidence: Optional[str] = None
    reason: Optional[str] = None