from pydantic import BaseModel

class ReasoningDecision(BaseModel):
    """Sintesi osservabile della decisione: non contiene chain-of-thought."""

    requires_tools: bool = False
    task_summary: str = ""
    reason: str = ""



