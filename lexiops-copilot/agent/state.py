from typing import TypedDict, Annotated, List, Optional, Dict, Any
import operator
from langchain_core.messages import BaseMessage
from .schemas import MultiStepPlan

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    planner_output: Optional[Dict[str, Any]] 
    is_approved: bool # approve plan
    is_valid: bool # validate output
    plan: Optional[MultiStepPlan]
    step_index: int
    step_outputs: Annotated[List, operator.add]
    scratchpad: List[BaseMessage]
    review_outcome: str