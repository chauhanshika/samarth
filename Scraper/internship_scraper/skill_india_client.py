from typing import List, Dict, Any

import requests

from .config import SKILL_INDIA_URL, HEADERS
from .models import base_record


def fetch_skill_india_programs(page_number: int = 1, page_size: int = 10000) -> Dict[str, Any]:
    payload = {
        "PageNumber": page_number,
        "PageSize": page_size,
    }

    headers = HEADERS.copy()
    headers["Content-Type"] = "application/json"
    headers["Accept"] = "application/json"

    resp = requests.post(SKILL_INDIA_URL, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def parse_skill_india_programs(api_json: Dict[str, Any]) -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []

    data = api_json.get("Data") or {}
    programs = data.get("UserProgramDetailsDTOS") or []

    for p in programs:
        rec = base_record()
        rec["source"] = "Skill India Internship"

        rec["job_title"] = str(p.get("Name") or "").strip()
        rec["company_name"] = str(p.get("ProviderName") or "").strip()
        rec["duration"] = str(p.get("Duration") or "").strip()
        rec["sector"] = str(p.get("Sector") or "").strip()
        rec["description"] = str(p.get("Description") or "").strip()

        price = p.get("Price")
        rec["price"] = "" if price is None else str(price)

        rec["fee_type"] = str(p.get("FeeType") or "").strip()
        rec["mode"] = str(p.get("Mode") or "").strip()

        stipend_bool = p.get("Stipend")
        if stipend_bool is True:
            rec["stipend"] = "Yes"
        elif stipend_bool is False:
            rec["stipend"] = "No"
        else:
            rec["stipend"] = ""

        stipend_amount = p.get("StipendAmount")
        rec["stipend_amount"] = "" if stipend_amount is None else str(stipend_amount)

        domain_list = p.get("Domain") or []
        if isinstance(domain_list, list):
            rec["domain"] = ", ".join(str(x) for x in domain_list)
        else:
            rec["domain"] = str(domain_list or "")

        occupation_list = p.get("Occupation") or []
        if isinstance(occupation_list, list):
            rec["occupation"] = ", ".join(str(x) for x in occupation_list)
        else:
            rec["occupation"] = str(occupation_list or "")

        openings = p.get("NumberOfOpenings")
        rec["number_of_openings"] = "" if openings is None else str(openings)

        credits = p.get("CreditsAvailable")
        if credits is True:
            rec["credits_available"] = "Yes"
        elif credits is False:
            rec["credits_available"] = "No"
        else:
            rec["credits_available"] = ""

        results.append(rec)

    return results
