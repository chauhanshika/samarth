import json
import os

import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.metrics.pairwise import cosine_similarity

from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier

# -----------------------------
# CONSTANT PATHS (shared)
# -----------------------------
DATA_DIR = "data"
JOBS_PATH = os.path.join(DATA_DIR, "jobs.json")
STUDENTS_PATH = os.path.join(DATA_DIR, "students_demo.json")
TRAINING_PAIRS_CSV = os.path.join(DATA_DIR, "training_pairs.csv")

MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, "xgb_match_model.json")


# -----------------------------
# Helper functions
# -----------------------------
def parse_duration_to_months(duration_str: str) -> float:
    if not isinstance(duration_str, str):
        return 0.0
    s = duration_str.lower().strip()
    if "month" in s:
        num = "".join(ch for ch in s if ch.isdigit())
        return float(num) if num else 0.0
    if "week" in s:
        num = "".join(ch for ch in s if ch.isdigit())
        weeks = float(num) if num else 0.0
        return weeks / 4.0
    if "year" in s:
        num = "".join(ch for ch in s if ch.isdigit())
        years = float(num) if num else 0.0
        return years * 12.0
    return 0.0


def simple_location_tokens(loc_str: str):
    if not isinstance(loc_str, str):
        return set()
    loc_str = loc_str.lower().replace(",", " ")
    return set(loc_str.split())


def jaccard(set1, set2):
    if not set1 or not set2:
        return 0.0
    inter = len(set1 & set2)
    union = len(set1 | set2)
    return inter / union if union > 0 else 0.0


def build_domain_from_title(title: str):
    if not isinstance(title, str):
        return "other"
    t = title.lower()
    if "data science" in t or "data analyst" in t:
        return "data science"
    if "machine learning" in t or "aiml" in t or " ai" in t:
        return "machine learning"
    if "python" in t:
        return "python"
    if "web" in t or "full stack" in t or "frontend" in t:
        return "web development"
    if "android" in t or "app" in t or "mobile" in t:
        return "app development"
    if "cyber" in t or "security" in t:
        return "cyber security"
    if "devops" in t or "cloud" in t:
        return "cloud devops"
    if "digital marketing" in t or "marketing" in t:
        return "digital marketing"
    if "vlsi" in t or "embedded" in t:
        return "vlsi/embedded"
    return "other"


def build_domain_from_student(preferred_domains: str):
    if not isinstance(preferred_domains, str):
        return []
    return [d.strip().lower() for d in preferred_domains.split(",") if d.strip()]


# -----------------------------
# MAIN TRAINING PIPELINE
# -----------------------------
def main():
    # 1) Load data
    print("Loading internships from:", JOBS_PATH)
    jobs_df = pd.read_json(JOBS_PATH)

    print("Loading students from:", STUDENTS_PATH)
    with open(STUDENTS_PATH, "r", encoding="utf-8") as f:
        students = json.load(f)
    students_df = pd.DataFrame(students)

    # 2) Prepare internship features
    jobs_df["duration_months"] = jobs_df["duration"].apply(parse_duration_to_months)
    jobs_df["job_title_clean"] = jobs_df["job_title"].fillna("").str.lower()
    jobs_df["location_tokens"] = jobs_df["location"].apply(simple_location_tokens)
    jobs_df["domain_auto"] = jobs_df["job_title"].apply(build_domain_from_title)

    # TF-IDF vectors for job text (title + description)
    text_corpus = (
        jobs_df["job_title"].fillna("") + " " + jobs_df["description"].fillna("")
    ).tolist()

    vectorizer = TfidfVectorizer(max_features=5000)
    job_tfidf = vectorizer.fit_transform(text_corpus)

    # 3) Build student-internship pairs with features + weak labels
    pairs = []

    for _, srow in students_df.iterrows():
        sid = srow["student_id"]

        s_skills = str(srow.get("skills", "")).lower()
        s_domains = build_domain_from_student(srow.get("preferred_domains", ""))
        s_loc_pref = [
            l.strip().lower()
            for l in str(srow.get("preferred_locations", "")).split(",")
            if l.strip()
        ]
        s_loc_pref_set = set(s_loc_pref)
        s_wfh_pref = str(srow.get("wfh_preference", "Any"))
        s_min_dur = float(srow.get("min_duration_months", 0))
        s_cgpa = float(srow.get("cgpa", 0))

        # EXPERIENCE FLAGS (simple, from radio/dropdown)
        has_exp_str = str(srow.get("has_internship_experience", "No")).strip().lower()
        experience_level_str = (
            str(srow.get("experience_level", "Fresher")).strip().lower()
        )
        rel_exp_str = str(srow.get("has_relevant_experience", "No")).strip().lower()

        has_exp_flag = 1 if has_exp_str == "yes" else 0

        if "2+" in experience_level_str:
            exp_level_num = 2
        elif "1" in experience_level_str:
            exp_level_num = 1
        else:
            exp_level_num = 0  # Fresher

        rel_exp_flag = 1 if rel_exp_str == "yes" else 0

        # skill tokens
        s_skill_tokens = set(s_skills.replace(",", " ").split())

        # student text for TF-IDF based similarity
        student_text = " ".join(
            [
                s_skills,
                " ".join(s_domains),
                " ".join(s_loc_pref),
                str(srow.get("degree", "")),
            ]
        ).strip()

        student_vec = vectorizer.transform([student_text])

        # Sample some internships for training (to keep size manageable)
        sampled_jobs = jobs_df.sample(min(100, len(jobs_df)), random_state=sid)

        for _, jrow in sampled_jobs.iterrows():
            jid = jrow["job_id"]
            job_title = jrow["job_title_clean"]
            job_loc_tokens = jrow["location_tokens"]
            job_wfh = str(jrow.get("wfh", ""))
            job_duration = float(jrow.get("duration_months", 0))
            job_domain = jrow.get("domain_auto", "other")

            # Index in original jobs_df -> job_tfidf row
            job_idx = jrow.name
            job_vec = job_tfidf[job_idx]

            # Skills similarity
            job_keywords = set(job_title.split())
            skills_sim = jaccard(s_skill_tokens, job_keywords)

            # Domain match
            domain_match = 1 if job_domain in s_domains else 0

            # Location similarity
            loc_sim = jaccard(job_loc_tokens, s_loc_pref_set)

            # WFH match
            if s_wfh_pref == "Any":
                wfh_match = 1
            elif s_wfh_pref.lower() in job_wfh.lower():
                wfh_match = 1
            elif s_wfh_pref == "Virtual" and "virtual" in job_wfh.lower():
                wfh_match = 1
            else:
                wfh_match = 0

            # Duration fit
            duration_fit = 1 if job_duration >= s_min_dur else 0

            # Text similarity (TF-IDF cosine)
            if student_vec.nnz == 0 or job_vec.nnz == 0:
                text_sim = 0.0
            else:
                text_sim = float(cosine_similarity(student_vec, job_vec)[0, 0])

            # Weak label: high-ish skills OR text sim AND some domain/location alignment
            if skills_sim > 0.15 and (domain_match == 1 or loc_sim > 0 or skills_sim > 0.3):
                label = 1
            else:
                label = 0

            pairs.append(
                {
                    "student_id": sid,
                    "job_id": jid,
                    "skills_sim": skills_sim,
                    "domain_match": domain_match,
                    "loc_sim": loc_sim,
                    "wfh_match": wfh_match,
                    "duration_fit": duration_fit,
                    "student_cgpa": s_cgpa,
                    "job_duration_months": job_duration,
                    "text_sim": text_sim,
                    "has_exp_flag": has_exp_flag,
                    "exp_level_num": exp_level_num,
                    "rel_exp_flag": rel_exp_flag,
                    "label": label,
                }
            )

    pairs_df = pd.DataFrame(pairs)
    print("Total pairs created:", len(pairs_df))
    print("Label distribution:\n", pairs_df["label"].value_counts())

    pairs_df.to_csv(TRAINING_PAIRS_CSV, index=False)
    print("Saved training pairs to:", TRAINING_PAIRS_CSV)

    # 4) Train-test split
    feature_cols = [
        "skills_sim",
        "domain_match",
        "loc_sim",
        "wfh_match",
        "duration_fit",
        "student_cgpa",
        "job_duration_months",
        "text_sim",
        "has_exp_flag",
        "exp_level_num",
        "rel_exp_flag",
    ]

    X = pairs_df[feature_cols].values
    y = pairs_df["label"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    print("Before SMOTE, train label counts:", np.bincount(y_train))

    # 5) SMOTE to handle imbalance
    smote = SMOTE(random_state=42, k_neighbors=1)
    X_train_res, y_train_res = smote.fit_resample(X_train, y_train)

    print("After SMOTE, train label counts:", np.bincount(y_train_res))

    # 6) Train XGBoost
    model = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="binary:logistic",
        eval_metric="auc",
        random_state=42,
    )

    print("Training XGBoost model...")
    model.fit(X_train_res, y_train_res)

    # 7) Evaluate
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    print("Classification report:\n", classification_report(y_test, y_pred))
    print("ROC AUC:", roc_auc_score(y_test, y_proba))

    # 8) Save model
    model.save_model(MODEL_PATH)
    print("Saved XGBoost model to:", MODEL_PATH)


if __name__ == "__main__":
    main()
