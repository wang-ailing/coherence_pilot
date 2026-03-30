from pydantic import BaseModel
from typing import List, Optional, Dict

class ProtocolSpec(BaseModel):
    name: str
    states: List[str]
    events: List[str]
    transitions: Dict[str, Dict[str, str]]  # State -> {Event -> Next_State}
    murphi_code: str
    lean_code: str

class VerificationResult(BaseModel):
    is_success: bool
    counterexample_trace: Optional[str] = None
    failed_invariant: Optional[str] = None
    stuck_state: Optional[str] = None
