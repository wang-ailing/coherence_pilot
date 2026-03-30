from core.protocol_state import ProtocolSpec, VerificationResult
import json
import os

class DataSynthesizer:
    """
    Data Synthesizer:
    Outputs three types of high-quality training data generated during the verification process.
    - Type A: Debugging CoT (Error Code + Trace -> Chain of Thought -> Fixed Code)
    - Type B: State Reasoning (State + Message -> Next State -> Reason)
    - Type C: Invariant Data (Protocol -> Invariant -> Explanation)
    """
    def __init__(self, output_dir: str = "dataset"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def synthesize_type_a(self, error_spec: ProtocolSpec, trace: str, cot_reasoning: str, fixed_spec: ProtocolSpec):
        """
        Type A — Debugging CoT:
        Teaches LLM how to recover from errors and improve logical reasoning.
        """
        print(f"[DataSynthesizer] Synthesizing Type A Data (Debugging CoT)...")
        data = {
            "type": "A_Debugging_CoT",
            "input": {
                "error_code": error_spec.murphi_code,
                "counterexample_trace": trace
            },
            "chain_of_thought": cot_reasoning,
            "output": fixed_spec.murphi_code
        }
        self._append_to_file("type_a_data.jsonl", data)

    def synthesize_type_b(self, current_state: dict, message: str, next_state: dict, reason: str):
        """
        Type B — State Reasoning:
        Provides supervision signal for exact state machine simulation.
        """
        print(f"[DataSynthesizer] Synthesizing Type B Data (State Reasoning)...")
        data = {
            "type": "B_State_Reasoning",
            "input": {
                "current_state": current_state,
                "message": message
            },
            "output": next_state,
            "reason": reason
        }
        self._append_to_file("type_b_data.jsonl", data)

    def synthesize_type_c(self, spec: ProtocolSpec, invariant: str, explanation: str):
        """
        Type C — Invariant Data:
        Enhances LLM understanding of proof languages, code semantics, and safety properties.
        """
        print(f"[DataSynthesizer] Synthesizing Type C Data (Invariant Data)...")
        data = {
            "type": "C_Invariant_Data",
            "input": spec.murphi_code,
            "invariant": invariant,
            "explanation": explanation
        }
        self._append_to_file("type_c_data.jsonl", data)

    def _append_to_file(self, filename: str, data: dict):
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
