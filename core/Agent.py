import os
import threading
from functools import partial
from pathlib import Path
from typing import Annotated, Any, Callable, Dict, Optional, TypedDict

from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages

from core.nodes.critic.critic import critic_node
from core.nodes.executor.executor import executor_node
from core.nodes.final.final import final_node
from core.nodes.memory.long_term_memory import LongTermMemory
from core.nodes.memory.memory import memory_node
from core.nodes.planning.planning import planner_node
from core.nodes.reasoning.reasoning import reasoner_node
from core.nodes.shared import extract_json, json_dumps, AgentState
from tools.tools import ToolRegistry


def setup_langsmith(project: str = "local-agent") -> None:
    """Enable LangSmith tracing when an API key is available."""

    api_key = os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY")
    if not api_key:
        os.environ.setdefault("LANGSMITH_TRACING", "false")
        os.environ.setdefault("LANGCHAIN_TRACING_V2", "false")
        return

    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_API_KEY"] = api_key
    os.environ.setdefault("LANGSMITH_PROJECT", project)
    os.environ.setdefault("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")

    # Backward-compatible LangChain env names.
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = api_key
    os.environ.setdefault("LANGCHAIN_PROJECT", project)
    os.environ.setdefault("LANGCHAIN_ENDPOINT", os.environ["LANGSMITH_ENDPOINT"])


def _load_md(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return ""
    try:
        return p.read_text(encoding="utf-8").strip()
    except UnicodeDecodeError:
        return p.read_text(encoding="cp1252", errors="ignore").strip()




class AgentInstance:
    """LangGraph based local agent with memory, planning, tools and critique."""

    MAX_REPLAN = 2

    def __init__(self, model_name: str, langsmith_project: str = "local-agent", verbose: bool = False):
        setup_langsmith(langsmith_project)

        self.verbose = verbose
        self._progress_callback: Optional[Callable[[str, Any], None]] = None
        self._emit_lock = threading.Lock()

        self.llm = ChatOllama(model=model_name, temperature=0.2)

        self.tools_registry = ToolRegistry()
        self.tools = self.tools_registry.get_tools()
        self.tool_map = self.tools_registry.tools
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.tool_catalog = self._build_tool_catalog()

        self.role = _load_md("knowledge/IO/role.md")
        self.personality = _load_md("knowledge/IO/personality.md")
        self.trading_context = _load_md("knowledge/IO/trading.md")

        self.long_memory = LongTermMemory()
        self.checkpointer = MemorySaver()
        self.graph = self._build_graph()

    def _build_tool_catalog(self) -> str:
        specs = []
        for tool in self.tools:
            try:
                args_schema = getattr(tool, "args", None) or {}
            except Exception:
                args_schema = {}
            specs.append({
                "name": tool.name,
                "description": (tool.description or "").strip(),
                "args_schema": args_schema,
            })
        return json_dumps(specs)

    def _route_after_reasoner(self, state: AgentState) -> str:
        return "planner" if state.get("requires_tools", False) else "final"

    def _route_after_critic(self, state: AgentState) -> str:
        critique = state.get("critique", {}) or {}
        if critique.get("retry") and int(state.get("attempt", 0) or 0) <= self.MAX_REPLAN:
            return "planner"
        return "final"

    def _console_progress(self, event: str, payload: Any) -> None:
        print(f"\n=== {event} ===")
        if isinstance(payload, (dict, list)):
            print(json_dumps(payload))
        else:
            print(payload)


    def _build_graph(self):
        graph = StateGraph(AgentState)
        graph.add_node("memory", partial(memory_node, self))
        graph.add_node("reasoner", partial(reasoner_node, self))
        graph.add_node("planner", partial(planner_node, self))
        graph.add_node("executor", partial(executor_node, self))
        graph.add_node("critic", partial(critic_node, self))
        graph.add_node("final", partial(final_node, self))

        graph.set_entry_point("memory")
        graph.add_edge("memory", "reasoner")
        graph.add_conditional_edges("reasoner", self._route_after_reasoner,
                                    {"planner": "planner", "final": "final"}, )
        graph.add_edge("planner", "executor")
        graph.add_edge("executor", "critic")
        graph.add_conditional_edges("critic", self._route_after_critic,
                                    {"planner": "planner", "final": "final"}, )
        graph.add_edge("final", END)

        return graph.compile(checkpointer=self.checkpointer)

    def _validate_model(self, schema, data):
        if isinstance(data, schema):
            return data
        if hasattr(schema, "model_validate"):
            return schema.model_validate(data)
        return schema.parse_obj(data)

    # Invokes
    def invoke(self, user_input: str,  thread_id: str = "default", show_progress: bool = False) -> str:
        previous_callback = self._progress_callback
        if show_progress:
            self._progress_callback = self._console_progress

        try:
            result = self.graph.invoke(
                {
                    "messages": [HumanMessage(content=user_input)],
                    "attempt": 0,
                },
                config={"configurable": {"thread_id": thread_id}},
            )
        finally:
            self._progress_callback = previous_callback

        return self.get_message_text(result["messages"][-1])

    def structured_invoke(self, schema, prompt: str, fallback):
        try:
            structured = self.llm.with_structured_output(schema)
            parsed = structured.invoke(prompt)
            return self._validate_model(schema, parsed)
        except Exception:
            pass
        try:
            raw = self.llm.invoke(
                prompt
                + "\n\nRispondi SOLO con JSON valido per lo schema richiesto."
            )
            data = extract_json(self.get_message_text(raw))
            return self._validate_model(schema, data)
        except Exception:
            return fallback

    # Emitter
    def emit(self, event: str, payload: Any) -> None:
        if not self.verbose and not self._progress_callback:
            return
        callback = self._progress_callback or self._console_progress
        with self._emit_lock:
            callback(event, payload)

    # message handling
    def get_latest_user_text(self, state: AgentState) -> str:
        for msg in reversed(state.get("messages", [])):
            if isinstance(msg, HumanMessage):
                return self.get_message_text(msg)
        messages = state.get("messages", [])
        return self.get_message_text(messages[-1]) if messages else ""

    def get_message_text(self, message: Any) -> str:
        content = getattr(message, "content", message)
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            chunks = []
            for item in content:
                if isinstance(item, dict):
                    chunks.append(str(item.get("text") or item.get("content") or ""))
                else:
                    chunks.append(str(item))
            return "\n".join(chunk for chunk in chunks if chunk)
        return str(content)