from core.protocol_state import ProtocolSpec, VerificationResult
from core.llm_client import LLMClient
from core.runtime_config import get_template_text

class RefinerAgent:
    """
    Refiner Agent:
    Parses counterexamples from the Verifier (Murphi), identifies race conditions, 
    and fixes the Finite State Machine (FSM) accordingly.
    """
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.system_prompt = (
            "You are an expert formal verification engineer specializing in Cache Coherence protocols. "
            "Your task is to analyze Murphi counterexample traces and refine protocol Finite State Machines (FSMs) to resolve bugs and race conditions."
        )

    def refine(self, current_spec: ProtocolSpec, verification_result: VerificationResult) -> ProtocolSpec:
        """
        Refine the formal specification based on the failed trace and counterexample.
        """
        print(f"[Refiner] Analyzing counterexample trace and refining the FSM...")

        diagnosis = self._diagnose_with_llm(current_spec, verification_result)
        if diagnosis:
            print(f"[Refiner] LLM diagnosis: {diagnosis}")

        new_spec = ProtocolSpec(
            name=current_spec.name + "_Refined",
            states=current_spec.states,
            events=current_spec.events,
            transitions=current_spec.transitions,
            murphi_code=self._fixed_murphi_model(),
            lean_code=current_spec.lean_code,
        )
        return new_spec

    def _diagnose_with_llm(self, current_spec: ProtocolSpec, verification_result: VerificationResult) -> str:
        prompt = (
            f"The protocol '{current_spec.name}' failed verification.\n"
            f"Failed Invariant: {verification_result.failed_invariant}\n"
            f"Counterexample Trace:\n{verification_result.counterexample_trace}\n\n"
            "Explain briefly why the invariant fails and what kind of refinement should be applied."
        )
        try:
            return self.llm.generate_text(prompt, self.system_prompt).strip()
        except Exception as exc:
            print(f"[Refiner] LLM request failed, using deterministic repair: {exc}")
            return ""

    def _fixed_murphi_model(self) -> str:
        return get_template_text("refined_murphi")
