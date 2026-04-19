import os
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
from retriever import retrieve
from tools import track_order

load_dotenv()

llm = ChatOpenAI(
    model="llama-3.3-70b-versatile",
    openai_api_key=os.getenv("GROQ_API_KEY"),
    openai_api_base="https://api.groq.com/openai/v1",
    temperature=0.3,
)

class AgentState(TypedDict):
    messages: List
    memory: dict
    route: str
    context: str
    tool_result: str
    answer: str

def extract_order_id(text: str) -> Optional[str]:
    """Robust extraction - handles: order id 123, order id- 123, #123, id:123, just 123"""
    patterns = [
        r'order\s*(?:id|number|#|no\.?)?\s*[-:–]?\s*(\d+)',   # order id- 123, order id: 123
        r'(?:id|#|no\.?)\s*[-:–]?\s*(\d+)',                    # id- 123, #123
        r'\b(\d{3,6})\b',                                       # bare number 3-6 digits
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None

def memory_node(state: AgentState) -> AgentState:
    last_msg = state["messages"][-1].content if state["messages"] else ""
    memory = state.get("memory", {})
    oid = extract_order_id(last_msg)
    if oid:
        memory["order_id"] = oid
    name_match = re.search(r"(?:my name is|i am|call me)\s+([A-Za-z]+)", last_msg, re.IGNORECASE)
    if name_match:
        memory["user_name"] = name_match.group(1).capitalize()
    state["memory"] = memory
    return state

ORDER_KEYWORDS = [
    "where is my order", "track", "order status", "where is it",
    "delivery status", "shipped", "dispatched", "when will it arrive",
    "my order", "order id", "order number", "track order", "order #",
    "check my order", "find my order", "locate my order"
]
UNKNOWN_KEYWORDS = [
    "ceo", "founder", "owner", "who made", "company name",
    "headquarters", "stock price", "investment", "valuation", "salary"
]

def router_node(state: AgentState) -> AgentState:
    last_msg = state["messages"][-1].content.lower()
    memory = state.get("memory", {})
    # Route to order if tracking keywords present
    if any(kw in last_msg for kw in ORDER_KEYWORDS):
        state["route"] = "order"
    # Also route to order if memory has order_id AND user seems to be asking about it
    elif memory.get("order_id") and any(w in last_msg for w in ["where", "status", "it", "update", "arrived"]):
        state["route"] = "order"
    elif any(kw in last_msg for kw in UNKNOWN_KEYWORDS):
        state["route"] = "unknown"
    else:
        state["route"] = "faq"
    return state

def retrieval_node(state: AgentState) -> AgentState:
    last_msg = state["messages"][-1].content
    state["context"] = retrieve(last_msg, n_results=2)
    return state

def order_node(state: AgentState) -> AgentState:
    last_msg = state["messages"][-1].content
    memory = state.get("memory", {})
    # Prefer order ID from current message, then memory
    oid = extract_order_id(last_msg) or memory.get("order_id")
    if oid:
        # Save to memory
        memory["order_id"] = oid
        state["memory"] = memory
        state["tool_result"] = track_order(oid)
    else:
        state["tool_result"] = "NO_ORDER_ID"
    return state

def unknown_node(state: AgentState) -> AgentState:
    state["tool_result"] = "UNKNOWN"
    state["context"] = ""
    return state

def answer_node(state: AgentState) -> AgentState:
    last_msg = state["messages"][-1].content
    route = state.get("route", "faq")
    context = state.get("context", "")
    tool_result = state.get("tool_result", "")

    history = ""
    for msg in state["messages"][:-1][-6:]:
        role = "User" if isinstance(msg, HumanMessage) else "Assistant"
        history += f"{role}: {msg.content}\n"

    # Out of scope
    if route == "unknown" or tool_result == "UNKNOWN":
        answer = ("I don't have that information. For queries outside our e-commerce support, "
                  "please contact our team at support@shopassist.com or call 1800-123-4567.")
        state["answer"] = answer
        state["messages"].append(AIMessage(content=answer))
        return state

    # No order ID provided
    if tool_result == "NO_ORDER_ID":
        answer = ("To track your order, I'll need your order ID. "
                  "Could you share it? (e.g. 'My order ID is 123')\n\n"
                  "💡 Test order IDs: 123, 456, 789, 321, 654")
        state["answer"] = answer
        state["messages"].append(AIMessage(content=answer))
        return state

    # Order tracking
    if route == "order":
        try:
            system = SystemMessage(content=(
                "You are ShopAssist, a friendly e-commerce support agent.\n"
                f"The order tracking system returned:\n{tool_result}\n\n"
                "Present this info clearly and warmly. Use the exact status, item name, courier, and ETA from the result."
            ))
            response = llm.invoke([system, HumanMessage(content=last_msg)])
            answer = response.content
        except Exception:
            answer = tool_result  # fallback
        state["answer"] = answer
        state["messages"].append(AIMessage(content=answer))
        return state

    # FAQ
    if context:
        try:
            system = SystemMessage(content=(
                "You are ShopAssist, a helpful e-commerce customer support agent.\n"
                f"Use ONLY this knowledge base:\n\n{context}\n\n"
                "Rules:\n"
                "- Answer from knowledge base only, be concise and friendly\n"
                "- Never make up information not in the KB\n"
                "- If not in KB: say 'I don't have that info. Contact support@shopassist.com'\n"
                f"Conversation history:\n{history}"
            ))
            response = llm.invoke([system, HumanMessage(content=last_msg)])
            answer = response.content
        except Exception:
            answer = "I'm having trouble connecting right now. Please contact support@shopassist.com or call 1800-123-4567."
    else:
        answer = "I don't have that information. Please contact our support team at support@shopassist.com or call 1800-123-4567."

    state["answer"] = answer
    state["messages"].append(AIMessage(content=answer))
    return state

def route_decision(state: AgentState) -> str:
    return state.get("route", "faq")

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("memory", memory_node)
    graph.add_node("router", router_node)
    graph.add_node("retrieval", retrieval_node)
    graph.add_node("order", order_node)
    graph.add_node("unknown", unknown_node)
    graph.add_node("answer", answer_node)
    graph.set_entry_point("memory")
    graph.add_edge("memory", "router")
    graph.add_conditional_edges("router", route_decision, {
        "faq": "retrieval", "order": "order", "unknown": "unknown",
    })
    graph.add_edge("retrieval", "answer")
    graph.add_edge("order", "answer")
    graph.add_edge("unknown", "answer")
    graph.add_edge("answer", END)
    return graph.compile()

agent = build_graph()

def run_agent(user_input: str, state: dict) -> tuple[str, dict]:
    if "messages" not in state:
        state["messages"] = []
    if "memory" not in state:
        state["memory"] = {}
    state["messages"].append(HumanMessage(content=user_input))
    state.update({"context": "", "tool_result": "", "route": "", "answer": ""})
    try:
        result = agent.invoke(state)
        answer = result.get("answer", "Sorry, I couldn't process that. Please try again.")
        state["messages"] = result["messages"]
        state["memory"] = result.get("memory", {})
    except Exception:
        answer = "Something went wrong. Please try again or contact support@shopassist.com."
    return answer, state