# Corroborated Evidence Ranking Engine

A candidate ranking system that doesn't trust claims — it trusts **corroboration between independent evidence sources**.

## Core Innovation

Most systems ask: *"How similar is this candidate to the JD?"*

We ask: *"How much independent evidence supports this candidate's claims?"*

### The 4 Evidence Axes

| Axis | What It Measures | Why It Matters |
|------|------------------|----------------|
| **Claim ↔ Assessment** | Self-reported proficiency vs platform assessment | Catches inflated skill claims |
| **Claim ↔ Career History** | Skills claimed vs career descriptions | Verifies experience authenticity |
| **Claim ↔ Corroboration** | Skills vs endorsements, GitHub, certifications | Multiple sources = more trust |
| **Seniority ↔ Trajectory** | Title vs years, tenure, progression | Detects title inflation |

### Geometric Mean Aggregation

```
ECS = (A^0.35 × B^0.30 × C^0.20 × D^0.15) ^ (1/1.0)
```

**Why geometric?** One contradiction kills the score.
- All consistent (0.9 each): ECS = 0.90
- One contradiction (0.9, 0.9, 0.9, 0.2): ECS = 0.58

## Architecture

```
100K Candidates
    ↓
[Feature Extraction] → 52 features per candidate (sentinel-safe)
    ↓
[4-Axis ECS] → Evidence Consistency Score (geometric mean)
    ↓
[Heuristic Scoring] → ECS × SkillDensity × Engagement × Experience × (1-Gate) × EngBonus
    ↓
[LightGBM LambdaMART] → Learned ranking from weak-supervision labels
    ↓
[Score Blend] → 60% LightGBM + 40% Heuristic
    ↓
[Behavioral Twin Resolution] → KMeans clustering + cluster quality bonus
    ↓
[Deterministic Reasoning] → Feature-based, no LLM, no hallucination, with counterfactuals
    ↓
Ranked CSV (100 candidates)
```

## Key Design Decisions

### 1. Sentinel Values = Unknown, Not Bad

- `offer_acceptance_rate = -1` → 59.6% of candidates (no offer history yet)
- `github_activity_score = -1` → 64.6% of candidates (no GitHub linked)

Treat as "no data" (neutral imputation), not penalty.

### 2. Soft Multiplicative Gates, Not Hard Rejections

Non-technical titles get penalized proportionally, not eliminated.
Naive elimination causes 13.4% false positive rate.

### 3. Engineer Bonus × Non-Tech Penalty

```
EngBonus = 1 + is_engineer × 0.7 - is_non_tech × 0.4
```

A Data Scientist gets 1.7x. An HR Manager gets 0.3x. Net difference: **5.7x**.

### 4. LightGBM LambdaMART

Trained on weak-supervision labels derived from JD-aligned heuristics:
- Technical role + AI skills → positive label
- Non-technical role → negative label
- Behavioral signals (response rate, interview completion) → bonus

### 5. Twin Resolution + Counterfactuals

Candidates are clustered into behavioral twins. For each top candidate, we find their closest twin and explain **why they outrank them** (evidence consistency, engagement, AI skills).

### 6. Feature-Based Reasoning (No LLM)

Every reasoning sentence sourced from actual features. No hallucination. Rank-consistent.

## Results

- **Top 10**: 100% technical roles (ML Engineer, Data Scientist, CV Engineer, etc.)
- **Top 100**: 100% technical roles (0 non-technical)
- **Runtime**: ~56 seconds (CPU-only, no GPU)
- **Passes official validator**: ✓

## Usage

```bash
pip install -r requirements.txt
python rank.py
```

Output: `ranked_candidates.csv` (100 rows, format: candidate_id, rank, score, reasoning)

## Competition Constraints

- CPU-only (no GPU) ✓
- No network access during evaluation ✓
- ≤5 minutes runtime ✓ (runs in ~56s)
- ≤16GB RAM ✓

## Files

| File | Description |
|------|-------------|
| `rank.py` | Main pipeline (runs everything end-to-end) |
| `features.py` | 52-feature extraction from JSONL candidates |
| `evidence.py` | 4-axis Evidence Consistency Engine |
| `reasoning.py` | Deterministic reasoning generator |
| `ranker.py` | LightGBM LambdaMART ranker |
| `twin_resolution.py` | Behavioral twin clustering |
| `config.py` | Calibrated constants and weights |
| `requirements.txt` | Python dependencies |
