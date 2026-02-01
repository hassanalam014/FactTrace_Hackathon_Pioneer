# 🧠 FactTrace Jury  
**Multi-Agent Fact Faithfulness Evaluation**

**Group Name:** Pioneer  
**Main Script:** `facttrace_jury.py`

---

## Overview

`facttrace_jury.py` implements a **jury of AI agents** that debates whether an external claim is a *faithful representation* of an internal fact, or whether the meaning has been **mutated** through exaggeration, omission, or misinterpretation.

Instead of relying on a single model verdict, the system orchestrates **multiple specialized agents** with distinct reasoning styles, forces them to **disagree and confront each other**, and then aggregates their judgments into a transparent final decision.

This project was built for the **FactTrace Hackathon @ University of Cambridge**, addressing the **Agentic Consensus Challenge**

---

## Core Idea

Each fact–claim pair is evaluated by a **jury**, not a single judge.

The system runs in **two rounds**:
1. **Independent Judgments** – agents evaluate the claim in isolation.
2. **Confrontation Round** – agents re-evaluate after seeing each other’s arguments.

A final verdict is reached using **majority consensus**, while preserving ambiguity when appropriate.

---

## Agent Roles

The jury consists of three intentionally distinct agents:

### 🧮 Pedantic Fact-Checker
- Focuses on **literal factual accuracy**
- Checks exact numbers, wording, and logical equivalence
- Does *not* excuse simplifications or framing choices

### 🧭 Context Guardian
- Focuses on **missing qualifiers and scope shifts**
- Flags changes in population, timeframe, geography, or causality
- Identifies what is omitted but materially important

### 🧠 Common-Sense Judge
- Represents an **average, reasonable reader**
- Evaluates whether the claim would **mislead in practice**
- Focuses on overall takeaway rather than technical precision

Each agent produces a structured response containing:
- A verdict: **Faithful**, **Mutated**, or **Unclear**
- A confidence level
- Bullet-pointed reasoning

---

## Decision Logic

After the confrontation round, the system determines a final verdict:

- **Mutated** → if at least **two agents** vote *Mutated*
- **Faithful** → only if **all agents** vote *Faithful*
- **Ambiguous** → all other cases

This conservative logic avoids overconfident conclusions and treats uncertainty as a first-class outcome.

---

## Data Flow

1. Load a CSV file containing:
   - `truth` → internal fact
   - `claim` → external claim
2. Select a **strategic subset** of cases (default: 5)
3. For each case:
   - Display the internal fact and external claim
   - Run Round 1 (independent judgments)
   - Run Round 2 (agent confrontation)
   - Output a final verdict with agent votes

All agent debates and decisions are printed live for **maximum demo transparency**.

---

## Configuration

Key parameters in `facttrace_jury.py`:

```python
MODEL = "gpt-5.2"        # switch to cheaper models during development
CSV_PATH = "Pioneer.csv"
N_CASES = 5
INTERNAL_COL = "truth"
EXTERNAL_COL = "claim"
```

## Implementation Notes

The script uses:

- **python-dotenv** for API key management  
- **OpenAI Chat Completions API** for agent reasoning  
- **Low temperature (0.3)** for consistent, reasoned outputs  

---

## Why a Multi-Agent Jury?

A single prompt can label a claim as *“true”* or *“false.”*  
A **jury explains why**.

This approach:

- Exposes different failure modes of factual mutation  
- Forces agents to confront alternative interpretations  
- Prevents brittle binary classifications  
- Preserves ambiguity when the data genuinely supports it  

The result is a **transparent, debatable, and explainable verdict**.

---

## Example Output

```text
CASE 12

[Pedantic Fact-Checker]
Verdict: Faithful
Confidence: High
Key Arguments:
- Numerical values match exactly

[Context Guardian]
Verdict: Mutated
Confidence: Medium
Key Arguments:
- Timeframe omitted
- Causal interpretation implied

[Common-Sense Judge]
Verdict: Mutated
Confidence: High
Key Arguments:
- Likely to mislead an average reader

FINAL VERDICT:
Decision: Mutated
Agent votes: ['Mutated', 'Mutated', 'Mutated']

```
---
## Intended Use

- Studying factual mutation and narrative drift  
- Transparent AI-assisted fact-checking  
- Research into agentic consensus and deliberative AI systems
---

