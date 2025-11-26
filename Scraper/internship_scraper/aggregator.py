from typing import List, Dict

from .aicte_scraper import fetch_aicte_html, parse_aicte_internships
from .skill_india_client import fetch_skill_india_programs, parse_skill_india_programs
from .iirs_scraper import fetch_iirs_internships


def aggregate_internships() -> List[Dict[str, str]]:
    all_records: List[Dict[str, str]] = []

    # --- AICTE ---
    try:
        aicte_html = fetch_aicte_html()
        aicte_records = parse_aicte_internships(aicte_html)
        all_records.extend(aicte_records)
    except Exception as e:  
        print(f"[WARN] Failed to fetch/parse AICTE internships: {e}")

    # --- Skill India ---
    try:
        skill_json = fetch_skill_india_programs(1, 10000)
        skill_records = parse_skill_india_programs(skill_json)
        all_records.extend(skill_records)
    except Exception as e: 
        print(f"[WARN] Failed to fetch/parse Skill India internships: {e}")

    # --- IIRS (ISRO) ---
    try:
        iirs_records = fetch_iirs_internships()
        all_records.extend(iirs_records)
    except Exception as e:  
        print(f"[WARN] Failed to fetch/parse IIRS internships: {e}")

    for idx, rec in enumerate(all_records, start=1):
        rec["job_id"] = idx

    return all_records
