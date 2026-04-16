# Coherence Pilot DSL: An LLM-Centric Paradigm for Protocol Specification

## 1. Abstract
The increasing complexity of modern industrial cache coherence protocols (e.g., ARM CHI) poses significant challenges for traditional formal verification workflows. Conventional Domain-Specific Languages (DSLs), such as ProtoCC, rely on deterministic AST-based parsers (e.g., ANTLR) and sequential specification (SSP) expansion algorithms. While effective for simple directory-based protocols (MSI, MESI), these legacy compilers inherently lack the abstraction elasticity required to model complex non-deterministic behaviors, such as snooping broadcasts, multi-level topologies (HN-F, RN-F, SN-F), and credit-based flow control.

To address this gap, the `coherence_pilot` framework introduces an **LLM-Centric Protocol DSL (CoPilot-DSL)**. By shifting the compilation workload from deterministic algorithms to Large Language Models (LLMs), the CoPilot-DSL adopts an intent-driven, highly structured Event-Condition-Action (ECA) paradigm. This document outlines the theoretical foundation and architectural design of this novel specification language.

## 2. Limitations of Traditional Protocol DSLs
Traditional protocol DSLs face structural bottlenecks when applied to modern coherence architectures:
- **Rigid Concurrency Expansion**: Existing algorithms (e.g., ForkTree expansion in ProtoGen) assume point-to-point message dependencies. They fail to natively map global ordering points required in snooping bus protocols without extensive, error-prone compiler rewrites.
- **Syntactic Noise**: Custom C-like syntaxes impose high cognitive loads on automated synthesis agents. LLMs often struggle with strict, esoteric grammatical constraints (e.g., specific semicolon placement or bracket matching), leading to elevated hallucination rates during code generation.
- **Coupled Invariants and Transitions**: The intermingling of local state transitions with global safety properties complicates counterexample-guided abstraction refinement (CEGAR).

## 3. Design Philosophy of CoPilot-DSL
The CoPilot-DSL Abstraction Layer is designed under the premise that **the LLM acts as the ultimate compiler**. Consequently, the DSL prioritizes semantic density and structural clarity over low-level execution details.

### 3.1 Configuration as Code (CaC)
Leveraging YAML or JSON data serialization standards, the DSL eliminates custom lexical parsing overhead. LLMs exhibit exceptional zero-shot comprehension of hierarchical key-value structures due to their prevalence in pre-training corpora. This ensures near-zero parsing cost and maximum semantic alignment.

### 3.2 Declarative Topologies and Imperative Intent
The DSL strictly decouples the declaration of physical entities from the specification of protocol behavior:
- **Declarative Topology**: Nodes, registers, and network channels (ordered/unordered, broadcast/point-to-point) are defined statically.
- **Intent-Driven Imperative Behavior**: State transitions are abstracted into high-level pseudocode primitives (e.g., `broadcast`, `wait_for`). The DSL captures the *intent* of the transition, delegating the implementation of concurrent queues, locks, and transient states to the LLM's synthesis capabilities.

### 3.3 Disaggregation of Verification Objectives
Local state machine behaviors are explicitly separated from global safety properties (Invariants). This disaggregation enables the LLM's Refiner Agent to perform localized fault isolation when a Model Checker (e.g., Murphi) yields an error trace, significantly accelerating the debugging loop.

## 4. Architectural Schema
The CoPilot-DSL schema is structured into four primary semantic blocks:

1. **Topology Matrix**: Defines the architectural components (e.g., `Cache`, `Memory`, `HN-F`) and their internal state spaces and data registers.
2. **Channel & Message Specification**: Formalizes the network abstraction, distinguishing between ordered/unordered delivery, point-to-point/broadcast routing, and defining message payloads.
3. **Event-Condition-Action (ECA) Core**: The behavioral logic is represented as a state-transition matrix. Each transition defines a trigger (`on_event`), a prerequisite (`condition`), a sequence of high-level operations (`actions`), and the resulting state (`next_state`).
4. **Invariant Assertions**: Formal definitions of the required safety properties (e.g., Single-Writer-Multiple-Reader, Data Consistency). These assertions serve a dual purpose: acting as constraints for bounded model checking (Murphi) and providing formal hints for inductive theorem proving (Lean 4).

## 5. Conclusion
The CoPilot-DSL represents a paradigm shift in protocol specification. By abstracting away deterministic compilation constraints and leveraging the reasoning capabilities of LLMs, it provides a highly scalable, noise-free specification medium. This architecture not only accommodates the intricacies of modern coherence protocols like CHI but also seamlessly integrates with autonomous verification pipelines, paving the way for end-to-end, LLM-driven formal verification.