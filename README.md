# Coherence Pilot

**Coherence Pilot** 是一个结合了 LLM + Agent 与形式化验证（模型检测 + 定理证明）的端到端自主框架。旨在解决缓存一致性协议证明的复杂性，实现自动化证明与高质量的数据生成。

## 🎯 目标

- 构建 LLM + Agent 端到端自主框架，实现缓存一致性协议的自动化证明。
- 将大语言模型的生成能力与形式化方法的严谨验证能力结合，突破复杂协议验证的瓶颈。
- 自动产出高质量的训练数据，反哺 LLM 进行领域微调。

---

## 💡 核心创新点

### 1. Lean + Murphi 交叉验证反馈循环
将有界模型检验（Murphi）与交互式定理证明（Lean 4）串联为双向反馈回路：
- **Murphi 快速过滤**：LLM 生成的候选不变量先经 Murphi 有限实例检验（秒级），发现反例则反馈给 LLM 修正。
- **Lean stuck state 驱动加强**：Lean 证明卡住时，将未完成的 proof obligation 反馈给 LLM 触发引理加强或分解。
- **互补性**：两者组合覆盖彼此盲区，Murphi 擅长找反例，Lean 提供完备证明。

### 2. 反例驱动的搜索空间剪枝
- **反例变量提取剪枝**：从 Murphi 反例中提取关键变量，压缩后续候选不变量的搜索空间。
- **失败 pattern 记录**：维护已探索失败子树的结构特征，避免 LLM 重复生成同构的错误候选。

### 3. 验证过程驱动的高质量数据合成
在验证循环中自动产出三类高质量训练数据：
- **Type A (Debugging CoT)**：来源于验证失败路径，包含错误代码、Trace 与思维链修正过程。
- **Type B (State Reasoning)**：来源于状态空间遍历，包含状态转移与规则理由。
- **Type C (Invariant Data)**：来源于证明成功时的协议-不变量对与自然语言解释。

---

## 🏗️ 框架结构

```text
[用户输入]  e.g. "设计一个包含 E 状态的 MESI 协议"
       ↓
[Spec Generator Agent]   LLM 生成初始 Murphi/Lean 规范代码
       ↓
[Formal Verifier]        Murphi / Ivy 编译运行，检查核心属性
   PASS ↓       FAIL ↓
       ↓    [反例 Trace]──→ [Pruning Module] 剪枝搜索树
       ↓         ↓
       ↓    [Refiner Agent]  LLM 解析反例，识别竞争条件，修复 FSM
       ↓         ↓ 修正后代码 → 返回 Verifier 重新验证
       ↓
[Lean Prover]    归纳不变量证明
   stuck ↓       ↓ 成功
[LLM Strengthener]  加强引理生成
       ↓
[完整机器验证证明]
       ↓
[Data Synthesizer]   同步输出三类训练数据 (Type A / B / C)
       ↓
[Synthesized Dataset]  反哺 LLM 微调，形成飞轮效应
```

---

## 🚀 快速开始

### 依赖安装

```bash
pip install -r requirements.txt
```
*(注意：运行完整流程需在系统中额外配置 Murphi 与 Lean 4 环境)*

### 运行框架

```bash
python main.py
```

执行后，核心调度器 (`orchestrator.py`) 将启动 Agent 与 Verifier 之间的双向反馈循环，并最终在控制台输出验证结果与合成的数据量。

### 作为 MCP (Model Context Protocol) 运行

为了让大语言模型（如 Claude Desktop 或 Cursor 等支持 MCP 的客户端）能够**自主、动态地**调用形式化验证工具，我们提供了标准的 MCP Server 封装。这改变了传统静态编译脚本的方式，让大模型能以交互式的方式进行自动定理证明与协议验证。

启动 MCP Server：

```bash
python mcp_server.py
```

**MCP Server 提供的核心工具（Tools）：**
- `run_murphi_check`: 编译并运行 Murphi 模型。当遇到 Invariant Violation 时，自动解析冗长的输出，提取**状态变化增量（State Deltas）**，避免 LLM 上下文溢出。
- `run_lean_proof`: 执行 Lean 4 脚本。不仅返回编译结果，还会在证明卡住时（stuck）提取并返回精确的 **Tactic State（剩余的证明目标/Unsolved Goals）**，引导大模型进行下一步策略推理。
- `run_ivy_check`: 执行 Ivy 归纳不变量检查。当不变量非归纳时，自动提取 **CTI (Counterexample To Induction)**，精确指出导致归纳失败的状态和动作。
- `parse_counterexample_trace`: 将现有的 Murphi 输出纯文本结构化为 JSON Trace。

---

## 📂 目录结构

- `main.py`：入口文件
- `core/`：核心调度器，串联整个反馈循环
- `agents/`：大模型 Agent 集合（生成、修复、加强）
- `verifiers/`：形式化工具接口（Murphi, Lean）
- `pruning/`：反例与状态空间剪枝模块
- `data_synth/`：训练数据合成引擎
