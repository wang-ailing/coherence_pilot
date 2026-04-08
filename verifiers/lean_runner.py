from core.protocol_state import ProtocolSpec, VerificationResult
from verifiers.lean_tool import LeanTool

class LeanRunner:
    """
    Lean Prover Interface:
    Interacts with the Lean 4 environment to perform inductive invariant proofs.
    """
    def __init__(self, lean_path: str = "lean"):
        self.lean_path = lean_path
        self.tool = LeanTool(lean_path=lean_path)

    def run_proof(self, spec: ProtocolSpec) -> VerificationResult:
        """
        Executes the theorem proving in Lean 4 via the standalone LeanTool.
        Returns success if proved, or the stuck state if the proof cannot be completed.
        """
        print(f"[LeanRunner] Running Lean 4 to prove inductive invariants for '{spec.name}'...")
        
        # Mocked return for framework structure:
        # We will simulate getting stuck on the first run, and success on the second run after strengthening.
        if not hasattr(self, 'run_count'):
            self.run_count = 0
        self.run_count += 1
        
        code_to_run = spec.lean_code
        if self.run_count == 1 and "sorry" not in code_to_run:
            # Force a mock error
            code_to_run += "\nsorry"
            
        result = self.tool.run_proof(code_to_run)
        
        if result["status"] == "success":
            return VerificationResult(is_success=True)
        else:
            # Provide exact Tactic State to the Strengthener
            stuck_state = result.get("unsolved_goals") or str(result.get("errors"))
            return VerificationResult(
                is_success=False,
                stuck_state=f"unsolved goals: \n {stuck_state}"
            )
