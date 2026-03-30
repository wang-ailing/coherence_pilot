from core.protocol_state import VerificationResult
from typing import List

class PruningModule:
    """
    Pruning Module (Tree of Thoughts inspired):
    Extracts key variables from Murphi counterexamples to prune the search space.
    Maintains patterns of failed subtrees to prevent the Agent from repeating isomorphic errors,
    effectively pruning the deliberate problem-solving search tree.
    """
    def __init__(self):
        self.failed_patterns = set()
        self.search_tree = {} # To keep track of explored paths

    def extract_variables_from_trace(self, trace: str) -> List[str]:
        """
        Parses the counterexample trace to find the specific state variables
        involved in the violation.
        """
        print(f"[PruningModule] Extracting key variables from counterexample trace...")
        # Mock logic
        return ["Node1.state", "Node2.state", "Bus.msg"]

    def record_failure_pattern(self, pattern: str, state_path: str = ""):
        """
        Records a structural feature of a failed FSM subtree.
        If state_path is provided, marks that specific path as failed in the search tree.
        """
        print(f"[PruningModule] Recording failure pattern to prune future search trees.")
        self.failed_patterns.add(pattern)
        if state_path:
            self.search_tree[state_path] = "FAILED"

    def is_pruned(self, candidate_fsm: str, state_path: str = "") -> bool:
        """
        Checks if a generated candidate FSM falls into an already known failed pattern.
        Also checks if the specific search tree path is already marked as failed.
        """
        if state_path and self.search_tree.get(state_path) == "FAILED":
            print(f"[PruningModule] Path {state_path} was previously pruned.")
            return True
            
        for pattern in self.failed_patterns:
            if pattern in candidate_fsm:
                print(f"[PruningModule] FSM matches failed pattern: {pattern}")
                return True
        return False
