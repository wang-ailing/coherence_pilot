from core.protocol_state import ProtocolSpec, VerificationResult
from core.runtime_config import load_runtime_config
from verifiers.lean_tool import LeanTool

class LeanRunner:
    """
    Lean Prover Interface:
    Interacts with the Lean 4 environment to perform inductive invariant proofs.
    """
    def __init__(self, lean_path: str | None = None):
        default_path = load_runtime_config()["lean"]["binary"]
        self.lean_path = lean_path or default_path
        self.tool = LeanTool(lean_path=self.lean_path)

    def run_proof(self, spec: ProtocolSpec) -> VerificationResult:
        """
        Executes the theorem proving in Lean 4 via the standalone LeanTool.
        Returns success if proved, or the stuck state if the proof cannot be completed.
        """
        print(f"[LeanRunner] Running Lean 4 to prove inductive invariants for '{spec.name}'...")

        result = self.tool.run_proof(spec.lean_code)
        
        if result["status"] == "success":
            return VerificationResult(is_success=True)

        stuck_state = result.get("unsolved_goals") or str(result.get("errors"))
        return VerificationResult(
            is_success=False,
            stuck_state=f"unsolved goals: \n {stuck_state}"
        )
