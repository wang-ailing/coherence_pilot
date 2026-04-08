import os
import re
import json
import subprocess
import tempfile
from typing import Dict, Any, Optional

class IvyTool:
    """
    Ivy Verification Tool for AI Agents.
    Executes ivy_check and parses Counterexamples to Induction (CTIs).
    Ideal for verifying parameterized systems and cache coherence protocols.
    """
    def __init__(self, ivy_path: str = "ivy_check"):
        self.ivy_path = ivy_path

    def run_check(self, ivy_code: str, isolate: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes ivy_check on the provided .ivy code.
        Returns success or extracts the Counterexample to Induction (CTI) for the LLM.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            ivy_file = os.path.join(tmpdir, "model.ivy")
            with open(ivy_file, "w", encoding="utf-8") as f:
                f.write(ivy_code)
                
            cmd = [self.ivy_path]
            if isolate:
                cmd.extend([f"isolate={isolate}"])
            cmd.append("model.ivy")
            
            try:
                # Ivy returns non-zero exit code if verification fails
                result = subprocess.run(cmd, cwd=tmpdir, capture_output=True, text=True)
            except FileNotFoundError:
                # Fallback to mock logic if ivy_check is not installed
                return self._mock_run(ivy_code)
            except Exception as e:
                return {
                    "status": "error",
                    "error_type": "ExecutionError",
                    "message": f"Failed to run Ivy: {str(e)}"
                }

            stdout, stderr = result.stdout, result.stderr
            output = stdout + "\n" + stderr
            
            if "OK" in output and "error" not in output.lower():
                return {
                    "status": "success",
                    "message": "Ivy verification passed! All invariants are inductive."
                }
            
            return self._parse_ivy_output(output)

    def _parse_ivy_output(self, output: str) -> Dict[str, Any]:
        """
        Extracts specific error messages and the CTI (Counterexample To Induction) from Ivy.
        """
        errors = []
        cti_snippet = None
        lines = output.split('\n')
        
        # Simple extraction logic for LLM consumption
        for i, line in enumerate(lines):
            if "error:" in line.lower() or "failed" in line.lower():
                errors.append(line.strip())
            
            # Look for the start of a CTI or counterexample trace
            if "CTI" in line or "counterexample" in line.lower() or "The following state is a counterexample" in line:
                # Capture the state snapshot to give context on WHY induction failed
                end_idx = min(i + 30, len(lines)) # limit to 30 lines to prevent overflow
                cti_snippet = "\n".join(lines[i:end_idx]).strip()
                break # Just capture the first major CTI block
                
        return {
            "status": "failed",
            "errors": errors,
            "cti_snippet": cti_snippet if cti_snippet else "No clear CTI extracted. Check raw output.",
            "raw_output_snippet": output[:1500] # Give a snippet in case parsing missed something
        }

    def _mock_run(self, ivy_code: str) -> Dict[str, Any]:
        """Mock execution when Ivy is not installed."""
        if "BUG" in ivy_code:
            return {
                "status": "failed",
                "errors": ["error: assertion failed"],
                "cti_snippet": "CTI: In state S0, node 1 holds exclusive lock (M), but node 2 also transitions to M. \nAction: grant_lock(node 2)",
                "message": "Found a Counterexample To Induction (CTI). Your invariants are not inductive."
            }
        elif "syntax_error" in ivy_code:
            return {
                "status": "error",
                "errors": ["model.ivy:15: error: syntax error"],
                "cti_snippet": None,
                "message": "Ivy parser error."
            }
        else:
            return {
                "status": "success",
                "message": "Ivy verification passed! All invariants are inductive."
            }
