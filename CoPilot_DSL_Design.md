# Coherence Pilot: LLM-Friendly Protocol DSL (CoPilot-DSL)

In the `coherence_pilot` framework, traditional regex or LALR(k)-based parsers (such as ProtoGen's ANTLR approach) are not the optimal solution. Considering that the core compiler and code generator of this framework is a **Large Language Model (LLM)**, the design of the DSL must meet the following criteria: **Semantically Structured, Intent-driven, and Extremely LLM-Friendly for parsing**.

Therefore, CoPilot-DSL adopts a structure similar to YAML or Python Dataclasses to decompose complex protocol topologies, channel properties, and behavioral logic into a structured knowledge skeleton. This allows the LLM to accurately understand and subsequently generate the underlying Murphi state machines and Lean theorem proving code.

Below is the architectural design scheme for **CoPilot-DSL**:

---

## 1. Design Philosophy

1. **Configuration as Code (CaC)**: Uses a YAML or JSON style, discarding traditional C-style curly braces `{}` syntax. Since LLMs are exposed to massive amounts of structured configuration files during pre-training, their ability to process hierarchical indentation and key-value mappings is exceptional.
2. **Decoupling Declarative and Imperative Logics**: Employs strict declarative logic for defining nodes, networks, and channels; for state transitions, it uses high-level pseudocode to focus on describing the intent of "Event Trigger -> Message Action -> State Transition", stripping away implementation details of underlying communication and lock mechanisms.
3. **Separation of Global and Local Perspectives**: A protocol includes not only the behavioral logic of local state machines but is also constrained by global safety properties (Invariants). Explicitly separating these two helps the LLM's Refiner Agent quickly perform counterexample localization and root-cause analysis when Model Checking (e.g., in Murphi) fails.

---

## 2. CoPilot-DSL Architectural Example (Snooping MESI)

### 2.1 Topology & Components Definition
Clearly defines the system architecture, participant roles, and their local registers:

```yaml
topology:
  type: snooping_bus  # Extensible to directory, ring, mesh (for CHI)
  components:
    - name: Cache
      count: 3
      stable_states: [I, S, E, M]
      registers:
        - data: cl
        - bool: is_dirty
    - name: Memory
      count: 1
      stable_states: [IDLE, BUSY]
      registers:
        - data: cl
```

### 2.2 Network & Message Channels
Modern industrial protocols like CHI contain extremely complex channel models. Clear channel definitions prevent the LLM from confusing out-of-order and in-order semantics:

```yaml
network:
  channels:
    - name: ReqBus
      type: broadcast
      ordered: true
    - name: RespBus
      type: point_to_point
      ordered: false

messages:
  - type: GetS
    payload: [addr, src_id]
  - type: DataResp
    payload: [addr, cl, is_dirty]
```

### 2.3 Behaviors & Transitions Core
Uses the "Event-Condition-Action" (ECA) pattern to specify the business logic of protocol operations:

```yaml
behaviors:
  Cache:
    - state: S
      triggers:
        - on_event: "Local_Write"  # Triggered by local processor event
          actions:
            - broadcast(ReqBus, GetM)
            - wait_for(RespBus, DataResp)
          next_state: M

        - on_event: "Snoop_GetM"   # Triggered by snooping bus event
          condition: "src_id != my_id"
          actions:
            - send(RespBus, DataResp(cl, is_dirty=false))
          next_state: I
```
*At this abstraction layer, only the core protocol flow logic is constrained. Translating `wait_for` into Murphi Rules with concurrency handling and queue management is the responsibility of the LLM code generator.*

### 2.4 Invariant Assertions
Defines the system invariants that must be mathematically guaranteed:

```yaml
invariants:
  - name: Single_Writer_Multiple_Reader
    description: "If any cache is in state M or E, no other cache can be in state M, E, or S."
    formal_hint: "forall i j. (Cache[i].State == M -> Cache[j].State == I)"
  
  - name: Data_Consistency
    description: "The data in state M must be the latest valid data in the system."
```

---

## 3. Workflow Integration in Coherence Pilot

In the closed-loop of `coherence_pilot`, this DSL acts as the core intermediate layer connecting natural language and underlying formal code:

1. **Input Phase**: Receives this structured YAML specification (which can be manually written or parsed from natural language by the Spec Generator Agent).
2. **Code Synthesis**: Freed from the noise of low-level syntax, the LLM focuses entirely on the core state transition logic (e.g., `Cache: S -> Snoop_GetM -> I`) and translates/expands it into complete Murphi model code (supplementing all intermediate transient states and deadlock avoidance mechanisms).
3. **Verification Feedback**: When formal verification fails, the Refiner Agent aligns the underlying Error Trace with the intent in the YAML DSL. This allows it to quickly understand whether a Race Condition was introduced during the translation of "concurrent wait (`wait_for`)" or "broadcast order (`broadcast`)", enabling targeted code repairs.
4. **Theorem Proving**: When generating Lean 4 inductive proofs, the LLM can directly extract meta-information from the `invariants` and `stable_states` nodes of the YAML to assist in constructing and strengthening Lemmas.

## 4. Summary of Architectural Advantages

Adopting this YAML ECA (Event-Condition-Action) structure as the framework's DSL offers several benefits:
- **High Extensibility**: Supports protocol evolution and architectural changes. For instance, supporting the CHI protocol merely requires adding `HN-F/RN-F` to the `topology` and supplementing Credit-based flow control fields in `channels`.
- **Zero Parsing Overhead**: Utilizing Python's native `yaml.safe_load` completely eliminates the engineering costs associated with maintaining and building complex AST parsers (like ANTLR).
- **Excellent LLM Adaptability**: The declarative nature of the YAML structure aligns perfectly with the generation paradigms of large models, maximally reducing Hallucination rates and improving the success rate of translation and repair.