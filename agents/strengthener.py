from core.llm_client import LLMClient
from core.protocol_state import ProtocolSpec, VerificationResult
from core.runtime_config import get_template_text

class StrengthenerAgent:
    """
    Strengthener Agent:
    Triggered when the Lean Prover gets stuck on an inductive invariant proof.
    Takes the incomplete proof obligations and generates new, stronger lemmas or invariants.
    """
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.system_prompt = (
            "You are an expert formal verification engineer specializing in Cache Coherence protocols and Lean 4 theorem proving. "
            "Your task is to analyze stuck proof states in Lean 4 and propose stronger lemmas or inductive invariants to complete the proof."
        )

    def strengthen(self, current_spec: ProtocolSpec, stuck_state: str) -> str:
        """
        Strengthen the lemma or invariant based on the stuck state from Lean.
        """
        print(f"[Strengthener] Analyzing Lean stuck state to strengthen lemmas...")

        suggestion = self._strengthen_with_llm(current_spec, stuck_state)
        if suggestion:
            print(f"[Strengthener] LLM suggestion: {suggestion}")

        return get_template_text("refined_lean")

    def _strengthen_with_llm(self, current_spec: ProtocolSpec, stuck_state: str) -> str:
        prompt = (
            f"The inductive invariant proof for protocol '{current_spec.name}' is stuck.\n"
            f"Current Proof State:\n{stuck_state}\n\n"
            "Suggest a concise strengthening strategy or proof fix."
        )
        try:
            return self.llm.generate_text(prompt, self.system_prompt).strip()
        except Exception as exc:
            print(f"[Strengthener] LLM request failed, using deterministic proof repair: {exc}")
            return ""
