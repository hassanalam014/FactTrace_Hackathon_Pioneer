import os
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
from textwrap import indent

# =========================
# 0. Setup
# =========================

load_dotenv(override=True)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-5.2"   # switch to "gpt-4.1" for final demo
# MODEL = "gpt-4.1-mini"   # switch to "gpt-4.1" for final demo

CSV_PATH = "Pioneer.csv"
N_CASES = 5              # recommended by the challenge

# CHANGE THESE IF YOUR CSV USES DIFFERENT NAMES
INTERNAL_COL = "truth"
EXTERNAL_COL = "claim"


# =========================
# 1. Agent definitions
# =========================

AGENTS = {
    "Pedantic Fact-Checker": """
You are a strict, pedantic fact-checker.
Your job is to assess literal factual faithfulness.

Focus on:
- Exact numbers
- Precise wording
- Logical equivalence

Do NOT consider whether simplification is reasonable.
""",

    "Context Guardian": """
You are a context-focused analyst.
Your job is to identify missing qualifiers or scope shifts.

Focus on:
- Population, timeframe, geography
- Correlation vs causation
- What is omitted but important
""",

    "Common-Sense Judge": """
You represent an average, reasonable reader.
Your job is to judge whether the external claim would mislead most people.

Focus on:
- Practical interpretation
- Overall meaning
- Reader takeaway
"""
}


OUTPUT_FORMAT = """
Respond using exactly this format:

Verdict: Faithful | Mutated | Unclear
Confidence: Low | Medium | High
Key Arguments:
- bullet point
- bullet point
"""


# =========================
# 2. Helper functions
# =========================

def ask_agent(role, system_prompt, internal_fact, external_claim, extra_context=None):
    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": f"""
Internal Fact:
{internal_fact}

External Claim:
{external_claim}

{extra_context or ""}

{OUTPUT_FORMAT}
"""
        }
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()


def parse_verdict(text):
    for line in text.splitlines():
        if line.lower().startswith("verdict"):
            return line.split(":", 1)[1].strip()
    return "Unclear"


def final_decision(verdicts):
    mutated = verdicts.count("Mutated")
    faithful = verdicts.count("Faithful")

    if mutated >= 2:
        return "Mutated"
    if faithful == len(verdicts):
        return "Faithful"
    return "Ambiguous"


# =========================
# 3. Load & select data
# =========================

df = pd.read_csv(CSV_PATH)

# cases = df[[INTERNAL_COL, EXTERNAL_COL]].dropna().head(N_CASES)

cases = (
    df[[INTERNAL_COL, EXTERNAL_COL]]
    .dropna()
    .iloc[[3, 7, 10, 12, 14]]
)

print(f"\nLoaded {len(cases)} cases from {CSV_PATH}\n")


# =========================
# 4. Run the jury
# =========================

for idx, row in cases.iterrows():
    internal_fact = row[INTERNAL_COL]
    external_claim = row[EXTERNAL_COL]

    print("\n" + "=" * 80)
    print(f"CASE {idx}")
    print("=" * 80)

    print("\nINTERNAL FACT:")
    print(indent(internal_fact, "  "))

    print("\nEXTERNAL CLAIM:")
    print(indent(external_claim, "  "))

    # ---- Round 1: Independent judgments ----
    print("\n--- ROUND 1: INITIAL JUDGMENTS ---")

    round1_outputs = {}
    verdicts = []

    for role, prompt in AGENTS.items():
        output = ask_agent(role, prompt, internal_fact, external_claim)
        round1_outputs[role] = output
        verdict = parse_verdict(output)
        verdicts.append(verdict)

        print(f"\n[{role}]")
        print(indent(output, "  "))

    # ---- Round 2: Confrontation ----
    print("\n--- ROUND 2: CONFRONTATION ---")

    confrontation_context = "Other agents said:\n"
    for role, text in round1_outputs.items():
        confrontation_context += f"\n[{role}]\n{text}\n"

    round2_verdicts = []

    for role, prompt in AGENTS.items():
        output = ask_agent(
            role,
            prompt,
            internal_fact,
            external_claim,
            extra_context=confrontation_context
        )

        verdict = parse_verdict(output)
        round2_verdicts.append(verdict)

        print(f"\n[{role} – After Confrontation]")
        print(indent(output, "  "))

    # ---- Final verdict ----
    final = final_decision(round2_verdicts)

    print("\n--- FINAL VERDICT ---")
    print(f"Decision: {final}")
    print(f"Agent votes: {round2_verdicts}")

print("\nDone.")
