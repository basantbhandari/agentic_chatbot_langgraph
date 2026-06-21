from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.config.llm import llm, intent_classification_structure_llm, appointment_booking_structure_llm
from app.models.schema import ChatState, IntentClassification, AppointmentBooking

def handle_intent_classification(state: ChatState):
    """Classify the user's message using structured LLM output."""
    system_prompt = """
    You are an intent classifier for a medical or service assistant.
    Given a user message, classify it into EXACTLY one of these intents:  

    - knowledge_base -> The user is asking for information that may exist in company documents, FAQs, policies, services, procedures, products, pricing, business information, or uploaded knowledge base documents.
    - appointment  → The user wants to book, schedule, or discuss an appointment (full name, phone number, email, preferred date).
    - casual_conversation -> Greetings, small talk, thanks, jokes, social conversation, or general chat.
    - other        → The intent cannot be determined confidently.

    Return structured output with intent, confidence, and a short reason.
    """
    last_n_user_conversations = state["messages"][-6:]
    result: IntentClassification = intent_classification_structure_llm.invoke([
        SystemMessage(content=system_prompt),
        *last_n_user_conversations,
    ])
    return {
        "intent_classification": {
            "intent": result.intent,
            "confidence": result.confidence,
            "reason": result.reason,
        },
    }



def handle_knowledge_base(state: ChatState):
    """Handle knowledge base / FAQ queries with memory + RAG."""

    last_user_message = state["messages"][-1].content
    from app.dependencies import retriever
    retrieved_documents = retriever.invoke(last_user_message)
    context = "\n\n".join(
        f"[Document {i+1}]\n{doc.page_content}"
        for i, doc in enumerate(retrieved_documents)
    ) if retrieved_documents else "No relevant documents found."

    system_prompt = f"""
    You are a helpful knowledge base assistant.
    
    You MUST use:
    1. user query
    2. Retrieved context (for factual answers)
    
    If the answer is not in context, say so clearly.
    
    Context:
    {context}
    """
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=last_user_message),
    ])
    return {
        "response": response.content,
        "messages": [AIMessage(content=response.content)]
    }


def handle_appointment(state: ChatState):
    """LangGraph node for conversational appointment booking."""
    system_prompt = """
    You are an appointment booking assistant.

    Extract appointment details from the Human conversation.

    Fields to extract:
    - name: user's full name
    - phone_number: user's phone number
    - email: user's email address
    - preferred_date: preferred appointment date (extract the natural language date into yyyy-mm-dd string format based on current date)

    Rules:
    - Do NOT guess missing values
    - Only extract explicitly mentioned information
    - If something is missing, leave it empty
    """
    user_message = state["messages"][-1].content
    result: AppointmentBooking = appointment_booking_structure_llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message),
    ])
    # merge extracted fields safely
    if result.name:
        state.get("appointment", {})["name"] = result.name

    if result.phone_number:
        state.get("appointment", {})["phone_number"] = result.phone_number

    if result.email:
        state.get("appointment", {})["email"] = result.email

    if result.preferred_date:
        state.get("appointment", {})["preferred_date"] = result.preferred_date

    missing_fields = [
        key for key in ["name", "phone_number", "email", "preferred_date"]
        if not  state.get("appointment", {}).get(key)
    ]

    if missing_fields:
        next_field = missing_fields[0]

        questions = {
            "name": "May I know your full name?",
            "phone_number": "Could you please provide your phone number?",
            "email": "What is your email address?",
            "preferred_date": "What date would you prefer for the appointment?"
        }

        next_question = questions[next_field]

        return {
            "appointment": state.get("appointment", {}),
            "response": next_question,
            "messages": [AIMessage(content=next_question)]
        }


    confirmation = f"""
    Appointment Confirmed!

    Name: {state.get("appointment", {})['name']}
    Phone: {state.get("appointment", {})['phone_number']}
    Email: {state.get("appointment", {})['email']}
    Preferred Date: {state.get("appointment", {})['preferred_date']}
    """

    return {
        "appointment": state.get("appointment", {}),
        "response": confirmation,
        "messages": [AIMessage(content=confirmation)]
    }


def handle_casual_conversation(state: ChatState):
    """Handle casual / small-talk messages."""
    last_n_user_conversations = state["messages"][-6:]
    messages = [
        SystemMessage(content="You are a friendly assistant."),
        *last_n_user_conversations,
    ]
    response = llm.invoke(messages)
    return {"response": response.content, "messages": [AIMessage(content=response.content)]}


def handle_other(state: ChatState):
    """Fallback — escalate or ask for clarification."""
    classification = state["intent_classification"]

    msg = (
        "I'm not quite sure what you need help with. Could you rephrase or "
        "let me know if you're looking for information, want to book an appointment, "
        f"or something else? (Reason: {classification['reason']})"
    )
    return {"response": msg, "messages": [AIMessage(content=msg)]}


def handle_low_confidence(state: ChatState) -> dict:
    """Ask for clarification when classifier confidence is low."""
    classification = state["intent_classification"]

    msg = (
        f"I think you might be asking about **{classification['intent'].replace('_', ' ')}**, "
        f"but I'm not fully sure ({classification['reason']}). "
        "Could you give me a bit more detail so I can help you better?"
    )
    return {"response": msg, "messages": [AIMessage(content=msg)]}


def route_intent(state: ChatState) -> str:
    """
    Primary router: low confidence always goes to clarification,
    otherwise route by intent.
    """
    classification = state["intent_classification"]

    if classification["confidence"] == "low":
        return "low_confidence"

    routes = {
        "knowledge_base": "knowledge_base",
        "appointment": "appointment",
        "casual_conversation": "casual_conversation",
        "other": "other",
    }
    return routes[classification["intent"]]
