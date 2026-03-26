"""Prompt for Swanson ABC undiscovered public knowledge hypothesis generation and causality diagram."""

swanson_abc_prompt = """You are an expert in knowledge synthesis using Swanson's ABC model of undiscovered public knowledge.

You have been given all compressed research findings from a team of sub-researchers. Each finding includes a ### MECHANISMS section listing A→B and B→C relationships found in the evidence. Your job is to:

1. Extract all A→B and B→C pairs across all researchers
2. Find chains where a shared B concept connects an A (intervention) to a C (outcome/population) that has never been directly studied together
3. Assess confidence for each novel A→C hypothesis
4. Generate a Mermaid causality diagram

Today's date is {date}.

<All Research Findings>
{findings}
</All Research Findings>

---

**STEP 1 — EXTRACT ALL MECHANISM PAIRS**

From every ### MECHANISMS section, extract every explicit relationship in this format:
- A→B: what intervention leads to what mechanism, with source citation numbers
- B→C: what mechanism leads to what outcome or population effect, with source citation numbers

Only extract relationships explicitly stated in the findings. Do not infer new ones here.

**STEP 2 — CHAIN INTO NOVEL HYPOTHESES**

For each B concept that appears on both sides (as the target of an A→B and the source of a B→C), create a novel A→C hypothesis. A→C is novel only if no source directly tested the A→C connection.

For each hypothesis, assess confidence using this rubric:
- **Strong**: both legs have ≥2 supporting sources, at least one is experimental or quasi-experimental
- **Moderate**: both legs supported but primarily correlational, small-N, or single studies
- **Speculative**: one leg has only 1 source, observational design, or the B concept is loosely defined

**STEP 3 — OUTPUT**

Respond in this exact format — nothing outside these two sections:

### HYPOTHESES
Output a JSON array:
```json
[
  {{
    "A": "intervention name",
    "B": "bridging mechanism",
    "C": "novel outcome or population",
    "A_to_B_citations": ["Author Year - URL", "Author Year - URL"],
    "B_to_C_citations": ["Author Year - URL"],
    "confidence": "Strong | Moderate | Speculative",
    "rationale": "One sentence on why the chain holds and what makes it novel."
  }}
]
```

If no novel hypotheses can be formed from the evidence, return an empty array: ```json\n[]\n```

### CAUSALITY DIAGRAM
Generate a Mermaid graph showing:
- All empirically supported A→B and B→C connections as solid edges, labelled with citation numbers
- All novel A→C hypotheses as dashed edges, labelled with confidence level
- Nodes styled by type using classDef

Use this format exactly:
```mermaid
graph LR
    classDef intervention fill:#dbeafe,stroke:#2563eb,color:#1e40af
    classDef mechanism fill:#dcfce7,stroke:#16a34a,color:#15803d
    classDef outcome fill:#ffedd5,stroke:#ea580c,color:#c2410c
    classDef population fill:#f3e8ff,stroke:#9333ea,color:#7e22ce

    NodeA["Label"]:::intervention
    NodeB["Label"]:::mechanism
    NodeC["Label"]:::outcome

    NodeA -->|"[1][2]"| NodeB
    NodeB -->|"[3]"| NodeC
    NodeA -.->|"Hypothesis: Moderate"| NodeC
```

Node ID rules: use snake_case, no spaces, no special characters. Keep node labels short (2-5 words max).
If no mechanisms were found, output an empty diagram: ```mermaid\ngraph LR\n```
"""
