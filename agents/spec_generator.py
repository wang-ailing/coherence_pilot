from core.llm_client import LLMClient
from core.protocol_state import ProtocolSpec
from core.runtime_config import get_template_text

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
        metadata = self._summarize_request_with_llm(user_prompt)
        return ProtocolSpec(
            name=metadata["name"],
            states=metadata["states"],
            events=metadata["events"],
            transitions={},
            murphi_code=self._initial_buggy_murphi_model(),
            lean_code=self._initial_lean_script(metadata["name"]),
        )

    def _summarize_request_with_llm(self, user_prompt: str) -> dict:
        prompt = (
            "Summarize the requested protocol into JSON.\n"
            "Keys: name, states, events.\n"
            "Use concise strings. Keep states/events short.\n"
            f"User request: {user_prompt}"
        )
        try:
            result = self.llm.generate_json(prompt, self.system_prompt)
            return {
                "name": result.get("name", "GeneratedProtocol"),
                "states": result.get("states", ["I", "S", "E", "M"]),
                "events": result.get("events", ["PrRd", "PrWr", "BusRd", "BusRdX"]),
            }
        except Exception as exc:
            print(f"[SpecGenerator] LLM request failed, using fallback metadata: {exc}")
            return {
                "name": "GeneratedProtocol",
                "states": ["I", "S", "E", "M"],
                "events": ["PrRd", "PrWr", "BusRd", "BusRdX"],
            }

    def _initial_buggy_murphi_model(self) -> str:
        return get_template_text("initial_murphi")

    def _initial_lean_script(self, protocol_name: str) -> str:
        theorem_name = "".join(ch if ch.isalnum() else "_" for ch in protocol_name.lower())
        return get_template_text("initial_lean").replace("__THEOREM_NAME__", f"{theorem_name}_single_writer_demo")
