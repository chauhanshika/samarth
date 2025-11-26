import os
import json
from datetime import datetime, timezone

import pandas as pd

from train_xgb_model import (
    JOBS_PATH,
    STUDENTS_PATH,
)

DATA_DIR = "data"
INTERESTS_CSV = os.path.join(DATA_DIR, "interests.csv")
ALLOCATION_CSV = os.path.join(DATA_DIR, "allocation_results.csv")

os.makedirs(DATA_DIR, exist_ok=True)


# -------------------------------------------------
# 1. "I'm Interested" API-like function
# -------------------------------------------------
def save_student_interest(student_id: int, student_name: str, job_id: int, match_score: float):
    """
    Is function ko frontend ke 'I'm Interested' button se call karoge.

    Example:
        save_student_interest(1, "Mazhar Akhtar", 116, 0.9988)
    """
    now = datetime.now(timezone.utc).isoformat()

    new_row = {
        "student_id": student_id,
        "student_name": student_name,
        "job_id": job_id,
        "match_score": match_score,
        "applied_at": now,
    }

    if os.path.exists(INTERESTS_CSV):
        df = pd.read_csv(INTERESTS_CSV)
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    else:
        df = pd.DataFrame([new_row])

    df.to_csv(INTERESTS_CSV, index=False)
    print(f"Saved interest: {new_row}")


# -------------------------------------------------
# 2. Pretty print allocation
# -------------------------------------------------
def print_allocation_pretty(allocation_df: pd.DataFrame):
    print("\n" + "=" * 80)
    print("Allocation Results")
    print("=" * 80)

    if allocation_df.empty:
        print("No allocations could be made (no interests or no matching data).\n")
        return

    # Sort for nicer grouping
    allocation_df = allocation_df.sort_values(
        by=["job_id", "match_score"], ascending=[True, False]
    )

    for job_id, group in allocation_df.groupby("job_id"):
        job_title = group["job_title"].iloc[0]
        company_name = group["company_name"].iloc[0]
        location = group["location"].iloc[0]
        wfh = group["wfh"].iloc[0]
        duration = group["duration"].iloc[0]
        capacity = int(group["capacity"].iloc[0])

        print("\n" + "-" * 80)
        print(f"[JOB {job_id}]")
        print(f"Internship : {job_title}")
        print(f"Company    : {company_name}")
        print(f"Location   : {location}")
        print(f"Mode       : {wfh}")
        print(f"Duration   : {duration}")
        print(f"Capacity   : {capacity}")
        print("\n→ Allocated Students:")

        for idx, row in enumerate(group.itertuples(index=False), start=1):
            score_percent = row.match_score * 100
            applied_str = ""
            if pd.notna(row.applied_at):
                applied_str = str(row.applied_at).replace("T", " ")

            print(f"    {idx}) {row.student_name} (ID={row.student_id})")
            print(f"       CGPA      : {row.student_cgpa}")
            print(f"       Year      : {row.year_of_study}")
            print(f"       Exp Level : {row.exp_level_num}  (0=Fresher,1=1 intern,2=2+)")
            print(f"       Relevant? : {row.rel_exp_flag}")
            print(f"       Match     : {score_percent:.2f}%")
            print(f"       Applied at: {applied_str}")
        print()


# -------------------------------------------------
# 3. Allocation Engine (capacity + tie-break)
# -------------------------------------------------
def run_allocation(default_capacity: int = 1):
    """
    Har internship ke liye best students allocate karega based on:

    1) match_score       (XGBoost recommendation score)
    2) rel_exp_flag      (relevant experience)
    3) exp_level_num     (more internships)
    4) cgpa
    5) year_of_study
    6) applied_at        (pehle apply karne wala thoda priority)

    Result -> data/allocation_results.csv
    """

    if not os.path.exists(INTERESTS_CSV):
        print("No interests file found. Run save_student_interest first.")
        return

    print("Loading interests from:", INTERESTS_CSV)
    interests_df = pd.read_csv(INTERESTS_CSV)

    print("Loading students from:", STUDENTS_PATH)
    with open(STUDENTS_PATH, "r", encoding="utf-8") as f:
        students = json.load(f)
    students_df = pd.DataFrame(students)

    print("Loading internships from:", JOBS_PATH)
    jobs_df = pd.read_json(JOBS_PATH)

    # Normalize job_id type
    jobs_df["job_id"] = pd.to_numeric(jobs_df["job_id"], errors="coerce")
    interests_df["job_id"] = pd.to_numeric(interests_df["job_id"], errors="coerce")

    # Capacity handling
    if "capacity" not in jobs_df.columns:
        jobs_df["capacity"] = default_capacity
    else:
        jobs_df["capacity"] = jobs_df["capacity"].fillna(default_capacity)
        jobs_df.loc[jobs_df["capacity"] <= 0, "capacity"] = default_capacity

    # Merge interests with student details (including experience flags)
    merged = interests_df.merge(
        students_df[
            [
                "student_id",
                "cgpa",
                "year_of_study",
                "has_internship_experience",
                "experience_level",
                "has_relevant_experience",
            ]
        ],
        on="student_id",
        how="left",
    )

    # Merge job details
    merged = merged.merge(
        jobs_df[
            [
                "job_id",
                "job_title",
                "company_name",
                "location",
                "wfh",
                "duration",
                "capacity",
            ]
        ],
        on="job_id",
        how="left",
    )

    merged = merged.dropna(subset=["job_id"])
    merged["applied_at"] = pd.to_datetime(merged["applied_at"], errors="coerce")

    allocation_rows = []

    for job_id, group in merged.groupby("job_id"):
        job_title = group["job_title"].iloc[0]
        company_name = group["company_name"].iloc[0]
        location = group["location"].iloc[0]
        wfh = group["wfh"].iloc[0]
        duration = group["duration"].iloc[0]
        capacity = int(group["capacity"].iloc[0])

        # Experience numeric encoding
        exp_map = {"fresher": 0, "1 internship": 1, "2+ internships": 2}

        group = group.copy()
        group["exp_level_num"] = (
            group["experience_level"]
            .fillna("Fresher")
            .str.strip()
            .str.lower()
            .map(exp_map)
            .fillna(0)
        )

        group["rel_exp_flag"] = (
            group["has_relevant_experience"]
            .fillna("No")
            .str.strip()
            .str.lower()
            .eq("yes")
            .astype(int)
        )

        group["has_exp_flag"] = (
            group["has_internship_experience"]
            .fillna("No")
            .str.strip()
            .str.lower()
            .eq("yes")
            .astype(int)
        )

        # Tie-breaker sorting
        group_sorted = group.sort_values(
            by=[
                "match_score",      # 1) model score
                "rel_exp_flag",     # 2) relevant experience
                "exp_level_num",    # 3) more internships
                "cgpa",             # 4) higher cgpa
                "year_of_study",    # 5) seniority
                "applied_at",       # 6) earlier applied
            ],
            ascending=[False, False, False, False, False, True],
        )

        selected = group_sorted.head(capacity)

        for _, row in selected.iterrows():
            allocation_rows.append(
                {
                    "job_id": job_id,
                    "job_title": job_title,
                    "company_name": company_name,
                    "location": location,
                    "wfh": wfh,
                    "duration": duration,
                    "capacity": capacity,
                    "student_id": row["student_id"],
                    "student_name": row["student_name"],
                    "student_cgpa": row["cgpa"],
                    "year_of_study": row["year_of_study"],
                    "match_score": row["match_score"],
                    "applied_at": row["applied_at"],
                    "exp_level_num": row["exp_level_num"],
                    "rel_exp_flag": row["rel_exp_flag"],
                    "has_exp_flag": row["has_exp_flag"],
                }
            )

    allocation_df = pd.DataFrame(allocation_rows)

    if allocation_df.empty:
        print("No allocations could be made (no interests?).")
    else:
        allocation_df.to_csv(ALLOCATION_CSV, index=False)
        print("Saved allocation results to:", ALLOCATION_CSV)
        print_allocation_pretty(allocation_df)


if __name__ == "__main__":
    # Example only:
    save_student_interest(1, "Mazhar Akhtar", 116, 0.9988)
    run_allocation(default_capacity=1)
