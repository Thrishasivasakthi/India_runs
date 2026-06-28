"""
Generate HireProof system architecture diagram.
Output: assets/architecture_diagram.png
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = Path(__file__).parent / "assets" / "architecture_diagram.png"
OUT.parent.mkdir(exist_ok=True)

BG = "#0B3D2E"
PANEL = "#145A42"
BOX = "#1E7A5C"
TEXT = "#FFFFFF"
ACCENT = "#4FD1A5"
ARROW = "#7EE8BC"
BORDER = "#2ECC9A"


def box(ax, x, y, w, h, title, lines, fontsize=8.5):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=1.8, edgecolor=BORDER, facecolor=BOX,
    ))
    ax.text(x + w / 2, y + h - 0.18, title, ha="center", va="top",
            fontsize=fontsize + 1.5, fontweight="bold", color=TEXT, family="serif")
    y_text = y + h - 0.48
    for line in lines:
        ax.text(x + 0.1, y_text, line, ha="left", va="top",
                fontsize=fontsize, color="#DFF7EE", family="serif")
        y_text -= 0.26


def arrow_h(ax, x1, x2, y):
    ax.add_patch(FancyArrowPatch(
        (x1, y), (x2, y), arrowstyle="-|>", mutation_scale=13,
        linewidth=2, color=ARROW, shrinkA=2, shrinkB=2,
    ))


def arrow_v(ax, x, y1, y2):
    ax.add_patch(FancyArrowPatch(
        (x, y1), (x, y2), arrowstyle="-|>", mutation_scale=13,
        linewidth=2, color=ARROW, shrinkA=2, shrinkB=2,
    ))


def main():
    fig, ax = plt.subplots(figsize=(16, 9), facecolor=BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis("off")

    ax.add_patch(FancyBboxPatch(
        (0.3, 8.05), 15.4, 0.75, boxstyle="round,pad=0.02",
        facecolor=PANEL, edgecolor=BORDER, linewidth=2,
    ))
    ax.text(8, 8.42, "HireProof — System Architecture", ha="center", va="center",
            fontsize=22, fontweight="bold", color=TEXT, family="serif")
    ax.text(8, 8.12,
            "4-Axis ECS  ·  LightGBM LambdaMART  ·  Twin Resolution  ·  CPU-only Pipeline",
            ha="center", va="center", fontsize=11, color=ACCENT, family="serif")

    # Row 1 — ingest
    box(ax, 0.35, 6.5, 2.8, 1.3, "INPUT",
        ["candidates.jsonl (100K)", "Job Description", "Profiles · Skills · Signals"])
    box(ax, 3.45, 6.5, 2.8, 1.3, "FEATURE ENGINE",
        ["features.py — 75 features", "Sentinel-safe parsing", "Career & JD extraction"])
    box(ax, 6.55, 6.5, 2.8, 1.3, "GATES & FILTERS",
        ["Non-tech role penalties", "Consulting / research flags", "Honeypot detection"])
    box(ax, 9.65, 6.5, 2.8, 1.3, "JD SEMANTIC MATCH",
        ["sentence-transformers", "Profile-JD cosine sim", "Role-specific relevance"])
    box(ax, 12.75, 6.5, 2.8, 1.3, "BEHAVIORAL",
        ["Response rate · Interview %", "Offer acceptance · Recency", "Engagement multiplier"])

    arrow_h(ax, 3.15, 3.45, 7.15)
    arrow_h(ax, 6.25, 6.55, 7.15)
    arrow_h(ax, 9.35, 9.65, 7.15)
    arrow_h(ax, 12.45, 12.75, 7.15)

    # Row 2 — core scoring
    box(ax, 0.35, 4.35, 4.5, 1.55, "4-AXIS EVIDENCE CONSISTENCY (ECS)",
        ["evidence.py — geometric mean", "A: Claim ↔ Assessment (35%)",
         "B: Claim ↔ Career (30%)  C: Corroboration (20%)  D: Seniority (15%)",
         "One contradiction collapses the score"])
    box(ax, 5.1, 4.35, 3.2, 1.55, "HEURISTIC SCORE",
        ["ECS × skills × engagement", "× experience × JD match", "× (1 − gate penalty)"])
    box(ax, 8.55, 4.35, 3.2, 1.55, "LightGBM LambdaMART",
        ["Learning-to-rank on 10K sample", "Weak-supervision from JD rules", "NDCG-optimized"])
    box(ax, 12.0, 4.35, 3.55, 1.55, "FINAL BLEND",
        ["60% LightGBM + 40% heuristic", "Twin cluster bonus (top 300)", "Deterministic tie-break"])

    arrow_v(ax, 1.75, 6.5, 5.9)
    arrow_v(ax, 4.85, 6.5, 5.9)
    arrow_v(ax, 11.05, 6.5, 5.9)
    arrow_v(ax, 14.15, 6.5, 5.9)
    arrow_h(ax, 4.85, 5.1, 5.12)
    arrow_h(ax, 8.3, 8.55, 5.12)
    arrow_h(ax, 11.75, 12.0, 5.12)

    # Row 3 — output
    box(ax, 0.35, 2.35, 3.5, 1.4, "TWIN RESOLUTION",
        ["KMeans behavioral twins", "Counterfactual: why A > B", "Hidden gem detection"])
    box(ax, 4.1, 2.35, 3.5, 1.4, "MMR DIVERSITY",
        ["Maximal Marginal Relevance", "8-dim diversity (λ=0.15)", "Varied top-100 archetypes"])
    box(ax, 7.85, 2.35, 3.5, 1.4, "REASONING ENGINE",
        ["reasoning.py — ≤300 chars", "Feature-sourced sentences", "No LLM · no hallucination"])
    box(ax, 11.6, 2.35, 3.95, 1.4, "OUTPUT & DEMO",
        ["submission.csv (top 100)", "ranked_profiles.json", "Streamlit dashboard (app.py)"])

    arrow_v(ax, 13.75, 4.35, 3.75)
    arrow_h(ax, 3.85, 4.1, 3.05)
    arrow_h(ax, 7.6, 7.85, 3.05)
    arrow_h(ax, 11.35, 11.6, 3.05)

    # Constraints footer
    ax.add_patch(FancyBboxPatch(
        (0.35, 0.3), 15.3, 1.55, boxstyle="round,pad=0.02",
        facecolor="#0F4D38", edgecolor=BORDER, linewidth=1.5,
    ))
    ax.text(8, 1.45, "All Challenge Constraints Met", ha="center", fontsize=12,
            fontweight="bold", color=ACCENT, family="serif")
    items = [
        "CPU-only (no GPU)", "119 sec runtime", "≤ 16 GB RAM",
        "No network at rank time", "100% tech top-100", "0 honeypots ranked",
    ]
    for i, item in enumerate(items):
        ax.text(0.7 + (i % 3) * 5.1, 0.95 - (i // 3) * 0.38, f"• {item}",
                fontsize=10, color=TEXT, family="serif")

    ax.text(0.35, 0.08,
            "Code modules: rank.py  ·  features.py  ·  evidence.py  ·  reasoning.py  ·  config.py  ·  ui/",
            fontsize=9, color="#A8DCC8", family="serif")

    plt.savefig(OUT, dpi=180, facecolor=BG, bbox_inches="tight", pad_inches=0.12)
    plt.close()
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
