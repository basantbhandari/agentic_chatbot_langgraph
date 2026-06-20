from app.config.llm import llm
from app.models.schema import ChatState


def chat_node(state: ChatState):

    # take user query from state
    messages = state.messages

    # send to config
    response = llm.invoke(messages)

    # response store state
    return {'messages': [response]}
