"""
Corroborated Evidence Ranking Engine — Final Pipeline

All components:
  1. Feature extraction (52 features, sentinel-safe)
  2. 4-axis Evidence Consistency Engine (geometric mean)
  3. JD disqualifier gates (soft multiplicative penalties)
  4. LightGBM LambdaMART (weak-supervision labels)
  5. Behavioral Twin Resolution (KMeans + counterfactuals)
  6. Deterministic reasoning (no LLM, no hallucination)
  7. Local validation (NDCG estimate)
  8. Tie-breaking by candidate_id ascending

Usage:
  python rank.py                           # auto-detect data dir
  python rank.py <data_dir> <output_csv>   # explicit paths
"""

import os, sys, json, time, warnings, gc
import numpy as np
import pandas as pd
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from features import load_candidates, extract_candidate_features, compute_semantic_jd_similarity
from evidence import compute_ecs
from reasoning import generate_reasoning
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
try:
    import lightgbm as lgb
    HAS_LGBM = True
except ImportError:
    HAS_LGBM = False

TECH_KW = ["engineer","developer","scientist","architect","sre","machine learning",
           "data scien","ai ","nlp","backend","frontend","full stack","mobile",
           "python","java",".net","cloud","devops","search engineer","applied scien"]
NON_TECH_KW = ["hr","human resource","accountant","mechanical","civil","sales",
               "business development","content","writer","copywriter","designer","graphic"]
N_CLUSTERS = 20


def find_data_dir():
    """Auto-detect data directory containing candidates.jsonl."""
    # Check command-line first
    if len(sys.argv) >= 2:
        return sys.argv[1]
    # Walk from script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for root, dirs, files in os.walk(script_dir):
        if "candidates.jsonl" in files:
            return root
    # Walk from current directory
    for root, dirs, files in os.walk(os.getcwd()):
        if "candidates.jsonl" in files:
            return root
    print("ERROR: candidates.jsonl not found. Pass data_dir as argument.")
    sys.exit(1)


def find_jsonl(data_dir):
    """Find candidates.jsonl in data_dir or subdirectories."""
    if os.path.isfile(data_dir) and data_dir.endswith(".jsonl"):
        return data_dir
    for root, dirs, files in os.walk(data_dir):
        for f in files:
            if f == "candidates.jsonl":
                return os.path.join(root, f)
    return ""


def get_output_path():
    """Get output CSV path from args or default."""
    if len(sys.argv) >= 3:
        return sys.argv[2]
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "ranked_candidates.csv")


# ─── Scoring Components ─────────────────────────────────────────────────

def compute_gate(df):
    gate = pd.Series(0.0, index=df.index)
    for c, w in [("is_hr",.45),("is_accountant",.45),("is_sales",.35),
                 ("is_content_writer",.35),("is_designer",.35),
                 ("is_civil",.35),("is_mechanical",.35),("consulting_only",.25)]:
        gate += df[c].astype(float) * w
    return gate.clip(upper=0.6)


def compute_skill_density(df):
    return (df["ai_skill_count"].astype(float)*0.35 + df["skill_count"].astype(float)/30*0.25 +
            df["github_activity"].astype(float)/100*0.15 + df["has_deployment_evidence"].astype(float)*0.15 +
            df["has_github"].astype(float)*0.10)


def compute_engagement(df):
    return (df["response_rate"].astype(float)*0.30 + df["interview_completion"].astype(float)*0.25 +
            df["offer_acceptance"].astype(float)*0.20 + df["profile_views"].astype(float)/500*0.15 +
            df["recruiter_saves"].astype(float)/50*0.10)


def compute_experience(df):
    return (df["years_of_experience"].astype(float)/10*0.30 + df["max_tenure_months"].astype(float)/60*0.25 +
            df["company_count"].astype(float)/5*0.20 + df["has_deployment_evidence"].astype(float)*0.25)


# ─── Counterfactual Generator ───────────────────────────────────────────

def generate_counterfactual(df, top_idx, clusters, i):
    """Generate specific counterfactual for candidate at position i in top_idx."""
    cid = top_idx[i]
    c = clusters[i]
    same = [j for j in range(len(top_idx)) if clusters[j] == c and j != i]
    if not same:
        return "unique profile — no comparable candidate in cluster"

    # Pre-compute feature arrays for speed
    ecs_arr = df.loc[top_idx, "ecs"].values.astype(float)
    resp_arr = df.loc[top_idx, "response_rate"].values.astype(float)
    ai_arr = df.loc[top_idx, "ai_skill_count"].values.astype(float)
    yoe_arr = df.loc[top_idx, "years_of_experience"].values.astype(float)
    deploy_arr = df.loc[top_idx, "has_deployment_evidence"].values.astype(float)
    profile_arr = df.loc[top_idx, "profile_completeness"].values.astype(float)
    endorse_arr = df.loc[top_idx, "total_endorsements"].values.astype(float)
    tenure_arr = df.loc[top_idx, "max_tenure_months"].values.astype(float)
    skill_arr = df.loc[top_idx, "skill_count"].values.astype(float)
    gh_arr = df.loc[top_idx, "github_activity"].values.astype(float)

    # Find closest twin by feature distance
    tc = ["ecs","years_of_experience","ai_skill_count","github_activity",
          "is_engineer","response_rate","skill_count","has_deployment_evidence","max_tenure_months"]
    td = df.loc[top_idx, tc].replace([np.inf,-np.inf],0).fillna(0).values.astype(float)
    cv = td[i]
    best_d, best_j = float("inf"), same[0]
    for j in same[:30]:
        d = np.linalg.norm(cv - td[j])
        if d < best_d:
            best_d, best_j = d, j

    twin = top_idx[best_j]
    j = best_j

    # Compare every dimension to find the MOST differentiating one
    comparisons = []
    de = ecs_arr[i] - ecs_arr[j]
    dr = resp_arr[i] - resp_arr[j]
    da = ai_arr[i] - ai_arr[j]
    dy = yoe_arr[i] - yoe_arr[j]
    dd = deploy_arr[i] - deploy_arr[j]
    dp = profile_arr[i] - profile_arr[j]
    den = endorse_arr[i] - endorse_arr[j]
    dt = tenure_arr[i] - tenure_arr[j]
    ds = skill_arr[i] - skill_arr[j]
    dg = gh_arr[i] - gh_arr[j]

    if abs(de) > 0.1:
        comparisons.append(f"evidence consistency ({ecs_arr[i]:.2f} vs {ecs_arr[j]:.2f})")
    if abs(da) > 2:
        comparisons.append(f"AI skill depth ({int(ai_arr[i])} vs {int(ai_arr[j])} skills)")
    if abs(dr) > 0.15:
        comparisons.append(f"recruiter engagement ({resp_arr[i]:.0%} vs {resp_arr[j]:.0%} response)")
    if abs(dy) > 2:
        comparisons.append(f"experience ({yoe_arr[i]:.1f} vs {yoe_arr[j]:.1f} yrs)")
    if abs(dt) > 12:
        comparisons.append(f"career stability ({tenure_arr[i]:.0f} vs {tenure_arr[j]:.0f} mo max tenure)")
    if abs(den) > 10:
        comparisons.append(f"peer recognition ({int(endorse_arr[i])} vs {int(endorse_arr[j])} endorsements)")
    if abs(dp) > 15:
        comparisons.append(f"profile completeness ({profile_arr[i]:.0f} vs {profile_arr[j]:.0f})")
    if abs(dg) > 20:
        comparisons.append(f"GitHub activity ({gh_arr[i]:.0f} vs {gh_arr[j]:.0f})")

    if comparisons:
        return f"outranks closest twin by {comparisons[0]}" + (f" + {comparisons[1]}" if len(comparisons) > 1 else "")
    else:
        return f"marginally stronger across all signals (distance: {best_d:.2f})"


# ─── Validation ─────────────────────────────────────────────────────────

def local_validation(df, cand_map):
    """Estimate ranking quality using heuristic ground truth."""
    # Build heuristic ground truth: score based on title relevance + AI skills + deployment
    gt = pd.Series(0.0, index=df.index)
    gt += df["is_engineer"].astype(float) * 3.0
    gt += (df["ai_skill_count"].astype(float) > 0).astype(float) * 2.0
    gt += (df["ai_skill_count"].astype(float) > 3).astype(float) * 1.0
    gt += df["has_deployment_evidence"].astype(float) * 1.5
    gt += df["has_production_metrics"].astype(float) * 1.0
    gt += df["response_rate"].astype(float) * 1.0
    gt -= (df["is_hr"] + df["is_accountant"] + df["is_sales"] +
           df["is_content_writer"] + df["is_designer"] +
           df["is_civil"] + df["is_mechanical"]).astype(float) * 3.0

    gt_ranked = gt.sort_values(ascending=False)
    our_ranked = df["score"].sort_values(ascending=False)

    # NDCG@10 estimate
    def ndcg_at_k(pred, ideal, k):
        def dcg(scores):
            return sum(s / np.log2(i + 2) for i, s in enumerate(scores[:k]))
        ideal_dcg = dcg(ideal.values[:k])
        pred_scores = [pred.get(idx, 0) for idx in ideal.index[:k]]
        pred_dcg = sum(s / np.log2(i + 2) for i, s in enumerate(pred_scores[:k]))
        return pred_dcg / ideal_dcg if ideal_dcg > 0 else 0

    our_dict = our_ranked.to_dict()
    n10 = ndcg_at_k(our_dict, gt_ranked, 10)
    n50 = ndcg_at_k(our_dict, gt_ranked, 50)

    # P@10: fraction of top 10 that are technical
    top10_ids = list(our_ranked.index[:10])
    p10 = sum(1 for cid in top10_ids
              if any(k in cand_map.get(cid,{}).get("profile",{}).get("current_title","").lower()
                     for k in TECH_KW)) / 10

    # Honeypot rate
    honeypots = sum(1 for cid in list(our_ranked.index[:100])
                    if any(k in cand_map.get(cid,{}).get("profile",{}).get("current_title","").lower()
                           for k in NON_TECH_KW)) / 100

    return {"NDCG@10": n10, "NDCG@50": n50, "P@10": p10, "honeypot_rate": honeypots}


# ─── Main Pipeline ───────────────────────────────────────────────────────

def main():
    T0 = time.time()

    data_dir = find_data_dir()
    output = get_output_path()
    jsonl = find_jsonl(data_dir)
    if not jsonl:
        print("ERROR: candidates.jsonl not found"); return

    # 1. Load
    print("=" * 65)
    print("CORROBORATED EVIDENCE RANKING ENGINE")
    print("=" * 65)
    cands = load_candidates(jsonl)
    cm = {c["candidate_id"]: c for c in cands}
    print(f"\n[1/7] Loaded {len(cands)} candidates ({time.time()-T0:.0f}s)")

    # 2. Features + ECS
    print("\n[2/7] Feature extraction + ECS...")
    fd = {}
    for i, c in enumerate(cands):
        cid = c["candidate_id"]
        f = extract_candidate_features(c)
        e = compute_ecs(f)
        f["ecs"] = e["ecs"]
        f["axes_consistent"] = e["axes_consistent"]
        f["contradictions"] = e["contradictions"]
        f["axis_a_score"] = e["axis_a_score"]
        f["axis_b_score"] = e["axis_b_score"]
        f["axis_c_score"] = e["axis_c_score"]
        f["axis_d_score"] = e["axis_d_score"]
        fd[cid] = f
        if (i+1) % 25000 == 0: print(f"  {i+1}...")

    del cands; gc.collect()
    df = pd.DataFrame(fd).T
    for col in df.columns:
        if col != "contradictions":
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    print(f"  {df.shape[1]} features, ECS: mean={df['ecs'].astype(float).mean():.3f}, "
          f"range=[{df['ecs'].astype(float).min():.3f}, {df['ecs'].astype(float).max():.3f}]"
          f" ({time.time()-T0:.0f}s)")

    # 2b. Semantic JD similarity (only for top 500 candidates by heuristic score)
    print("\n[2b/7] Semantic JD similarity...")
    jd_text = ""
    for root_dir, dirs, files in os.walk(data_dir):
        for f_name in files:
            if "job_description" in f_name.lower() or "jd" in f_name.lower():
                jd_path = os.path.join(root_dir, f_name)
                try:
                    if f_name.endswith(".docx"):
                        from docx import Document
                        doc = Document(jd_path)
                        jd_text = " ".join([p.text for p in doc.paragraphs])
                    elif f_name.endswith(".txt"):
                        with open(jd_path, "r", encoding="utf-8", errors="ignore") as fh:
                            jd_text = fh.read()
                    print(f"  Loaded JD from: {jd_path} ({len(jd_text)} chars)")
                except Exception as e:
                    print(f"  Could not load JD: {e}")

    if jd_text:
        pre_scores = {}
        for cid, feat_dict in fd.items():
            pre_scores[cid] = (feat_dict.get("ecs", 0) * 0.4 + feat_dict.get("ai_skill_count", 0) / 10 * 0.3 +
                               feat_dict.get("avg_proficiency", 0) / 5 * 0.3)
        top500_cids = sorted(pre_scores, key=pre_scores.get, reverse=True)[:500]
        top500_cands = [cm[cid] for cid in top500_cids if cid in cm]
        jd_scores = compute_semantic_jd_similarity(top500_cands, jd_text)
        df["jd_similarity"] = df.index.map(lambda x: jd_scores.get(x, 0.0))
        print(f"  JD similarity: mean={df['jd_similarity'].mean():.4f}, "
              f"range=[{df['jd_similarity'].min():.4f}, {df['jd_similarity'].max():.4f}]")
    else:
        df["jd_similarity"] = 0.0
        print("  No JD found, skipping semantic similarity")
    print(f"  ({time.time()-T0:.0f}s)")

    # 3. Heuristic score
    print("\n[3/7] Heuristic scoring...")
    gate = compute_gate(df)

    # Honeypot detection: impossible profiles
    honeypot = pd.Series(0.0, index=df.index)
    # YoE claimed but no career history
    honeypot += ((df["years_of_experience"].astype(float) > 3) & (df["total_duration_months"].astype(float) < 12)).astype(float) * 0.5
    # Expert claims with < 2 years
    honeypot += ((df["avg_proficiency"].astype(float) > 3) & (df["years_of_experience"].astype(float) < 2)).astype(float) * 0.4
    # 50+ skills listed (keyword stuffing)
    honeypot += (df["skill_count"].astype(float) > 50).astype(float) * 0.3
    # Advanced/expert but zero assessments and zero GitHub
    honeypot += ((df["claim_assessment_consistency"].astype(float) > 0.7) &
                 (df["assessment_count"].astype(float) == 0) &
                 (df["has_github"].astype(float) == 0)).astype(float) * 0.2
    gate = (gate + honeypot).clip(upper=0.8)
    is_eng = df["is_engineer"].astype(float)
    is_nt = (df["is_hr"]+df["is_accountant"]+df["is_sales"]+df["is_content_writer"]+
             df["is_designer"]+df["is_civil"]+df["is_mechanical"]).astype(float)
    eng_b = (1.0 + is_eng*0.7 - is_nt*0.4).clip(lower=0.3)

    skill_d = compute_skill_density(df)
    engage = compute_engagement(df)
    exp = compute_experience(df)

    heuristic = (df["ecs"].astype(float)*0.25 + skill_d*0.25 + engage*0.15 + exp*0.15 + (1-gate)*0.10 + df["jd_similarity"].astype(float)*0.10) * eng_b
    print(f"  Heuristic range: [{heuristic.min():.4f}, {heuristic.max():.4f}]")

    # 4. LightGBM LambdaMART (train on 10K subsample)
    print("\n[4/7] LightGBM LambdaMART...")
    if HAS_LGBM:
        try:
            X_cols = ["ecs","axis_a_score","axis_b_score","axis_c_score","axis_d_score",
                      "response_rate","interview_completion","offer_acceptance",
                      "years_of_experience","max_tenure_months","company_count",
                      "ai_skill_count","backend_skill_count","data_skill_count",
                      "skill_count","avg_proficiency","has_deployment_evidence",
                      "has_production_metrics","is_engineer","consulting_only",
                      "has_github","github_activity","claim_assessment_consistency",
                      "jd_similarity"]
            X_all = df[X_cols].astype(float).fillna(0)
            y_all = (df["is_engineer"]*2 + (df["ai_skill_count"]>0).astype(float)*1.5 +
                     df["has_deployment_evidence"] + df["has_production_metrics"] +
                     (df["response_rate"]>0.7).astype(float)*0.5 +
                     (df["interview_completion"]>0.7).astype(float)*0.5 -
                     is_nt*2.5 - df["consulting_only"]*1.5 +
                     df["jd_similarity"].astype(float)*1.5)
            y_all = ((y_all-y_all.min())/(y_all.max()-y_all.min()+1e-6)*4).round().astype(int)

            np.random.seed(42)
            idx = np.random.choice(len(df), min(10000, len(df)), replace=False)
            ds = lgb.Dataset(X_all.iloc[idx].values, label=y_all.iloc[idx].values,
                             group=[min(10000, len(idx))], feature_name=list(X_all.columns))
            m = lgb.train({"objective":"lambdarank","metric":"ndcg","eval_at":[10,50],
                           "num_leaves":31,"learning_rate":0.05,"feature_fraction":0.8,
                           "verbose":-1,"num_threads":4,"label_gain":[0,1,2,3,4],
                           "seed":42},
                          ds, num_boost_round=100, callbacks=[lgb.log_evaluation(0)])
            p = m.predict(X_all.values)
            p = (p-p.min())/(p.max()-p.min()+1e-6)
            df["lgbm"] = p
            df["score"] = df["lgbm"]*0.60 + heuristic*0.40
            imp = pd.DataFrame({"f":X_all.columns,"i":m.feature_importance()}).sort_values("i",ascending=False)
            print(f"  Top features: {imp.head(5)['f'].tolist()}")
            print(f"  Score range: [{df['score'].min():.4f}, {df['score'].max():.4f}]")
        except Exception as ex:
            print(f"  Failed: {ex}")
            df["score"] = heuristic
    else:
        df["score"] = heuristic
        print("  Skipped (not installed)")
    print(f"  ({time.time()-T0:.0f}s)")

    # 5. Twin resolution on top 300
    print("\n[5/7] Twin resolution (top 300)...")
    top300 = df.nlargest(300, "score").index
    tc = ["ecs","years_of_experience","ai_skill_count","github_activity",
          "is_engineer","response_rate","skill_count","has_deployment_evidence","max_tenure_months"]
    td = df.loc[top300, tc].replace([np.inf,-np.inf],0).fillna(0).values.astype(float)
    scaled = StandardScaler().fit_transform(td)
    nc = min(15, len(td)//10)
    km = KMeans(n_clusters=nc, random_state=42, n_init=3, max_iter=50)
    cl = km.fit_predict(scaled)

    # Cluster quality bonus
    cq = {}
    for cid in range(nc):
        mask = cl == cid
        if mask.sum() == 0: continue
        r = df.loc[top300[mask], "response_rate"].values.astype(float)
        a = df.loc[top300[mask], "interview_completion"].values.astype(float)
        ai = df.loc[top300[mask], "ai_skill_count"].values.astype(float)
        cq[cid] = r.mean()*0.4 + a.mean()*0.3 + min(ai.mean()/5,1)*0.3

    scores_arr = df.loc[top300, "score"].values.copy()
    for i in range(len(top300)):
        scores_arr[i] *= (0.92 + cq.get(cl[i], 0.5) * 0.08)
    df.loc[top300, "score"] = scores_arr

    # Counterfactuals for top 150
    counterfactuals = {}
    for i in range(min(150, len(top300))):
        counterfactuals[top300[i]] = generate_counterfactual(df, top300, cl, i)
    print(f"  {nc} clusters, {len(counterfactuals)} counterfactuals ({time.time()-T0:.0f}s)")

    # 5b. MMR diversity: ensure top 100 has diverse archetypes
    print("\n[5b/7] MMR diversity (top 100)...")
    mmr_cols = ["ecs","jd_similarity","years_of_experience","ai_skill_count",
                "response_rate","skill_count","is_engineer","max_tenure_months"]
    mmr_data = df.loc[list(top300), mmr_cols].replace([np.inf,-np.inf],0).fillna(0).values.astype(float)
    mmr_scaler = StandardScaler()
    mmr_scaled = mmr_scaler.fit_transform(mmr_data)

    selected = [0]
    remaining = list(range(1, len(top300)))
    lambda_div = 0.15

    for _ in range(min(99, len(remaining))):
        best_idx = -1
        best_mmr = -1e9
        for idx in remaining:
            relevance = float(df.loc[top300[idx], "score"])
            max_sim = max(float(np.dot(mmr_scaled[idx], mmr_scaled[s]))
                         / (np.linalg.norm(mmr_scaled[idx]) * np.linalg.norm(mmr_scaled[s]) + 1e-6)
                         for s in selected)
            mmr_score = (1 - lambda_div) * relevance - lambda_div * max_sim
            if mmr_score > best_mmr:
                best_mmr = mmr_score
                best_idx = idx
        if best_idx >= 0:
            selected.append(best_idx)
            remaining.remove(best_idx)

    # Apply MMR reordering to top 100
    mmr_order = [top300[i] for i in selected]
    # Keep remaining from original sort
    remaining_top = [c for c in df.head(300).index if c not in mmr_order]
    final_order = mmr_order + remaining_top[:max(0, 100 - len(mmr_order))]
    df_mmr = df.loc[final_order].copy()
    df_mmr["candidate_id"] = df_mmr.index
    df_mmr["score_r"] = df_mmr["score"].round(4)
    df_mmr = df_mmr.sort_values(["score_r","candidate_id"], ascending=[False,True])
    df = df_mmr
    top100 = df.head(100)
    print(f"  MMR diversity applied: {len(mmr_order)} MMR-selected ({time.time()-T0:.0f}s)")

    rows = []
    for rank, (cid, row) in enumerate(top100.iterrows(), 1):
        c = cm.get(cid, {})
        title = c.get("profile",{}).get("current_title","Unknown")
        yoe = c.get("profile",{}).get("years_of_experience",0)
        cf = counterfactuals.get(cid, "")
        ecs_d = {"ecs":float(row["ecs"]),"axes_consistent":int(row["axes_consistent"]),
                 "contradictions":row.get("contradictions",[])}
        r_text = generate_reasoning(rank, row.to_dict(), ecs_d, cf, title, yoe)
        rows.append({
            "candidate_id":cid,"rank":rank,"score":float(row["score_r"]),"reasoning":r_text,
            "ecs":float(row["ecs"]),"jd_similarity":float(row.get("jd_similarity",0)),
            "ai_skill_count":int(row.get("ai_skill_count",0)),
            "response_rate":float(row.get("response_rate",0)),
            "interview_completion":float(row.get("interview_completion",0)),
            "years_of_experience":yoe,
        })

    out = pd.DataFrame(rows)
    out.to_csv(output, index=False)

    # Save lightweight profiles JSON for Streamlit app
    profiles_for_app = {}
    for cid in df.head(100).index:
        c = cm.get(cid, {})
        profiles_for_app[cid] = {
            "profile": c.get("profile", {}),
            "skills": c.get("skills", []),
            "career_history": c.get("career_history", []),
            "redrob_signals": c.get("redrob_signals", {}),
            "projects": c.get("projects", []),
            "publications": c.get("publications", []),
        }
    profiles_path = os.path.join(os.path.dirname(output), "ranked_profiles.json")
    with open(profiles_path, "w", encoding="utf-8") as f:
        json.dump(profiles_for_app, f)
    print(f"  Saved {len(profiles_for_app)} profiles to {profiles_path}")

    # 7. Validation
    print("\n[7/7] Local validation...")
    metrics = local_validation(df, cm)
    print(f"  NDCG@10 (est): {metrics['NDCG@10']:.3f}")
    print(f"  NDCG@50 (est): {metrics['NDCG@50']:.3f}")
    print(f"  P@10:          {metrics['P@10']:.1%}")
    print(f"  Honeypot rate: {metrics['honeypot_rate']:.1%}")

    # Summary
    tech = sum(1 for _,r in out.iterrows()
               if any(k in cm.get(r["candidate_id"],{}).get("profile",{}).get("current_title","").lower() for k in TECH_KW))
    print(f"\n{'='*65}")
    print(f"DONE in {time.time()-T0:.0f}s | Output: {output}")
    print(f"{'='*65}")
    for _,r in out.head(10).iterrows():
        c=cm.get(r["candidate_id"],{})
        t=c.get("profile",{}).get("current_title","?")
        y=c.get("profile",{}).get("years_of_experience",0)
        print(f"  #{r['rank']} {r['candidate_id']} | {t} ({y}y) | {r['score']:.4f}")
    print(f"\nTech: {tech}/100 | Non-tech: {100-tech}/100 | Honeypots: {metrics['honeypot_rate']:.0%}")

    # Counterfactual variety
    cf_types = {}
    for cf in counterfactuals.values():
        key = cf.split("—")[0].split(",")[0].strip()[:30]
        cf_types[key] = cf_types.get(key, 0) + 1
    print(f"\nCounterfactual variety: {len(cf_types)} unique types")
    for k, v in sorted(cf_types.items(), key=lambda x: -x[1])[:5]:
        print(f"  [{v}x] {k}")

    return out


if __name__ == "__main__":
    main()
