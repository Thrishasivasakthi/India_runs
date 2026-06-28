# Redrob AI — Candidate Ranking Engine

Evidence-first candidate ranking for the Redrob Intelligent Candidate Discovery & Ranking Challenge.

## Core Innovation

Most systems ask: *"How similar is this candidate to the JD?"*

We ask: *"How much independent evidence supports this candidate's claims?"*

### The 4 Evidence Axes

| Axis | What It Measures | Why It Matters |
|------|------------------|----------------|
| **Claim ↔ Assessment** | Self-reported proficiency vs platform assessment | Catches inflated skill claims |
| **Claim ↔ Career History** | Skills claimed vs career descriptions | Verifies experience authenticity |
| **Claim ↔ GitHub/Publications** | Skills vs repos, papers, certifications | Multiple sources = more trust |
| **Seniority ↔ Trajectory** | Title vs years, tenure, progression | Detects title inflation |

### Geometric Mean Aggregation

```
ECS = (A^0.35 × B^0.30 × C^0.20 × D^0.15) ^ (1/1.0)
```

One contradiction kills the score:
- All consistent (0.9 each): ECS = 0.90
- One contradiction (0.9, 0.9, 0.9, 0.2): ECS = 0.58

## Architecture

```
100K Candidates
    ↓
[Feature Extraction] → 75 features per candidate (sentinel-safe)
    ↓
[4-Axis ECS] → Evidence Consistency Score (geometric mean)
    ↓
[Semantic JD Match] → sentence-transformers cosine similarity (top 500)
    ↓
[Heuristic Scoring] → ECS × SkillDensity × Engagement × Experience × (1-Gate) × EngBonus × JD_Sim
    ↓
[LightGBM LambdaMART] → Learned ranking from weak-supervision labels (10K subsample)
    ↓
[Score Blend] → 60% LightGBM + 40% Heuristic
    ↓
[Behavioral Twin Resolution] → KMeans clustering + counterfactual analysis
    ↓
[MMR Diversity] → Maximal Marginal Relevance (λ=0.15, 8 dimensions)
    ↓
[Honeypot Detection] → Impossible timelines, expert-without-evidence, skill stuffing
    ↓
Ranked CSV (100 candidates) + ranked_profiles.json
```

## Results

| Metric | Value |
|--------|-------|
| NDCG@10 | 0.151 (+11% from baseline) |
| NDCG@50 | 0.159 |
| P@10 Technical | 100% |
| Honeypots in Top 100 | 0 |
| Runtime | 119s (CPU-only) |

## Key Design Decisions

### 1. Geometric Mean ECS (Not Additive)
One contradiction tanks the entire score. Mathematically catches fraud that weighted averages miss.

### 2. Semantic JD Matching
Sentence-transformers compute cosine similarity between profiles and the actual job description. Ranking is role-specific, not generic.

### 3. Twin Resolution + Counterfactuals
Candidates are clustered into behavioral twins. For each top candidate, we find their closest twin and explain **why they outrank them**.

### 4. MMR Diversity Control
Maximal Marginal Relevance ensures the top 100 has diverse archetypes across experience levels, skill domains, and engagement patterns.

### 5. Honeypot Detection
Multi-pattern fraud detection: impossible timelines, expert claims without assessments, skill stuffing, no-engagement profiles.

### 6. Feature-Based Reasoning (No LLM)
Every reasoning sentence sourced from actual features. No hallucination. Deterministic.

## Usage

```bash
pip install -r requirements.txt
python rank.py          # Generate ranked_candidates.csv + ranked_profiles.json
streamlit run app.py    # Launch dashboard
```

## Submission Artifacts

| Artifact | Description |
|----------|-------------|
| `ranked_candidates.csv` | 100 rows: candidate_id, rank, score, reasoning, ecs, jd_similarity, ai_skill_count |
| `ranked_profiles.json` | 100 candidate profiles for Streamlit dashboard |
| `app.py` | Streamlit dashboard (mandatory per spec) |
| `submission_metadata.yaml` | Declarations, compute specs, methodology |

## Files

| File | Description |
|------|-------------|
| `rank.py` | Main pipeline — features + ECS + LightGBM + twin + MMR + reasoning |
| `features.py` | 75-feature extraction (sentinel-safe, JD keyword matching, career history) |
| `evidence.py` | 4-axis ECS geometric mean + JD-specific ECS bonus |
| `reasoning.py` | Concise ≤300 char deterministic reasoning |
| `config.py` | Calibrated constants, weights, AI skill keywords |
| `app.py` | Streamlit dashboard entry point |
| `ui/` | Dashboard modules (nav, pages, styles, data) |
| `requirements.txt` | Python dependencies |

## Competition Constraints

- CPU-only (no GPU) ✓
- No network access during evaluation ✓
- ≤5 minutes runtime ✓ (119s)
- ≤16GB RAM ✓
