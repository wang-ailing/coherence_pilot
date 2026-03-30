import click
from core.llm_client import LLMClient
from agents.spec_generator import SpecGeneratorAgent
from agents.refiner import RefinerAgent
from agents.strengthener import StrengthenerAgent
from verifiers.murphi_runner import MurphiRunner
from verifiers.lean_runner import LeanRunner
from verifiers.pruning import PruningModule
from data.synthesizer import DataSynthesizer

class CoherencePilot:
    def __init__(self):
        self.llm = LLMClient()
        self.spec_generator = SpecGeneratorAgent(self.llm)
        self.refiner = RefinerAgent(self.llm)
        self.strengthener = StrengthenerAgent(self.llm)
        
        self.murphi = MurphiRunner()
        self.lean = LeanRunner()
        self.pruning = PruningModule()
        self.data_synth = DataSynthesizer()

    def run(self, user_request: str):
        print(f"\n=== Coherence Pilot Started ===")
        print(f"User Request: {user_request}\n")
        
        # 1. Spec Generation
        spec = self.spec_generator.generate(user_request)
        
        # 2. Murphi Verification & Refinement Loop
        max_retries = 3
        murphi_success = False
        
        for attempt in range(max_retries):
            print(f"\n--- Murphi Verification (Attempt {attempt + 1}) ---")
            murphi_res = self.murphi.run_verification(spec)
            
            if murphi_res.is_success:
                murphi_success = True
                print("[Pilot] Murphi verification PASSED.")
                break
            else:
                print(f"[Pilot] Murphi verification FAILED. Counterexample found.")
                # Pruning step (mock)
                vars_to_prune = self.pruning.extract_variables_from_trace(murphi_res.counterexample_trace)
                
                # Refiner Agent fixes the spec
                fixed_spec = self.refiner.refine(spec, murphi_res)
                
                # Synthesize Type A Data (Debugging CoT)
                self.data_synth.synthesize_type_a(
                    error_spec=spec,
                    trace=murphi_res.counterexample_trace,
                    cot_reasoning="Analyzed trace, identified race condition on BusRdX, updated FSM...",
                    fixed_spec=fixed_spec
                )
                
                spec = fixed_spec
                
        if not murphi_success:
            print("[Pilot] Failed to pass Murphi verification within max retries.")
            return

        # 3. Lean Prover Loop
        lean_success = False
        for attempt in range(max_retries):
            print(f"\n--- Lean 4 Theorem Proving (Attempt {attempt + 1}) ---")
            lean_res = self.lean.run_proof(spec)
            
            if lean_res.is_success:
                lean_success = True
                print("[Pilot] Lean 4 proof PASSED. Machine-verified proof generated!")
                # Synthesize Type C Data
                self.data_synth.synthesize_type_c(
                    spec=spec,
                    invariant="Only one node in M state",
                    explanation="Ensures single-writer multiple-reader consistency."
                )
                break
            else:
                print("[Pilot] Lean 4 proof STUCK. Strengthening lemmas...")
                new_lean_code = self.strengthener.strengthen(spec, lean_res.stuck_state)
                spec.lean_code = new_lean_code
                
        if lean_success:
            print("\n=== Coherence Pilot Completed Successfully ===")
        else:
            print("\n=== Coherence Pilot Failed during Lean Proof ===")


@click.command()
@click.option('--prompt', default="设计一个包含 E 状态的 MESI 协议", help='User natural language request for protocol.')
def cli(prompt):
    """
    Coherence Pilot: LLM + Agent Framework for Cache Coherence Verification.
    """
    pilot = CoherencePilot()
    pilot.run(prompt)

if __name__ == '__main__':
    cli()
