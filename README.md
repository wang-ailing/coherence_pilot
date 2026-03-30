# Coherence Pilot: LLM + Agent 驱动的缓存一致性协议自动化证明框架

Coherence Pilot 是一个端到端的自主 Agent 框架，旨在将大语言模型（LLM）的生成能力与形式化方法（Murphi、Lean 4）的严谨验证能力相结合，从而解决复杂缓存一致性协议在设计和验证中的难题。

同时，该框架在证明搜索和验证循环中，自动产出高质量的思维链与状态推理数据，形成反哺 LLM 训练的“数据飞轮”。

---

## 🎯 核心目标

- 构建 LLM + Agent 端到端自主框架（Coherence Pilot），实现缓存一致性协议的自动化证明与高质量数据生成。
- 将大语言模型的生成能力与形式化方法的严谨验证能力结合，解决缓存一致性协议设计的复杂性。

---

## 💡 核心创新点

### 1. Lean + Murphi 交叉验证反馈循环
将有界模型检验（Murphi）与交互式定理证明（Lean 4）串联为双向反馈回路：
- **Murphi 快速过滤**：LLM 生成的候选不变量先经 Murphi 有限实例检验（秒级），发现反例则将具体状态赋值反馈给 LLM 修正，避免将错误候选送入 Lean 造成浪费。
- **Lean stuck state 驱动加强**：Lean 证明卡住时，将未完成的 proof obligation 反馈给 LLM，触发引理加强或分解。
- **优势互补**：Murphi 擅长找反例但无法证明无穷状态；Lean 可给出完备证明但对错误输入代价高。两者组合完美覆盖彼此盲区。

### 2. 反例驱动的搜索空间剪枝
在 Agent 证明搜索过程中，利用多层剪枝策略控制搜索树规模：
- **反例变量提取剪枝**：从 Murphi 反例中提取参与违例的关键变量子集，后续候选不变量只在该子集的组合空间上搜索，大幅压缩候选空间。
- **失败 pattern 记录**：维护已探索失败子树的结构特征，避免 LLM 在不同迭代中重复生成同构的错误候选。

### 3. 验证过程驱动的高质量数据合成
将证明搜索树与验证循环本身转化为数据生成引擎，自动产出三类高质量训练数据：
- **Type A (Debugging CoT)**：来源于 Murphi 验证失败路径。格式：`错误协议代码 + 反例 Trace → 思维链分析竞争条件 → 修正后的代码`。教 LLM 如何从错误中恢复，提升逻辑推理能力。
- **Type B (State Reasoning)**：来源于模型检验器遍历的状态空间。格式：`当前状态集合 + 新消息 → 预测下一状态 → 依据协议规则的理由`。为 LLM 提供精确状态机模拟的监督信号。
- **Type C (Invariant Data)**：来源于证明成功时提取的协议-不变量对。格式：`协议代码 → 关键不变量 → 自然语言解释`。提升 LLM 对证明语言、代码语义和安全属性的理解。

---

## 🏗️ 架构设计

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

## 📁 项目结构

```bash
coherence_pilot/
├── main.py                  # 框架主控入口，管理验证与修复循环
├── agents/                  # LLM 智能体模块
│   ├── spec_generator.py    # 从自然语言生成初始规范
│   ├── refiner.py           # 分析反例 Trace 并修复 FSM
│   └── strengthener.py      # 分析 Lean 卡住状态并加强引理
├── verifiers/               # 形式化验证器接口
│   ├── murphi_runner.py     # Murphi 有界模型检验封装
│   ├── lean_runner.py       # Lean 4 定理证明封装
│   └── pruning.py           # 搜索空间剪枝与反例变量提取
├── data/                    # 数据飞轮模块
│   └── synthesizer.py       # 合成 Type A/B/C 高质量训练数据
├── core/                    # 核心数据结构与基础工具
│   ├── protocol_state.py    # 协议规范定义 (ProtocolSpec)
│   └── llm_client.py        # OpenAI API / 结构化输出封装
└── requirements.txt         # 项目依赖
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

配置你的大模型 API 密钥：

```bash
export OPENAI_API_KEY="your_api_key_here"
```

### 3. 运行框架

启动 Coherence Pilot 的自动迭代验证流程（当前包含演示模拟流程）：

```bash
python main.py --prompt "设计一个包含 E 状态的 MESI 协议"
```

---

## 🎯 演进路线：目标协议分级

| Tier | 协议 | 复杂度 | 状态 |
| :--- | :--- | :--- | :--- |
| **Tier 1** | Write-Once, Illinois MESI, MOESI | 基础 Snoopy 协议 | 优先支持 |
| **Tier 2** | Censier-Feautrier, DASH | 目录协议，多跳消息网络 | 计划中 |
| **Tier 3** | CXL Cache Coherence | 新型异构互连协议 | 探索性 |

---

## 📚 参考资料与理论基础

- **缓存一致性基础**: *A Primer on Memory Consistency and Cache Coherence* (Hill & Nagarajan, 2020)
- **形式化验证方法**: Ivy (Padon et al.), CMurphi, IC3/PDR (Bradley)
- **最新学术进展**: Formalising CXL Cache Coherence (ASPLOS 2025), HeteroGen (HPCA 2022)
- **大模型与定理证明**: LeanDojo (NeurIPS 2023), DeepSeek-Prover-V1.5 (2024), AlphaProof (DeepMind 2024)
- **硬件设计 LLM**: ChipNeMo (2023), AssertLLM (2024)
