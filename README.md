# Corroborated Evidence Ranking Engine

A candidate ranking system that doesn't trust claims — it trusts corroboration between independent evidence sources.

## Core Innovation

Most systems ask: **"How similar is this candidate to the JD?"**

We ask: **"How much independent evidence supports this candidate's claims?"**

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
[Semantic Recall] → Top 5000 relevant
    ↓
[JD Disqualifier Gates] → Soft penalties (not hard rejections)
    ↓
[Evidence Consistency Engine] → ECS score (4 axes, geometric mean)
    ↓
[Behavioral Reality Layer] → Sentinels treated as unknown
    ↓
[Availability Scoring] → Notice period + activity
    ↓
[Final Score] → ECS × Recruitability × Availability × (1 - GatePenalty)
    ↓
[Reasoning Generator] → Feature-based, no LLM, no hallucination
    ↓
Submission CSV
```

## Key Design Decisions

### 1. Sentinel Values = Unknown, Not Bad

- `offer_acceptance_rate = -1` → 59.6% of candidates (no offer history yet)
- `github_activity_score = -1` → 64.6% of candidates (no GitHub linked)

Treat as "no data" (neutral imputation), not penalty.

### 2. Soft Gates, Not Hard Rejections

Naive elimination causes 13.4% false positive rate. Soft penalties avoid this.

### 3. Multiplicative Scoring

```
Score = ECS × Recruitability × Availability × (1 - GatePenalty)
```

Why: A candidate with 95 skill and 0 recruitability scores 0. Correct — they're unreachable.

### 4. Feature-Based Reasoning (No LLM)

Every reasoning sentence sourced from actual features. No hallucination. Rank-consistent.

## Usage

### Run Pipeline
```bash
pip install -r requirements.txt
python rank.py ./data ranked_candidates.csv
```

### Validate
```bash
python validate.py ./data ranked_candidates.csv
```

## Competition Constraints

- CPU-only (no GPU)
- No network access during evaluation
- ≤5 minutes runtime
- ≤16GB RAM

All components are designed to meet these constraints.

## Files

- `rank.py` — Main pipeline
- `features.py` — Feature extraction
- `evidence.py` — Evidence consistency engine
- `reasoning.py` — Deterministic reasoning generator
- `validate.py` — Validation harness
- `config.py` — Configuration and constants
