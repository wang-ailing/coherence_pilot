import json
from mcp.server.fastmcp import FastMCP
from verifiers.murphi_tool import MurphiTool
from verifiers.lean_tool import LeanTool
from verifiers.ivy_tool import IvyTool

# Initialize FastMCP Server
mcp = FastMCP("Coherence Pilot Formal Verification MCP Server")

# Initialize our specialized tool wrappers
murphi_runner = MurphiTool()
lean_runner = LeanTool()
ivy_runner = IvyTool()

@mcp.tool()
def run_murphi_check(model_code: str, max_depth: int = 100) -> str:
    """
    Run Murphi model checker on the provided Murphi code.
    This tool compiles and executes the model, and returns a structured 
    Counterexample Trace showing only State Deltas (variable changes) 
    if an invariant is violated.
    
    Args:
        model_code: The raw Murphi code string to verify.
        max_depth: Maximum exploration depth for the model checker.
    """
    result = murphi_runner.run_check(model_code=model_code, max_depth=max_depth)
    return json.dumps(result, indent=2)

@mcp.tool()
def run_lean_proof(lean_code: str) -> str:
    """
    Execute Lean 4 to verify the provided theorem/proof script.
    This tool parses the Lean output and specifically returns the
    Tactic State (unsolved goals) or syntax errors, allowing for 
    iterative proof development.
    
    Args:
        lean_code: The raw Lean 4 code string to verify.
    """
    result = lean_runner.run_proof(lean_code=lean_code)
    return json.dumps(result, indent=2)

@mcp.tool()
def run_ivy_check(ivy_code: str, isolate: str = None) -> str:
    """
    Run Ivy model checker to verify inductive invariants.
    If the invariants are not inductive, it returns a structured 
    Counterexample To Induction (CTI) that shows exactly which state 
    violates the induction step.
    
    Args:
        ivy_code: The raw Ivy model code string to verify.
        isolate: Optional isolate to verify (e.g., 'iso_protocol').
    """
    result = ivy_runner.run_check(ivy_code=ivy_code, isolate=isolate)
    return json.dumps(result, indent=2)

@mcp.tool()
def parse_counterexample_trace(murphi_output: str) -> str:
    """
    Helper tool: If you already have raw Murphi output, you can use 
    this tool to parse it into a structured, delta-only Counterexample Trace.
    
    Args:
        murphi_output: The raw console output from Murphi.
    """
    result = murphi_runner._parse_murphi_trace(murphi_output)
    return json.dumps(result, indent=2)

if __name__ == "__main__":
    # Start the MCP server using standard stdio communication (used by Agent tools like Claude Desktop)
    print("Starting Coherence Pilot MCP Server via stdio...")
    mcp.run()
