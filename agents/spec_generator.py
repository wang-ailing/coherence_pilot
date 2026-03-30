from core.llm_client import LLMClient
from core.protocol_state import ProtocolSpec

class SpecGeneratorAgent:
    """
    Spec Generator Agent: 
    Takes a natural language request from the user and generates
    the initial Murphi/Lean specification code for the Cache Coherence protocol.
    """
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.system_prompt = (
            "You are an expert formal verification engineer specializing in Cache Coherence protocols. "
            "Your task is to translate user natural language descriptions into formal Murphi and Lean 4 specifications."
        )

    def generate(self, user_prompt: str) -> ProtocolSpec:
        """
        Generate the initial formal specification based on the user's description.
        """
        print(f"[SpecGenerator] Generating specification for: {user_prompt}")
        prompt = (
            f"User requested a cache coherence protocol: {user_prompt}\n"
            f"Please generate the complete formal protocol specification including its states, events, "
            f"transitions, as well as the initial Murphi and Lean 4 code for model checking and theorem proving."
        )
        
        # In a real implementation, this would use self.llm.generate_structured(prompt, ProtocolSpec, self.system_prompt)
        # Here we mock it for the framework skeleton.
        return ProtocolSpec(
            name="GeneratedProtocol",
            states=["I", "S", "E", "M"],
            events=["PrRd", "PrWr", "BusRd", "BusRdX"],
            transitions={},
            murphi_code="-- Mock Murphi Code Here",
            lean_code="-- Mock Lean Code Here"
        )
