from typing import Annotated, Literal, Optional, TypedDict, NotRequired
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from pydantic import BaseModel, Field


class AppointmentBooking(BaseModel):
    """
    Structured appointment booking form collected via conversation.
    """

    name: Optional[str] = Field(
        default=None, description="Full name of the user. Must be non-empty and valid."
    )

    phone_number: Optional[str] = Field(
        default=None,
        description="Valid phone number with correct length and numeric format.",
    )

    email: Optional[str] = Field(
        default=None, description="Valid email address following standard email format."
    )

    preferred_date: Optional[str] = Field(
        default=None, description="Preferred appointment date in YYYY-MM-DD format."
    )


class IntentClassification(BaseModel):
    """Structured response from the intent classifier."""

    intent: Literal["knowledge_base", "appointment", "casual_conversation", "other"] = (
        Field(
            default="other", description="The classified intent of the user's message."
        )
    )
    confidence: Literal["high", "medium", "low"] = Field(
        default="low", description="How confident the model is in this classification."
    )
    reason: str = Field(
        default=None,
        description="One short sentence explaining why this intent was chosen.",
    )


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    intent_classification: NotRequired[dict]
    appointment: NotRequired[dict]
    response: NotRequired[str]
