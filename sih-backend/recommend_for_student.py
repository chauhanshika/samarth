import json

import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from xgboost import XGBClassifier

from train_xgb_model import (
    DATA_DIR,
    JOBS_PATH,
    STUDENTS_PATH,
    MODEL_PATH,
    parse_duration_to_months,
    simple_location_tokens,
    build_domain_from_title,
    build_domain_from_student,
)


def load_xgb_model(path: str) -> XGBClassifier:
    model = XGBClassifier()
    model.load_model(path)
    return model


def split_location_mode(location_str: str):
    """Pan India, Virtual Internship -> ('Pan India,', 'Virtual Internship')"""
    if not isinstance(location_str, str):
        return "", ""
    parts = [p.strip() for p in location_str.split(",") if p.strip()]
    if len(parts) >= 2:
        return parts[0] + ",", ", ".join(parts[1:])
    elif len(parts) == 1:
        return parts[0], ""
    return "", ""


def get_recommendations_for_student_row(
    srow, jobs_df, model, job_tfidf, vectorizer, top_n: int = 10
):
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

    # Experience flags (same logic as training)
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
        exp_level_num = 0
    rel_exp_flag = 1 if rel_exp_str == "yes" else 0

    # Skill tokens
    s_skill_tokens = set(s_skills.replace(",", " ").split())

    # Student text for TF-IDF
    student_text = " ".join(
        [
            s_skills,
            " ".join(s_domains),
            " ".join(s_loc_pref),
            str(srow.get("degree", "")),
        ]
    ).strip()
    student_vec = vectorizer.transform([student_text])

    feature_rows = []
    meta_rows = []

    for _, jrow in jobs_df.iterrows():
        jid = jrow["job_id"]
        job_title_clean = jrow["job_title_clean"]
        job_loc_tokens = jrow["location_tokens"]
        job_wfh = str(jrow.get("wfh", ""))
        job_duration = float(jrow.get("duration_months", 0))
        job_domain = jrow.get("domain_auto", "other")

        job_idx = jrow.name
        job_vec = job_tfidf[job_idx]

        job_keywords = set(job_title_clean.split())
        skills_sim = 0.0 if not job_keywords else (
            sum(1 for w in s_skill_tokens if w in job_keywords)
            / len(s_skill_tokens | job_keywords)
            if s_skill_tokens | job_keywords
            else 0.0
        )

        # Domain match
        domain_match = 1 if job_domain in s_domains else 0

        # Location similarity
        loc_sim = 0.0
        if job_loc_tokens and s_loc_pref_set:
            inter = len(job_loc_tokens & s_loc_pref_set)
            union = len(job_loc_tokens | s_loc_pref_set)
            loc_sim = inter / union if union > 0 else 0.0

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

        # Text similarity
        if student_vec.nnz == 0 or job_vec.nnz == 0:
            text_sim = 0.0
        else:
            text_sim = float(cosine_similarity(student_vec, job_vec)[0, 0])

        feature_rows.append(
            [
                skills_sim,
                domain_match,
                loc_sim,
                wfh_match,
                duration_fit,
                s_cgpa,
                job_duration,
                text_sim,
                has_exp_flag,
                exp_level_num,
                rel_exp_flag,
            ]
        )

        meta_rows.append(
            {
                "job_id": jid,
                "job_title": jrow["job_title"],
                "company_name": jrow.get("company_name", ""),
                "location": jrow.get("location", ""),
                "wfh": jrow.get("wfh", ""),
                "duration": jrow.get("duration", ""),
                "job_link": jrow.get("job_link", ""),
            }
        )

    X_features = np.array(feature_rows)
    scores = model.predict_proba(X_features)[:, 1]

    results_df = pd.DataFrame(meta_rows)
    results_df["match_score"] = scores

    # Sort by score desc
    results_df = results_df.sort_values(by="match_score", ascending=False)

    # Remove near-duplicate internships (title + company + mode + duration)
    results_df = results_df.drop_duplicates(
        subset=["job_title", "company_name", "wfh", "duration"], keep="first"
    )

    # Top N
    results_df = results_df.head(top_n).reset_index(drop=True)

    return results_df


def main():
    print("Loading internships from:", JOBS_PATH)
    jobs_df = pd.read_json(JOBS_PATH)

    print("Loading students from:", STUDENTS_PATH)
    with open(STUDENTS_PATH, "r", encoding="utf-8") as f:
        students = json.load(f)
    students_df = pd.DataFrame(students)

    # Prepare job features similar to training
    jobs_df["duration_months"] = jobs_df["duration"].apply(parse_duration_to_months)
    jobs_df["job_title_clean"] = jobs_df["job_title"].fillna("").str.lower()
    jobs_df["location_tokens"] = jobs_df["location"].apply(simple_location_tokens)
    jobs_df["domain_auto"] = jobs_df["job_title"].apply(build_domain_from_title)

    text_corpus = (
        jobs_df["job_title"].fillna("") + " " + jobs_df["description"].fillna("")
    ).tolist()
    vectorizer = TfidfVectorizer(max_features=5000)
    job_tfidf = vectorizer.fit_transform(text_corpus)

    # Load trained model
    print("Loading XGBoost model from:", MODEL_PATH)
    model = load_xgb_model(MODEL_PATH)

    # For each student -> print recommendations
    for _, srow in students_df.iterrows():
        sid = srow["student_id"]
        sname = srow["name"]

        print("\n" + "=" * 80)
        print(f"Recommendations for {sname} (student_id={sid})")
        print("=" * 80)
        print()

        rec_df = get_recommendations_for_student_row(
            srow, jobs_df, model, job_tfidf, vectorizer, top_n=10
        )

        if rec_df.empty:
            print("No recommendations found.\n")
            continue

        for idx, row in rec_df.iterrows():
            rank = idx + 1
            score_percent = row["match_score"] * 100

            loc_place, _ = split_location_mode(row["location"])

            print(f"{rank}) {row['job_title']}")
            print(f"    Company  : {row['company_name']}")
            print(f"    Location : {loc_place}")
            print(f"    Mode     : {row['wfh']}")
            print(f"    Duration : {row['duration']}")
            print(f"    Score    : {score_percent:.2f}%")
            print(f"    Link     : {row['job_link']}")
            print()


if __name__ == "__main__":
    main()
