from typing import Dict, Any, List

from pydantic import Field, BaseModel


class PlanStep(BaseModel):
    id: str
    tool: str
    args: Dict[str, Any] = Field(default_factory=dict)
    depends_on: List[str] = Field(default_factory=list)
    purpose: str = ""


class Plan(BaseModel):
    requires_tools: bool = True
    strategy: str = ""
    thought_tree: List[str] = Field(default_factory=list)
    steps: List[PlanStep] = Field(default_factory=list)
    final_response_hint: str = ""


# Backward-compatible alias for older imports/snippets.
Step = PlanStep