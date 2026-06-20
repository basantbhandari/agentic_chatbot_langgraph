from langchain_core.messages import SystemMessage, HumanMessage

from app.config.llm import llm, intent_classification_structure_llm
from app.models.schema import ChatState, IntentClassification


def chat_node(state: ChatState):

    # take user query from state
    messages = state.messages

    # send to config
    response = llm.invoke(messages)

    # response store state
    return {'messages': [response]}


def classify_intent_node(state: ChatState):
    """Classify the user's message using structured LLM output."""
    system_prompt = """
    You are an intent classifier for a medical or service assistant.
    Given a user message, classify it into EXACTLY one of these intents:  

    - knowledge_base -> The user is asking for information that may exist in company documents, FAQs, policies, services, procedures, products, pricing, business information, or uploaded knowledge base documents.
    - appointment  → The user wants to book, reschedule, cancel, check, or discuss an appointment.
    - casual_conversation -> Greetings, small talk, thanks, jokes, social conversation, or general chat.
    - other        → The intent cannot be determined confidently.

    Return structured output with intent, confidence, and a short reason.
    """

    result: IntentClassification = intent_classification_structure_llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=state.messages[-1].content),
    ])

    return {
        "intent": result.intent,
        "confidence": result.confidence,
        "reason": result.reason,
    }
