from langgraph.constants import START, END
from langgraph.graph import StateGraph

from app.agents.node import chat_node
from app.models.schema import ChatState
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()

graph = StateGraph(ChatState)

# add nodes
graph.add_node('chat_node', chat_node)
# add edge
graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

workflow = graph.compile(
    checkpointer=checkpointer
)