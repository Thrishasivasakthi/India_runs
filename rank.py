import os, sys, json, time, warnings, gc
import numpy as np
import pandas as pd
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from features import load_candidates, extract_candidate_features
from evidence import compute_ecs
from reasoning import generate_reasoning
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
try:
    import lightgbm as lgb
    HAS_LGBM = True
except ImportError:
    HAS_LGBM = False

DATA_DIR = r"C:\Users\thris\Downloads\Resume-hexa-format\hackathon\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge"
OUTPUT = r"C:\Users\thris\Downloads\Resume-hexa-format\hackathon\ranked_candidates.csv"

TECH_KW = ["engineer","developer","scientist","architect","sre","machine learning",
           "data scien","ai ","nlp","backend","frontend","full stack","mobile",
           "python","java",".net","cloud","devops","search engineer","applied scien"]
NON_TECH_KW = ["hr","human resource","accountant","mechanical","civil","sales",
               "business development","content","writer","copywriter","designer","graphic"]

def find_jsonl(d):
    for r,_,fs in os.walk(d):
        for f in fs:
            if f=="candidates.jsonl": return os.path.join(r,f)
    return ""

def main():
    T0 = time.time()

    # 1. Load
    cands = load_candidates(find_jsonl(DATA_DIR))
    cm = {c["candidate_id"]: c for c in cands}
    print(f"[1/5] Loaded {len(cands)} ({time.time()-T0:.0f}s)")

    # 2. Features + ECS
    fd = {}
    for i,c in enumerate(cands):
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
        if (i+1)%25000==0: print(f"  {i+1}...")
    del cands; gc.collect()
    df = pd.DataFrame(fd).T
    for col in df.columns:
        if col != "contradictions":
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    print(f"[2/5] Features: {df.shape} ({time.time()-T0:.0f}s)")

    # 3. Scores
    gate = pd.Series(0.0, index=df.index)
    for c,w in [("is_hr",.45),("is_accountant",.45),("is_sales",.35),
                ("is_content_writer",.35),("is_designer",.35),
                ("is_civil",.35),("is_mechanical",.35),("consulting_only",.25)]:
        gate += df[c].astype(float)*w
    gate = gate.clip(upper=0.6)

    is_eng = df["is_engineer"].astype(float)
    is_nt = (df["is_hr"]+df["is_accountant"]+df["is_sales"]+df["is_content_writer"]+
             df["is_designer"]+df["is_civil"]+df["is_mechanical"]).astype(float)
    eng_b = (1.0 + is_eng*0.7 - is_nt*0.4).clip(lower=0.3)

    skill_d = (df["ai_skill_count"].astype(float)*0.35 + df["skill_count"].astype(float)/30*0.25 +
               df["github_activity"].astype(float)/100*0.15 + df["has_deployment_evidence"].astype(float)*0.15 +
               df["has_github"].astype(float)*0.10)
    engage = (df["response_rate"].astype(float)*0.30 + df["interview_completion"].astype(float)*0.25 +
              df["offer_acceptance"].astype(float)*0.20 + df["profile_views"].astype(float)/500*0.15 +
              df["recruiter_saves"].astype(float)/50*0.10)
    exp = (df["years_of_experience"].astype(float)/10*0.30 + df["max_tenure_months"].astype(float)/60*0.25 +
           df["company_count"].astype(float)/5*0.20 + df["has_deployment_evidence"].astype(float)*0.25)

    df["score"] = (df["ecs"].astype(float)*0.30 + skill_d*0.30 + engage*0.15 + exp*0.15 + (1-gate)*0.10) * eng_b
    print(f"[3/6] Scores computed ({time.time()-T0:.0f}s)")

    # 4. LightGBM LambdaMART (train on 10K subsample, predict all)
    if HAS_LGBM:
        try:
            X_cols = ["ecs","axis_a_score","axis_b_score","axis_c_score","axis_d_score",
                      "response_rate","interview_completion","offer_acceptance",
                      "years_of_experience","max_tenure_months","company_count",
                      "ai_skill_count","backend_skill_count","data_skill_count",
                      "skill_count","avg_proficiency","has_deployment_evidence",
                      "has_production_metrics","is_engineer","consulting_only",
                      "has_github","github_activity","claim_assessment_consistency"]
            X_all = df[X_cols].astype(float).fillna(0)
            y_all = (df["is_engineer"]*2 + (df["ai_skill_count"]>0).astype(float)*1.5 +
                     df["has_deployment_evidence"] + df["has_production_metrics"] +
                     (df["response_rate"]>0.7).astype(float)*0.5 +
                     (df["interview_completion"]>0.7).astype(float)*0.5 -
                     is_nt*2.5 - df["consulting_only"]*1.5)
            y_all = ((y_all-y_all.min())/(y_all.max()-y_all.min()+1e-6)*4).round().astype(int)

            # Train on balanced 10K subsample
            np.random.seed(42)
            idx = np.random.choice(len(df), min(10000, len(df)), replace=False)
            X_tr = X_all.iloc[idx].values
            y_tr = y_all.iloc[idx].values
            groups = [min(10000, len(X_tr))]
            ds = lgb.Dataset(X_tr, label=y_tr, group=groups, feature_name=list(X_all.columns))
            m = lgb.train({"objective":"lambdarank","metric":"ndcg","eval_at":[10,50],
                           "num_leaves":31,"learning_rate":0.05,"feature_fraction":0.8,
                           "verbose":-1,"num_threads":4,"label_gain":[0,1,2,3,4]},
                          ds, num_boost_round=100, callbacks=[lgb.log_evaluation(0)])
            p = m.predict(X_all.values)
            p = (p-p.min())/(p.max()-p.min()+1e-6)
            df["lgbm"] = p
            df["score"] = df["lgbm"]*0.60 + df["score"]*0.40
            imp = pd.DataFrame({"f":X_all.columns,"i":m.feature_importance()}).sort_values("i",ascending=False)
            print(f"  LightGBM OK. Top: {imp.head(3)['f'].tolist()}")
        except Exception as ex:
            print(f"  LightGBM failed: {ex}")
    else:
        print("  LightGBM not installed")
    print(f"[4/6] LightGBM done ({time.time()-T0:.0f}s)")

    # 5. Twin resolution on top 300 only (fast)
    top300 = df.nlargest(300, "score").index
    tc = ["ecs","years_of_experience","ai_skill_count","github_activity",
          "is_engineer","response_rate","skill_count","has_deployment_evidence","max_tenure_months"]
    td = df.loc[top300, tc].replace([np.inf,-np.inf],0).fillna(0).values.astype(float)
    scaled = StandardScaler().fit_transform(td)
    nc = min(15, len(td)//10)
    km = KMeans(n_clusters=nc, random_state=42, n_init=3, max_iter=50)
    cl = km.fit_predict(scaled)

    # Pre-extract needed columns as numpy
    resp_arr = df.loc[top300, "response_rate"].values.astype(float)
    intv_arr = df.loc[top300, "interview_completion"].values.astype(float)
    ai_arr = df.loc[top300, "ai_skill_count"].values.astype(float)
    ecs_arr = df.loc[top300, "ecs"].values.astype(float)

    # Cluster quality bonus
    cq = {}
    for cid in range(nc):
        mask = cl==cid
        if mask.sum()==0: continue
        cq[cid] = resp_arr[mask].mean()*0.4 + intv_arr[mask].mean()*0.3 + min(ai_arr[mask].mean()/5,1)*0.3
    scores_arr = df.loc[top300, "score"].values.copy()
    for i in range(len(top300)):
        q = cq.get(cl[i], 0.5)
        scores_arr[i] *= (0.92 + q * 0.08)
    df.loc[top300, "score"] = scores_arr

    # Counterfactuals for top 150
    counterfactuals = {}
    for i in range(min(150, len(top300))):
        cid = top300[i]
        c = cl[i]
        same = [j for j in range(len(top300)) if cl[j]==c and j!=i][:20]
        if not same:
            counterfactuals[cid] = "unique profile"
            continue
        cv = td[i]
        best_d, best_j = float("inf"), same[0]
        for j in same:
            d = np.linalg.norm(cv - td[j])
            if d < best_d: best_d, best_j = d, j
        twin = top300[best_j]
        de = ecs_arr[i] - ecs_arr[best_j]
        dr = resp_arr[i] - resp_arr[best_j]
        da = ai_arr[i] - ai_arr[best_j]
        if abs(de)>0.1:
            counterfactuals[cid] = f"stronger evidence ({ecs_arr[i]:.2f} vs {ecs_arr[best_j]:.2f})"
        elif abs(dr)>0.2:
            counterfactuals[cid] = f"{'better' if dr>0 else 'lower'} recruiter engagement"
        elif abs(da)>2:
            counterfactuals[cid] = f"{int(ai_arr[i])} vs {int(ai_arr[best_j])} AI skills"
        else:
            counterfactuals[cid] = "balanced profile vs comparable candidate"
    print(f"[5/6] Twin resolution done ({time.time()-T0:.0f}s)")

    # 6. Rank + output
    df["candidate_id"] = df.index
    df["score_r"] = df["score"].round(4)
    df = df.sort_values(["score_r","candidate_id"], ascending=[False,True])
    top100 = df.head(100)

    rows = []
    for rank, (cid, row) in enumerate(top100.iterrows(), 1):
        c = cm.get(cid, {})
        title = c.get("profile",{}).get("current_title","Unknown")
        yoe = c.get("profile",{}).get("years_of_experience",0)
        cf = counterfactuals.get(cid, "")
        ecs_d = {"ecs":float(row["ecs"]),"axes_consistent":int(row["axes_consistent"]),
                 "contradictions":row.get("contradictions",[])}
        r_text = generate_reasoning(rank, row.to_dict(), ecs_d, cf, title, yoe)
        rows.append({"candidate_id":cid,"rank":rank,"score":float(row["score_r"]),"reasoning":r_text})

    out = pd.DataFrame(rows)
    out.to_csv(OUTPUT, index=False)

    tech = sum(1 for _,r in out.iterrows()
               if any(k in cm.get(r["candidate_id"],{}).get("profile",{}).get("current_title","").lower() for k in TECH_KW))
    print(f"\n{'='*60}")
    print(f"DONE in {time.time()-T0:.0f}s")
    print(f"{'='*60}")
    for _,r in out.head(10).iterrows():
        c=cm.get(r["candidate_id"],{})
        print(f"  #{r['rank']} {r['candidate_id']} | {c.get('profile',{}).get('current_title','?')} | {r['score']:.4f}")
    print(f"\nTech: {tech}/100 | Non-tech: {100-tech}/100")
    print(f"\nReasoning:\n  {out.iloc[0]['reasoning'][:200]}")

if __name__=="__main__":
    main()
