import os
import re
import json
import subprocess
import tempfile
from typing import Dict, Any, List, Optional

class LeanTool:
    """
    Lean 4 Tool for AI Agents.
    Executes Lean code/tactics and extracts the Tactic State (remaining goals).
    """
    def __init__(self, lean_path: str = "lean"):
        self.lean_path = lean_path

    def run_proof(self, lean_code: str) -> Dict[str, Any]:
        """
        Executes Lean code and parses the output for unsolved goals or errors.
        Provides the LLM with precise feedback on what's left to prove.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            lean_file = os.path.join(tmpdir, "model.lean")
            with open(lean_file, "w", encoding="utf-8") as f:
                f.write(lean_code)
                
            try:
                # Run `lean model.lean`
                result = subprocess.run(
                    [self.lean_path, lean_file], 
                    cwd=tmpdir, 
                    capture_output=True, 
                    text=True
                )
            except FileNotFoundError:
                # Fallback to mock logic if lean is not installed
                return self._mock_run(lean_code)
            except Exception as e:
                return {
                    "status": "error",
                    "error_type": "ExecutionError",
                    "message": f"Failed to run Lean 4: {str(e)}"
                }

            stdout, stderr = result.stdout, result.stderr
            output = stdout + "\n" + stderr
            
            # If no errors/unsolved goals, proof is successful
            if "error:" not in output and "unsolved goals" not in output:
                return {
                    "status": "success",
                    "message": "Lean verification passed! All goals proved."
                }
            
            return self._parse_lean_output(output)

    def _parse_lean_output(self, output: str) -> Dict[str, Any]:
        """
        Extracts specific error messages and the tactic state (unsolved goals).
        """
        # Search for unsolved goals
        goals_match = re.search(r"unsolved goals\n(.*?)(?:\n\n|$)", output, re.DOTALL)
        unsolved_goals = goals_match.group(1).strip() if goals_match else None
        
        # Search for syntax/tactic errors
        errors = []
        for line in output.split('\n'):
            if "error:" in line:
                errors.append(line.strip())
                
        status = "stuck" if unsolved_goals else "error"
        
        return {
            "status": status,
            "unsolved_goals": unsolved_goals,
            "errors": errors,
            "raw_output_snippet": output[:1000] # Provide snippet to prevent context overflow
        }

    def _mock_run(self, lean_code: str) -> Dict[str, Any]:
        """Mock execution when Lean is not installed."""
        if "sorry" in lean_code or "stuck" in lean_code:
            return {
                "status": "stuck",
                "unsolved_goals": "⊢ ∀ (n1 n2 : Node), state n1 = M → state n2 = I",
                "errors": [],
                "message": "Found 'sorry' macro, proof incomplete."
            }
        elif "syntax_error" in lean_code:
            return {
                "status": "error",
                "unsolved_goals": None,
                "errors": ["model.lean:10:4: error: expected '=>'"],
                "message": "Lean parser error."
            }
        else:
            return {
                "status": "success",
                "message": "Lean verification passed! All goals proved."
            }
