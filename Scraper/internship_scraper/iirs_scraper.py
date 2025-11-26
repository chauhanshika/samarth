from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import urllib3

from .models import base_record

BASE_URL = "https://www.iirs.gov.in"
START_URL = "https://www.iirs.gov.in/content/external-student-internship"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_session = requests.Session()
_session.headers.update(HEADERS)
_session.verify = False


def fetch_iirs_internships() -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []

    try:
        resp = _session.get(START_URL, timeout=25)
        resp.raise_for_status()
    except Exception as e:  
        print(f"[WARN] Error accessing {START_URL}: {e}")
        return results

    _parse_main_page(resp.text, START_URL, results)

    results = _deduplicate_results(results)
    return results




def _parse_main_page(html: str, page_url: str, results: List[Dict[str, str]]) -> None:
    soup = BeautifulSoup(html, "html.parser")

    content = _extract_main_content(soup)
    title = "IIRS External Student Internship / Project / Dissertation"

    data = _parse_details_to_record(content, title, page_url)
    results.append(data)

    keywords = ["intern", "project", "dissertation", "training"]
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        if not text:
            continue
        if any(kw in text.lower() for kw in keywords):
            href = a["href"]
            full_url = _build_full_url(href)
            if full_url != page_url:
                detail = _fetch_detail(full_url, text)
                if detail:
                    results.append(detail)


def _build_full_url(href: str) -> str:
    if href.startswith("http"):
        return href
    elif href.startswith("/"):
        return BASE_URL + href
    else:
        return f"{BASE_URL}/{href}"


def _fetch_detail(url: str, title: str) -> Optional[Dict[str, str]]:
    try:
        resp = _session.get(url, timeout=25)
        resp.raise_for_status()
    except Exception as e: 
        print(f"[WARN] Error fetching {url}: {e}")
        return None
    soup = BeautifulSoup(resp.text, "html.parser")
    content = _extract_main_content(soup)
    return _parse_details_to_record(content, title, url)


def _extract_main_content(soup: BeautifulSoup) -> str:
    selectors = ["main", "article", ".content", ".main-content", "#content", ".page-content", ".container"]
    main = None
    for s in selectors:
        main = soup.select_one(s)
        if main:
            break
    if not main:
        main = soup.find("body")
    if main:
        for tag in main.find_all(["nav", "footer", "aside", "header"]):
            tag.decompose()
        return main.get_text(" ", strip=True)
    return soup.get_text(" ", strip=True)


def _parse_details_to_record(text: str, title: str, url: str) -> Dict[str, str]:
    rec = base_record()
    rec["source"] = "IIRS Internship"

    rec["job_title"] = title
    rec["company_name"] = "ISRO - Indian Institute of Remote Sensing (IIRS)"

    rec["description"] = text[:1800] if len(text) > 1800 else text

    rec["job_link"] = url
    rec["location"] = "Dehradun"

    apply_by = _extract_deadline(text)
    if apply_by:
        rec["apply_by"] = apply_by

    duration = _extract_duration(text)
    if duration:
        rec["duration"] = duration

    stipend = _extract_stipend(text)
    if stipend:
        rec["stipend"] = stipend

    rec["sector"] = "Space / Remote Sensing / Geoinformatics"

    skills = _extract_skills(text)
    if skills:
        rec["domain"] = ", ".join(skills)

    opp_type = _determine_type(title, text)
    if opp_type:
        rec["occupation"] = opp_type


    return rec


def _extract_duration(text: str) -> Optional[str]:
    patterns = [
        r"(\d+)\s*(?:months?|month|weeks?|week)",
        r"duration[:\s]*(\d+\s*(?:months?|weeks?))",
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(0)
    return None


def _extract_stipend(text: str) -> Optional[str]:
    tl = text.lower()
    if any(w in tl for w in ["no stipend", "unpaid", "without stipend"]):
        return "Unpaid / No stipend"
    patterns = [
        r"stipend[:\s]*[₹Rs\.\s]*([\d,]+)",
        r"[₹Rs\.\s]([\d,]+)\s*(?:per month|/month)",
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(0)
    return None


def _extract_deadline(text: str) -> Optional[str]:
    patterns = [
        r"(?:last date|apply by|deadline)[:\s]*([\d]{1,2}[\-/\.][\d]{1,2}[\-/\.][\d]{2,4})",
        r"(?:last date|apply by|deadline)[:\s]*([\d]{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+[\d]{4})",
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1)
    return None


def _extract_skills(text: str) -> List[str]:
    keywords = [
        "remote sensing",
        "gis",
        "geoinformatics",
        "image processing",
        "python",
        "machine learning",
        "satellite",
        "spatial",
        "cartography",
    ]
    found: List[str] = []
    tl = text.lower()
    for k in keywords:
        if k in tl:
            found.append(k.title())
    return found


def _determine_type(title: str, content: str) -> str:
    tl = title.lower()
    cl = content.lower()
    if "dissertation" in tl or "dissertation" in cl:
        return "Dissertation / Thesis"
    if "project" in tl or "project" in cl:
        return "Project Work"
    if "intern" in tl or "internship" in cl:
        return "Internship"
    return "IIRS Opportunity"


def _deduplicate_results(results: List[Dict[str, str]]) -> List[Dict[str, str]]:
    seen = set()
    uniq: List[Dict[str, str]] = []
    for r in results:
        url = r.get("job_link")
        if url and url not in seen:
            seen.add(url)
            uniq.append(r)
    return uniq
