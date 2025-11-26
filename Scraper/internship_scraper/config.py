from typing import Dict


AICTE_LIST_URL: str = "https://internship.aicte-india.org/fetch_city.php?city="
AICTE_DETAIL_BASE: str = "https://internship.aicte-india.org/"

SKILL_INDIA_URL: str = "https://api-fe.skillindiadigital.gov.in/api/internship/get-programs"

HEADERS: Dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (compatible; ShivamtrixScraper/4.32; +https://local.itshivam.in)",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Site": "cross-site",
    "Accept": "*/*",
    "Content-Type": "application/json",
    "Sec-Ch-Ua": '"Not.A/Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"macOS"',
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}
