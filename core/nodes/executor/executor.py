import json
from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Any, Dict, List

from core.nodes.shared import AgentState

MAX_PARALLEL = 4



def _plan_steps(plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not plan or not plan.get("requires_tools", True):
        return []
    steps = plan.get("steps", [])
    return [step for step in steps if isinstance(step, dict)]

def _jsonable(value: Any) -> Any:
    try:
        json.dumps(value, ensure_ascii=False)
        return value
    except TypeError:
        return str(value)


def _run_tool(agent: Any, step: Dict[str, Any]) -> Dict[str, Any]:
    tool_name = step.get("tool", "")
    args = step.get("args", {}) or {}
    if not isinstance(args, dict):
        args = {}

    tool = agent.tool_map.get(tool_name)
    if not tool:
        return {
            "ok": False,
            "tool": tool_name,
            "error": "tool_not_found",
            "available_tools": sorted(agent.tool_map.keys()),
        }

    try:
        output = tool.invoke(args)
        return {
            "ok": True,
            "tool": tool_name,
            "args": args,
            "output": _jsonable(output),
        }
    except Exception as exc:
        return {
            "ok": False,
            "tool": tool_name,
            "args": args,
            "error": str(exc),
        }

def _short_step(step: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": step.get("id"),
        "tool": step.get("tool"),
        "args": step.get("args", {}),
        "depends_on": step.get("depends_on", []),
    }

def _execute_steps(agent: Any, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
    pending = {step["id"]: step for step in steps}
    results: Dict[str, Any] = {}

    while pending:
        _mark_failed_dependencies(pending, results)

        ready = _get_ready_steps(pending, results)

        if not ready:
            _mark_remaining_as_invalid(pending, results)
            break

        _execute_ready_steps(agent, ready, pending, results)

    return results


def _mark_failed_dependencies(
    pending: Dict[str, Dict[str, Any]],
    results: Dict[str, Any],
) -> None:
    skipped = []

    for step_id, step in pending.items():
        failed_deps = [
            dep
            for dep in step.get("depends_on", [])
            if dep in results and not results[dep].get("ok", False)
        ]

        if failed_deps:
            results[step_id] = {
                "ok": False,
                "tool": step.get("tool"),
                "error": "dependency_failed",
                "failed_dependencies": failed_deps,
            }
            skipped.append(step_id)

    for step_id in skipped:
        pending.pop(step_id, None)


def _get_ready_steps(
    pending: Dict[str, Dict[str, Any]],
    results: Dict[str, Any],
) -> List[Dict[str, Any]]:
    return [
        step
        for step in pending.values()
        if all(
            dep in results
            for dep in step.get("depends_on", [])
        )
    ]


def _mark_remaining_as_invalid(
    pending: Dict[str, Dict[str, Any]],
    results: Dict[str, Any],
) -> None:
    for step_id, step in pending.items():
        results[step_id] = {
            "ok": False,
            "tool": step.get("tool"),
            "error": "dependency_cycle_or_missing_dependency",
        }


def _execute_ready_steps(
    agent: Any,
    ready: List[Dict[str, Any]],
    pending: Dict[str, Dict[str, Any]],
    results: Dict[str, Any],
) -> None:
    workers = min(MAX_PARALLEL, len(ready))

    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_map = {
            executor.submit(_run_tool, agent, step): step
            for step in ready
        }

        for step in ready:
            pending.pop(step["id"], None)
            agent.emit("TOOL_START", _short_step(step))

        for future in as_completed(future_map):
            step = future_map[future]
            output = _get_future_result(future, step)

            results[step["id"]] = output

            agent.emit(
                "TOOL_DONE" if output.get("ok") else "TOOL_ERROR",
                {step["id"]: output},
            )


def _get_future_result(future, step: Dict[str, Any]) -> Dict[str, Any]:
    try:
        return future.result()
    except Exception as exc:
        return {
            "ok": False,
            "tool": step.get("tool"),
            "error": str(exc),
        }

def executor_node(agent: Any, state: AgentState) -> Dict[str, Dict[str, Any]]:
    plan = state.get("plan", {})
    steps = _plan_steps(plan)

    if not steps:
        result = {"steps": {}, "summary": "Nessun tool richiesto."}
        agent.emit("EXECUTION", result)
        return {"result": result}

    agent.emit("EXECUTION", f"Avvio {len(steps)} step.")
    results = _execute_steps(agent, steps)
    result = {"steps": results}
    agent.emit("EXECUTION", result)
    return {"result": result}
