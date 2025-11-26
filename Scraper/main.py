import json
from pathlib import Path

from internship_scraper.aggregator import aggregate_internships


def main() -> None:
    records = aggregate_internships()
    out_path = Path("jobs.json")
    out_path.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✔ jobs.json generated with {len(records)} records (each with job_id).")


if __name__ == "__main__":
    main()
