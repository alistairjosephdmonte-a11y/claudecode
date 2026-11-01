"""Download the primary sources (SEC EDGAR filings and the SoftBank Group press release) into evidence/sec_filings/.
    python3 scripts/fetch_sources.py
SEC asks automated clients to identify themselves: set SEC_USER_AGENT="Name email" before running."""
import os
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "evidence", "sec_filings")
EDGAR = "https://www.sec.gov/Archives/edgar/data/"
SOURCES = {
    "S1_20190814.htm": EDGAR + "1533523/000119312519220499/d781982ds1.htm",
    "S1A_20190904.htm": EDGAR + "1533523/000119312519236798/d781982ds1a.htm",
    "S1A_20190913.htm": EDGAR + "1533523/000119312519244329/d804478ds1a.htm",
    "RW_20190930.htm": EDGAR + "1533523/000119312519258913/d808793drw.htm",
    "BOWX_ex991.htm": EDGAR + "1813756/000119312521095508/d29340dex991.htm",
    "8K_20211026_close.htm": EDGAR + "1813756/000119312521308162/d188107d8k.htm",
    "10K_2022.htm": EDGAR + "1813756/000181375623000016/we-20221231.htm",
    "10Q_20230808.htm": EDGAR + "1813756/000181375623000059/we-20230630.htm",
    "8K_20231107_ch11.htm": EDGAR + "1813756/000119312523271902/d522028d8k.htm",
    "EX991_2023Q3.htm": EDGAR + "1813756/000181375623000067/wework2023q310q.htm",
    "8K_20240612_emerge.htm": EDGAR + "1813756/000119312524159419/d803133d8k.htm",
    "SB_20191023.htm": "https://group.softbank/en/news/press/20191023",
}

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    ua = os.environ.get("SEC_USER_AGENT", "BrandCoroner research contact@example.com")
    for name, url in SOURCES.items():
        path = os.path.join(OUT, name)
        if os.path.exists(path):
            continue
        req = urllib.request.Request(url, headers={"User-Agent": ua})
        with urllib.request.urlopen(req) as r, open(path, "wb") as fh:
            fh.write(r.read())
        print("fetched", name)
        time.sleep(0.3)
