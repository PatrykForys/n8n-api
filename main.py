from fastapi import FastAPI, HTTPException
import requests
from bs4 import BeautifulSoup
import re


app = FastAPI()

def scrape(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    with requests.Session() as session:
        session.max_redirects = 5
        response = session.get(url, headers=headers, timeout=(5, 15))
        
        # Jeśli dostajemy 403, spróbuj z innymi nagłówkami
        if response.status_code == 403:
            # Spróbuj z uproszczonymi nagłówkami
            simple_headers = {
                "User-Agent": "Mozilla/5.0 (compatible; Bot)"
            }
            response = session.get(url, headers=simple_headers, timeout=(5, 15))
        
        response.raise_for_status()
        return response.text


def extract_titles_and_dates_in_container(html: str):
    soup = BeautifulSoup(html, "html.parser")

    results = []
    containers = soup.select("div.container")

    for container in containers:
        items = container.select("div.newsContainer") or container.select("div.news")
        for item in items:
            h2 = item.find("h2")
            if not h2:
                continue
            title = h2.get_text(strip=True)

            h3 = item.find("h3")
            date_str = None
            if h3:
                text = h3.get_text(" ", strip=True)
                m = re.search(r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}", text)
                if m:
                    date_str = m.group(0)

            results.append({"title": title, "date": date_str})

    return results


def extract_teacher_names(html: str):
    soup = BeautifulSoup(html, "html.parser")

    names = []
    containers = soup.select("div.container")
    for container in containers:
        for card in container.select("div.miniatureContainer"):
            personal = card.select_one(".personalInfo")
            name = None
            if personal:
                name = personal.get_text(" ", strip=True)
            else:
                img = card.select_one(".photoContainer img[alt]")
                if img and img.get("alt"):
                    name = img.get("alt").strip()

            if name:
                name = re.sub(r"\s+", " ", name)
                names.append(name)

    seen = set()
    deduped = []
    for n in names:
        if n not in seen:
            seen.add(n)
            deduped.append(n)
    return deduped

@app.get("/akutalnosci")
def read_root():
    try:
        html = scrape("http://www.zsz2.ostrzeszow.pl/news_all")
    except requests.Timeout:
        raise HTTPException(status_code=504, detail="Upstream timeout while fetching source page")
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Upstream request error: {e.__class__.__name__}")

    news = extract_titles_and_dates_in_container(html)
    return {"news": news}


@app.get("/nauczyciele")
def nauczyciele(url: str = "http://www.zsz2.ostrzeszow.pl/grono_pedagogiczne"):
    try:
        html = scrape(url)
    except requests.Timeout:
        raise HTTPException(status_code=504, detail="Upstream timeout while fetching source page")
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Upstream request error: {e.__class__.__name__}")

    teachers = extract_teacher_names(html)
    return {"teachers": teachers}
