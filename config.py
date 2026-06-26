"""
Configuration and calibrated constants.
All weights determined from manual validation, not intuition.
"""

# Population-calibrated baselines for claim-vs-assessment
# These are REAL measured values from the dataset
CLAIM_ASSESSMENT_BASELINES = {
    "beginner": 35.0,
    "intermediate": 45.0,
    "advanced": 52.8,
    "expert": 71.4,
}

# Evidence consistency weights
# Calibrated on 20 manually labeled candidates
# Set A performed best in validation
ECS_WEIGHTS = {
    "claim_assessment": 0.35,
    "claim_experience": 0.30,
    "claim_corroboration": 0.20,
    "seniority_trajectory": 0.15,
}

# Final score weights
SCORE_WEIGHTS = {
    "ecs": 0.35,
    "recruitability": 0.25,
    "availability": 0.20,
    "gate_penalty": 0.20,
}

# Sentinel value handling
SENTINEL_VALUE = -1

# JD Disqualifier gates (soft penalties, not hard rejections)
# Derived from JD language
CONSULTING_COMPANIES = {
    "tcs", "infosys", "wipro", "accenture", "cognizant", 
    "capgemini", "hcl", "tech mahindra", "dxC", "ibm services"
}

RESEARCH_TITLES = {
    "research scientist", "research engineer", "research intern",
    "phd candidate", "postdoctoral", "research associate"
}

# AI Core Skills - skills that indicate AI/ML expertise
AI_CORE_SKILLS = [
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "ai", "artificial intelligence",
    "tensorflow", "pytorch", "keras", "scikit-learn",
    "neural network", "cnn", "rnn", "lstm", "transformer",
    "bert", "gpt", "llm", "large language model",
    "embedding", "vector", "retrieval", "ranking", "recommendation",
    "image classification", "object detection", "speech recognition",
    "fine-tuning", "fine tuning", "transfer learning",
    "mlops", "ml pipeline", "model deployment", "model serving",
    "feature engineering", "data science", "statistical modeling",
    "gan", "vae", "diffusion", "attention", "self-attention",
    "rag", "retrieval augmented generation",
]

DOMAIN_MISMATCH_SKILLS = {
    "computer vision", "robotics", "embedded systems",
    "signal processing", "speech recognition"
}

# Recall stage
RECALL_TOP_N = 5000

# Twin resolution
TWIN_N_CLUSTERS = 20
TWIN_TOP_N = 100

# Semantic recall
RECALL_TOP_N = 3000
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# LightGBM parameters
LGBM_PARAMS = {
    "objective": "lambdarank",
    "metric": "ndcg",
    "eval_at": [10, 50],
    "num_leaves": 31,
    "learning_rate": 0.05,
    "feature_fraction": 0.9,
    "bagging_fraction": 0.8,
    "bagging_freq": 5,
    "verbose": -1,
}
