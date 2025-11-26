from typing import List, Dict

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from .config import AICTE_LIST_URL, AICTE_DETAIL_BASE, HEADERS
from .models import base_record


def fetch_aicte_html() -> str:
    resp = requests.get(AICTE_LIST_URL, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.text


def parse_aicte_internships(html: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    results: List[Dict[str, str]] = []

    for card in soup.select("div.internships-list div.card.internship-item"):
        primary = card.select_one(".internship-primary-info")

        rec = base_record()
        rec["source"] = "AICTE Internship"

        if primary:
            job_title_el = primary.select_one("h3.job-title")
            if job_title_el:
                rec["job_title"] = job_title_el.get_text(strip=True)

            company_el = primary.select_one("h5.company-name")
            if company_el:
                rec["company_name"] = company_el.get_text(strip=True)

            attr = primary.select_one("ul.job-attributes")
            if attr:
                wfh_el = attr.select_one("li.wfh span")
                posted_el = attr.select_one("li.posted-on span")
                location_el = attr.select_one("li.location span")

                if wfh_el:
                    rec["wfh"] = wfh_el.get_text(strip=True)
                if posted_el:
                    rec["posted_on"] = posted_el.get_text(strip=True)
                if location_el:
                    rec["location"] = location_el.get_text(strip=True)

        supp = card.select_one("ul.job-supplement-attributes")
        if supp:
            start_el = supp.select_one("li.start-date span")
            duration_el = supp.select_one("li.duration span")
            apply_el = supp.select_one("li.apply-by span")

            if start_el:
                rec["start_date"] = start_el.get_text(strip=True)
            if duration_el:
                rec["duration"] = duration_el.get_text(strip=True)
            if apply_el:
                rec["apply_by"] = apply_el.get_text(strip=True)

        link_el = card.select_one(".btn-wrap a.btn.btn-primary")
        if link_el and link_el.has_attr("href"):
            rec["job_link"] = urljoin(AICTE_DETAIL_BASE, link_el["href"])

        results.append(rec)

    return results
